<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import NavBar from '@/components/NavBar.vue';
import CodeEditor from '@/components/CodeEditor.vue';
import VoiceInput from '@/components/VoiceInput.vue';
import api from '@/services/api';

// ─── State ───────────────────────────────────────────────
const topics = ref([]);
const session = ref(null); // This will still be used for the traditional flow if that is kept
const questions = ref([]);
const currentIdx = ref(0);
const loading = ref(false);
const error = ref('');

// Ghost Recruiter specific state
const ghostSessionActive = ref(false);
const recruiterResponseText = ref('');
const profileData = ref({}); // Candidate's profile JSON from DB
const localContextHistory = ref([]); // Stores conversation for LLM context
const answeredQuestionIds = ref([]); // Tracks questions already answered by ghost
const currentPhase = ref('introduction'); // Tracks which phase the interview is in
const lastEvaluation = ref(null); // Stores the evaluation from the last answer
const questionStartTime = ref(null); // Tracks when the current question was presented

// Ghost Timer
const timerSeconds = ref(5400); // 90 minutes
let ghostTimerInterval = null;
const formattedTimer = computed(() => {
  const m = Math.floor(timerSeconds.value / 60);
  const s = timerSeconds.value % 60;
  return `${m}:${s.toString().padStart(2, '0')}`;
});

// Setup form
const selectedTopic = ref(null);
const selectedDifficulty = ref('medium');

// Per-question answers
const voiceAnswer = ref('');
const codeAnswer = ref('');
const selectedLanguage = ref('python');
const submitting = ref(false);

const currentQuestion = computed(() => {
  // If ghost session is active, currentQuestion comes from the session's next_question
  if (ghostSessionActive.value && session.value && session.value.next_question) {
    return session.value.next_question;
  }
  // Otherwise, use the traditional questions array
  return questions.value[currentIdx.value] || null;
});

// Audio playback
const audioPlayer = ref(null);

// Watch for language changes to update the starting code
watch(selectedLanguage, (newLang) => {
  if (currentQuestion.value?.starting_code && currentQuestion.value.question_type === 'coding') {
    try {
      const codeData = typeof currentQuestion.value.starting_code === 'string'
        ? JSON.parse(currentQuestion.value.starting_code)
        : currentQuestion.value.starting_code;
      if (codeData[newLang]) {
        codeAnswer.value = codeData[newLang];
      }
    } catch (e) {
      // If it's not JSON, leave the current code
    }
  }
});

// The questions list is no longer used for Ghost, but we won't delete all state just yet.

// ─── Fetch topics and profile on mount ──────────────────
onMounted(async () => {
  try {
    const res = await api.get('/api/interview/topics');
    topics.value = res.data.topics;
    if (topics.value.length) selectedTopic.value = topics.value[0].topic_id;

    // Fetch REAL profile data from the database
    try {
      const profileRes = await api.get('/profile');
      profileData.value = profileRes.data.profile || profileRes.data || {};
    } catch (profileErr) {
      console.warn('Could not load profile, using empty profile:', profileErr);
      profileData.value = {};
    }

  } catch (err) {
    error.value = err.response?.data?.message || 'Failed to load topics or profile data.';
  }
});

// ─── Start session ──────────────────────────────────────
async function startSession() {
  loading.value = true;
  error.value = '';
  currentPhase.value = 'introduction';

  // Start Ghost Timer
  timerSeconds.value = 5400; // 90 minutes
  if (ghostTimerInterval) clearInterval(ghostTimerInterval);
  ghostTimerInterval = setInterval(() => {
    if (timerSeconds.value > 0) timerSeconds.value--;
  }, 1000);

  try {
    const res = await api.post('/api/interview/ghost_step', {
      user_answer: '',
      current_phase: 'introduction',
      profile_json: JSON.stringify(profileData.value),
      local_context_history: [],
      answered_question_ids: [],
      difficulty: selectedDifficulty.value,
    });
    ghostSessionActive.value = true;
    session.value = res.data;

    recruiterResponseText.value = res.data.recruiter_response_text;
    currentPhase.value = res.data.next_phase || 'resume_drilldown';

    // Add the recruiter's greeting to context
    localContextHistory.value.push({ role: 'assistant', content: recruiterResponseText.value });

    // If the question is a coding question, set the starting code
    if (res.data.next_question?.starting_code && res.data.next_question.question_type === 'coding') {
      const codeData = typeof res.data.next_question.starting_code === 'string'
        ? JSON.parse(res.data.next_question.starting_code)
        : res.data.next_question.starting_code;
      codeAnswer.value = codeData[selectedLanguage.value] || '';
    }

    if (res.data.audio_url) {
      await playAudioFromUrl(res.data.audio_url);
    }
    
    // Set timer for the first question
    questionStartTime.value = Date.now();
  } catch (err) {
    error.value = err.response?.data?.message || 'Failed to start Ghost Interview session.';
  } finally {
    loading.value = false;
  }
}

