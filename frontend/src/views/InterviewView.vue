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

// Setup form
const selectedTopic = ref(null);
const selectedDifficulty = ref('medium');

// Per-question answers
const voiceAnswer = ref('');
const codeAnswer = ref('');
const selectedLanguage = ref('python');
const submitting = ref(false);

const currentQuestion = computed(() => {
  // If ghost session is active, currentQuestion comes from ghostSession's next_question
  if (ghostSessionActive.value && ghostSession.value && ghostSession.value.next_question) {
    return ghostSession.value.next_question;
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
      const parsedCode = JSON.parse(currentQuestion.value.starting_code);
      if (parsedCode[newLang]) {
        codeAnswer.value = parsedCode[newLang];
      }
    } catch (e) {
      // If it's not JSON (old format), just leave the current code or fallback
    }
  }
});

const isLastQuestion = computed(() => currentIdx.value >= questions.value.length - 1);
const progress = computed(() => {
  if (!questions.value.length) return 0;
  const answered = questions.value.filter(q => q.evaluation).length;
  return Math.round((answered / questions.value.length) * 100);
});

// Watch currentIdx to auto-play audio for the new question
watch(currentIdx, async () => {
  if (currentQuestion.value) {
    await playQuestionAudio(currentQuestion.value.question_id);
  }
});

// ─── Fetch topics on mount ──────────────────────────────
onMounted(async () => {
  try {
    const res = await api.get('/api/interview/topics');
    topics.value = res.data.topics;
    if (topics.value.length) selectedTopic.value = topics.value[0].topic_id;

    // Fetch profile data for the Ghost Recruiter
    profileData.value = await getProfileData();

  } catch (err) {
    error.value = err.response?.data?.message || 'Failed to load topics or profile data.';
  }
});

// Mock profile data for now
async function getProfileData() {
  // In a real application, this would fetch from /profile endpoint
  // const res = await api.get('/profile');
  // return res.data.profile;
  return {
    "name": "John Doe",
    "email": "john.doe@example.com",
    "skills": ["python", "java", "data structures", "algorithms", "system design"],
    "experience": ["Software Engineer at Google", "Software Engineer at Facebook"],
    "education": ["Stanford University"]
  };
}