async function playAudioFromUrl(audioUrl) {
  try {
    if (audioPlayer.value) {
      audioPlayer.value.pause();
      audioPlayer.value.src = audioUrl;
      await audioPlayer.value.play();
    }
  } catch (err) {
    console.error('Failed to play audio from URL:', err);
  }
}

function replayAudio() {
  if (audioPlayer.value && audioPlayer.value.src) {
    audioPlayer.value.play();
  }
}

// ─── Submit answer ──────────────────────────────────────
async function submitAnswer() {
  if (!currentQuestion.value) return;
  submitting.value = true;
  error.value = '';

  // Time taken logic
  let timeStr = "";
  if (questionStartTime.value) {
    const timeTaken = Math.round((Date.now() - questionStartTime.value) / 1000);
    timeStr = `[Time Taken: ${Math.floor(timeTaken/60)}m ${timeTaken%60}s]`;
  }

  // Combine voice + code + time into a single answer payload
  const combinedAnswer = [
    voiceAnswer.value ? `Spoken: ${voiceAnswer.value}` : '',
    codeAnswer.value ? `Code:\n${codeAnswer.value}` : '',
    timeStr
  ].filter(Boolean).join('\n\n');

  // Add user's answer to local context history
  localContextHistory.value.push({ role: 'user', content: combinedAnswer });

  // Track answered question IDs
  if (currentQuestion.value?.id && !answeredQuestionIds.value.includes(currentQuestion.value.id)) {
    answeredQuestionIds.value.push(currentQuestion.value.id);
  }

  try {
    const res = await api.post('/api/interview/ghost_step', {
      user_answer: combinedAnswer,
      current_phase: currentPhase.value,
      profile_json: JSON.stringify(profileData.value),
      local_context_history: localContextHistory.value,
      answered_question_ids: answeredQuestionIds.value,
      difficulty: selectedDifficulty.value,
    });
    // Update ghost session state
    session.value = res.data;
    recruiterResponseText.value = res.data.recruiter_response_text;
    currentPhase.value = res.data.next_phase || 'completed';
    lastEvaluation.value = res.data.evaluation || null;

    // Restart the tracking timer for the next question
    questionStartTime.value = Date.now();

    // Reset inputs for next question
    voiceAnswer.value = '';
    // Add recruiter's response to local context history
    localContextHistory.value.push({ role: 'assistant', content: recruiterResponseText.value });

    // Reset answers and set starting code for next question if coding
    resetAnswers();
    if (res.data.next_question?.starting_code && res.data.next_question.question_type === 'coding') {
      try {
        const codeData = typeof res.data.next_question.starting_code === 'string'
          ? JSON.parse(res.data.next_question.starting_code)
          : res.data.next_question.starting_code;
        codeAnswer.value = codeData[selectedLanguage.value] || '';
      } catch (e) {
        codeAnswer.value = '';
      }
    }

    if (res.data.audio_url) {
      await playAudioFromUrl(res.data.audio_url);
    }
  } catch (err) {
    error.value = err.response?.data?.message || 'Failed to submit answer to Ghost Recruiter.';
  } finally {
    submitting.value = false;
  }
}

// ─── Navigation ─────────────────────────────────────────
function resetAnswers() {
  voiceAnswer.value = '';
  // Don't reset codeAnswer entirely, or it will flash empty.
  // The actual new codeAnswer is set by generateQuestions or nextQuestion/prevQuestion.
  selectedLanguage.value = 'python';
}

function resetSession() {
  if (audioPlayer.value) audioPlayer.value.pause();
  session.value = null; // Traditional session
  questions.value = [];
  currentIdx.value = 0;
  resetAnswers();
  error.value = '';

  // Ghost Recruiter specific resets
  ghostSessionActive.value = false;
  recruiterResponseText.value = '';
  localContextHistory.value = [];
  answeredQuestionIds.value = [];
  currentPhase.value = 'introduction';
  lastEvaluation.value = null;
  codeAnswer.value = '';
  questionStartTime.value = null;

  if (ghostTimerInterval) {
    clearInterval(ghostTimerInterval);
    ghostTimerInterval = null;
  }
  // profileData is not reset as it's fetched on mount and persists
}

function scoreClass(score) {
  if (score >= 75) return 'high';
  if (score >= 45) return 'mid';
  return 'low';
}
</script>

<template>
  <div class="page">
    <NavBar />
    <main class="main">
      <div class="page-header">
        <h1 class="page-title">AI Interview</h1>
        <p class="page-sub">Practice technical & behavioral interviews with AI feedback.</p>
      </div>

      <!-- Audio Element (Hidden) -->
      <audio ref="audioPlayer"></audio>

      <!-- ─── Error ─────────────────────────────────────── -->
      <div v-if="error" class="box status-box error">
        <p class="status-label">ERROR</p>
        <p class="status-text">{{ error }}</p>
        <button class="outline-btn" @click="error = ''">DISMISS</button>
      </div>

      <!-- ─── Setup Panel (no ghost session yet) ──────────────── -->
      <template v-if="!ghostSessionActive">
        <div class="box setup-box">
          <h2 class="section-title">Start AI Interview</h2>
          <p class="section-sub">
            Complete a full, realistic 6-stage interview including Behavioral, System Design, and DSA. The AI will adapt to your responses in real-time.
          </p>
          <div class="setup-form">
            <button class="primary-btn" @click="startSession" :disabled="loading">
              {{ loading ? 'STARTING...' : 'Start Interview' }}
            </button>
          </div>
        </div>
      </template>

      <!-- ─── Active Ghost Interview ──────────────────────────── -->
      <template v-else-if="ghostSessionActive">
        <!-- Timer -->
        <div class="timer-display" style="text-align: right; font-size: 1.2rem; font-weight: bold; margin-bottom: 10px; color: var(--accent);">
          ⏱ Time Remaining: {{ formattedTimer }}
        </div>

        <!-- Phase Indicator -->
        <div class="box phase-indicator">
          <div
            v-for="phase in ['introduction', 'resume_drilldown', 'leetcode', 'system_design', 'behavioral', 'wrapup']"
            :key="phase"
            class="phase-dot"
            :class="{
              active: currentPhase === phase,
              completed: ['introduction', 'resume_drilldown', 'leetcode', 'system_design', 'behavioral', 'wrapup']
                .indexOf(phase) < ['introduction', 'resume_drilldown', 'leetcode', 'system_design', 'behavioral', 'wrapup']
                .indexOf(currentPhase)
            }"
          >
            {{ phase.replace('_', ' ') }}
          </div>
        </div>

        <!-- Last Evaluation (if available) -->
        <div v-if="lastEvaluation" class="box eval-box">
          <div class="eval-header">
            <span class="eval-label">Previous Answer Evaluation</span>
            <span class="eval-score" :class="scoreClass(lastEvaluation.score)">
              {{ lastEvaluation.score }}/100
            </span>
          </div>
          <div class="eval-section">
            <p class="eval-sub">Strengths</p>
            <p class="eval-text">{{ lastEvaluation.strengths }}</p>
          </div>
          <div class="eval-section">
            <p class="eval-sub">Areas for Improvement</p>
            <p class="eval-text">{{ lastEvaluation.improvements }}</p>
          </div>
        </div>

        <!-- Recruiter's Response -->
        <div v-if="recruiterResponseText" class="box recruiter-response-box">
          <p class="recruiter-text">{{ recruiterResponseText }}</p>
          <button class="replay-btn" @click="replayAudio" title="Replay Audio">
            🔊
          </button>
        </div>

        <!-- Current Question -->
        <template v-if="currentQuestion && currentPhase !== 'completed'">
          <div class="box question-box">
            <span class="q-type-badge" :class="currentQuestion.question_type">
              {{ currentQuestion.question_type.replace('_', ' ') }}
            </span>
            <p class="question-text">{{ currentQuestion.question_text }}</p>
          </div>

          <!-- Answer area -->
          <div class="answer-section">
            <h3 class="section-title">Your Answer</h3>

            <!-- Voice input -->
            <VoiceInput v-model="voiceAnswer" />

            <!-- Code editor (for coding questions or optionally any) -->
            <div v-if="currentQuestion.question_type === 'coding'" class="editor-section">
              <CodeEditor v-model="codeAnswer" v-model:language="selectedLanguage" />
            </div>

            <button
              class="primary-btn"
              @click="submitAnswer"
              :disabled="submitting || (!voiceAnswer && !codeAnswer)"
            >
              {{ submitting ? 'SUBMITTING...' : 'SUBMIT ANSWER' }}
            </button>
          </div>
        </template>
        <template v-else-if="currentPhase === 'completed'">
          <div class="box status-box">
            <p class="status-label">INTERVIEW COMPLETE</p>
            <p class="status-text">{{ recruiterResponseText }}</p>
            <button class="primary-btn" @click="resetSession">START NEW INTERVIEW</button>
          </div>
        </template>

        <div class="nav-row">
          <button class="outline-btn" @click="resetSession">END INTERVIEW</button>
        </div>
      </template>
    </main>
  </div>