// ─── Start session ──────────────────────────────────────
async function startSession() {
  loading.value = true;
  error.value = '';
  try {
    // Initiate Ghost Interview flow
    const res = await api.post('/api/interview/ghost_step', {
      user_answer: '', // Initial call, no answer yet
      current_phase: 'introduction',
      profile_json: JSON.stringify(profileData.value),
      local_context_history: [],
      answered_question_ids: [],
    });
    ghostSessionActive.value = true;
    session.value = res.data; // Store the entire response as ghostSession

    recruiterResponseText.value = res.data.recruiter_response_text;
    if (res.data.audio_url) {
      await playAudioFromUrl(res.data.audio_url);
    }
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

// This function is no longer needed for the Ghost flow, but keep for traditional
async function generateQuestions() {
  loading.value = true;
  try {
    const res = await api.post(`/api/interview/sessions/${session.value.session_id}/questions`, { count: 5 });
    questions.value = res.data.questions;
    currentIdx.value = 0;

    // Set initial code to the starting_code of the first question, if applicable
    resetAnswers();
    if (questions.value[0]?.starting_code) {
      try {
        const parsedCode = JSON.parse(questions.value[0].starting_code);
        codeAnswer.value = parsedCode[selectedLanguage.value] || '';
      } catch (e) {
        codeAnswer.value = questions.value[0].starting_code; // Fallback
      }
    }

    // Auto-play the first question's audio
    if (questions.value.length > 0) {
      await playQuestionAudio(questions.value[0].question_id);
    }
  } catch (err) {
    error.value = err.response?.data?.message || 'Failed to generate questions.';
  } finally {
    loading.value = false;
  }
}

async function playQuestionAudio(questionId) {
  try {
    const response = await api.get(`/api/interview/questions/${questionId}/audio`, {
      responseType: 'blob'
    });

    const audioBlob = new Blob([response.data], { type: 'audio/mpeg' });
    const audioUrl = URL.createObjectURL(audioBlob);

    if (audioPlayer.value) {
      audioPlayer.value.pause();
      audioPlayer.value.src = audioUrl;
      await audioPlayer.value.play();
    }
  } catch (err) {
    console.error('Failed to play question audio:', err);
    // Don't show error to user, just fail gracefully if audio doesn't play
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

  // Add user's answer to local context history
  localContextHistory.value.push({ role: 'user', content: voiceAnswer.value });

  // Update answered questions for the ghost recruiter
  if (currentQuestion.value && currentQuestion.value.id && !answeredQuestionIds.value.includes(currentQuestion.value.id)) {
    answeredQuestionIds.value.push(currentQuestion.value.id);
  }

  try {
    const res = await api.post('/api/interview/ghost_step', {
      user_answer: voiceAnswer.value,
      current_phase: 'questioning', // Or 'evaluation' depending on the logic
      profile_json: JSON.stringify(profileData.value),
      local_context_history: localContextHistory.value,
      answered_question_ids: answeredQuestionIds.value,
    });

    // Update ghost session state
    session.value = res.data; // Overwrite current session with ghost data
    recruiterResponseText.value = res.data.recruiter_response_text;
    if (res.data.audio_url) {
      await playAudioFromUrl(res.data.audio_url);
    }

    // Add recruiter's response to local context history
    localContextHistory.value.push({ role: 'assistant', content: recruiterResponseText.value });

    resetAnswers(); // Clear user's answer input
  } catch (err) {
    error.value = err.response?.data?.message || 'Failed to submit answer to Ghost Recruiter.';
  } finally {
    submitting.value = false;
  }
}

// ─── Navigation ─────────────────────────────────────────
function nextQuestion() {
  if (currentIdx.value < questions.value.length - 1) {
    if (audioPlayer.value) audioPlayer.value.pause();
    currentIdx.value++;
    resetAnswers();
    if (currentQuestion.value?.starting_code) {
      try {
        const parsedCode = JSON.parse(currentQuestion.value.starting_code);
        codeAnswer.value = parsedCode[selectedLanguage.value] || '';
      } catch (e) {
        codeAnswer.value = currentQuestion.value.starting_code;
      }
    }
  }
}

function prevQuestion() {
  if (currentIdx.value > 0) {
    if (audioPlayer.value) audioPlayer.value.pause();
    currentIdx.value--;
    resetAnswers();
    if (currentQuestion.value?.starting_code) {
      try {
        const parsedCode = JSON.parse(currentQuestion.value.starting_code);
        codeAnswer.value = parsedCode[selectedLanguage.value] || '';
      } catch (e) {
        codeAnswer.value = currentQuestion.value.starting_code;
      }
    }
  }
}

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
          <h2 class="section-title">Start a Ghost Interview</h2>
          <p class="section-sub">
            This is a stateless, event-driven interview. The AI will generate questions
            and responses on the fly based on your profile and answers.
          </p>
          <div class="setup-form">
            <!-- Difficulty selection can still be used to inform the initial question type -->
            <div class="form-group">
              <label class="form-label">DIFFICULTY</label>
              <div class="diff-group">
                <button
                  v-for="d in ['easy', 'medium', 'hard']"
                  :key="d"
                  class="diff-btn"
                  :class="{ active: selectedDifficulty === d, [d]: true }"
                  @click="selectedDifficulty = d"
                >{{ d }}</button>
              </div>
            </div>
            <button class="primary-btn" @click="startSession" :disabled="loading">
              {{ loading ? 'STARTING...' : 'START GHOST INTERVIEW' }}
            </button>
          </div>
        </div>
      </template>

      <!-- ─── Active Ghost Interview ──────────────────────────── -->
      <template v-else-if="ghostSessionActive">
        <!-- Recruiter's Response -->
        <div v-if="recruiterResponseText" class="box recruiter-response-box">
          <p class="recruiter-text">{{ recruiterResponseText }}</p>
          <button class="replay-btn" @click="replayAudio" title="Replay Audio">
            🔊
          </button>
        </div>

        <!-- Current Question -->
        <template v-if="currentQuestion">
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
        <template v-else>
          <div class="box status-box">
            <p class="status-text">Interview completed. Thank you!</p>
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