</template>

<style scoped>
.main {
  max-width: 900px;
  width: 100%;
  margin: 0 auto;
  padding: 28px 28px 60px;
  display: flex;
  flex-direction: column;
  gap: 22px;
}
/* ── Phase Indicator ─────────────────────────────────── */
.phase-indicator {
  display: flex;
  justify-content: space-between;
  padding: 14px 20px;
  gap: 4px;
  overflow-x: auto;
}
.phase-dot {
  font-size: 10px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  padding: 6px 12px;
  border: 2px solid var(--ink);
  background: #f5f5f5;
  opacity: 0.4;
  white-space: nowrap;
  transition: all 0.2s;
}
.phase-dot.active {
  background: #2d8cf0;
  color: #fff;
  opacity: 1;
  box-shadow: 3px 3px 0 var(--ink);
}
.phase-dot.completed {
  background: #22c55e;
  color: #fff;
  opacity: 0.8;
}
/* ── Page Header ──────────────────────────────────────── */
.page-header { margin-bottom: 4px; }
.page-title {
  font-size: 40px;
  font-weight: 900;
  text-transform: uppercase;
  margin-bottom: 6px;
}
.page-sub {
  font-size: 16px;
  font-weight: 600;
  opacity: 0.7;
}
/* ── Status boxes ─────────────────────────────────────── */
.status-box {
  padding: 40px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}
.status-label {
  font-size: 11px;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  opacity: 0.5;
}
.status-text {
  font-size: 16px;
  font-weight: 700;
  max-width: 440px;
}
.status-box.error { border-left: 6px solid #ef4444; }
/* ── Buttons ──────────────────────────────────────────── */
.outline-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--surface);
  border: 2px solid var(--ink);
  box-shadow: 3px 3px 0 var(--ink);
  padding: 10px 18px;
  font-weight: 800;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  cursor: pointer;
  color: var(--ink);
  transition: box-shadow 0.1s, transform 0.1s;
}
.outline-btn:hover  { background: #f5f5f5; }
.outline-btn:active { box-shadow: 1px 1px 0 var(--ink); transform: translate(2px,2px); }
.outline-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.outline-btn.small { padding: 6px 12px; font-size: 10px; }
.primary-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #2d8cf0;
  color: #fff;
  border: 2px solid var(--ink);
  box-shadow: 3px 3px 0 var(--ink);
  padding: 12px 24px;
  font-weight: 800;
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  cursor: pointer;
  transition: box-shadow 0.1s, transform 0.1s;
}
.primary-btn:hover  { background: #1a7ae0; }
.primary-btn:active { box-shadow: 1px 1px 0 var(--ink); transform: translate(2px,2px); }
.primary-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.replay-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
  padding: 4px;
  opacity: 0.7;
  transition: opacity 0.2s;
}
.replay-btn:hover {
  opacity: 1;
}

/* ── Recruiter Response Box ───────────────────────────────── */
.recruiter-response-box {
  padding: 20px 28px;
  background: var(--accent);
  color: #fff;
  border: 2px solid var(--ink);
  box-shadow: 3px 3px 0 var(--ink);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.recruiter-response-box .recruiter-text {
  font-size: 16px;
  font-weight: 600;
  line-height: 1.6;
  margin-right: 15px; /* Space between text and replay button */
}

.recruiter-response-box .replay-btn {
  color: #fff;
}

/* ── Setup Box ────────────────────────────────────────── */
.setup-box { padding: 28px; }
.section-title { margin-bottom: 18px; }
.section-sub {
  font-size: 14px;
  font-weight: 500;
  opacity: 0.8;
  margin-bottom: 20px;
  line-height: 1.5;
}
.setup-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.form-label {
  font-size: 10px;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  opacity: 0.6;
}
.form-select {
  padding: 10px 14px;
  border: 2px solid var(--ink);
  box-shadow: 3px 3px 0 var(--ink);
  font-size: 14px;
  font-weight: 700;
  background: #fff;
  cursor: pointer;
  appearance: auto;
}
.diff-group {
  display: flex;
  gap: 8px;
}
.diff-btn {
  padding: 8px 18px;
  border: 2px solid var(--ink);
  background: #fff;
  font-weight: 800;
  font-size: 12px;
  text-transform: uppercase;
  cursor: pointer;
  transition: all 0.1s;
}
.diff-btn:hover { background: #f5f5f5; }
.diff-btn.active.easy { background: #22c55e; color: #fff; box-shadow: 3px 3px 0 var(--ink); }
.diff-btn.active.medium { background: #f59e0b; color: #fff; box-shadow: 3px 3px 0 var(--ink); }
.diff-btn.active.hard { background: #ef4444; color: #fff; box-shadow: 3px 3px 0 var(--ink); }
/* ── Progress Box ─────────────────────────────────────── */
.progress-box { padding: 18px 22px; }
.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}
.progress-label {
  font-size: 13px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.progress-count {
  font-size: 13px;
  font-weight: 900;
  opacity: 0.6;
}
.progress-track {
  height: 8px;
  background: #e0e0e0;
  border: 2px solid var(--ink);
  margin-bottom: 14px;
}
.progress-fill {
  height: 100%;
  background: #22c55e;
  transition: width 0.3s ease;
}
/* ── Question Box ─────────────────────────────────────── */
.question-box { padding: 24px 28px; }
.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}
.q-type-badge {
  display: inline-block;
  padding: 3px 10px;
  font-size: 10px;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  border: 2px solid var(--ink);
}
.q-type-badge.conceptual { background: #a5b4fc; }
.q-type-badge.coding { background: #34d399; }
.q-type-badge.behavioral { background: #fbbf24; }
.question-text {
  font-size: 17px;
  font-weight: 700;
  line-height: 1.6;
}
/* ── Answer Section ───────────────────────────────────── */
.answer-section {
  display: flex;
  flex-direction: column;
  gap: 18px;
}
.editor-section {
  margin-top: 4px;
}
/* ── Evaluation Box ───────────────────────────────────── */
.eval-box {
  padding: 24px 28px;
  border-left: 6px solid var(--accent);
  background: #f0f7ff;
}
.eval-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.eval-label {
  font-size: 11px;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--accent);
}
.eval-score {
  font-size: 24px;
  font-weight: 900;
  padding: 4px 14px;
  border: 2px solid var(--ink);
  box-shadow: 2px 2px 0 var(--ink);
}
.eval-score.high { background: #22c55e; color: #fff; }
.eval-score.mid { background: #f59e0b; color: #fff; }
.eval-score.low { background: #ef4444; color: #fff; }
.eval-section { margin-bottom: 16px; }
.eval-section:last-child { margin-bottom: 0; }
.eval-sub {
  font-size: 11px;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  opacity: 0.6;
  margin-bottom: 6px;
}
.eval-text {
  font-size: 14px;
  font-weight: 600;
  line-height: 1.6;
}
/* ── Nav Row ──────────────────────────────────────────── */
.nav-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}
/* ── Responsive ───────────────────────────────────────── */
@media (max-width: 640px) {
  .main { padding: 16px; }
  .diff-group { flex-wrap: wrap; }
}
</style>