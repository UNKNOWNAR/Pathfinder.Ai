<script setup>
import { ref, computed, onMounted } from 'vue';
import NavBar from '@/components/NavBar.vue';
import CodeEditor from '@/components/CodeEditor.vue';
import VoiceInput from '@/components/VoiceInput.vue';
import api from '@/services/api';

// ─── State ───────────────────────────────────────────────
const topics = ref([]);
const session = ref(null);
const questions = ref([]);
const currentIdx = ref(0);
const loading = ref(false);
const error = ref('');

// Setup form
const selectedTopic = ref(null);
const selectedDifficulty = ref('medium');

// Per-question answers
const voiceAnswer = ref('');
const codeAnswer = ref('');
const submitting = ref(false);

const currentQuestion = computed(() => questions.value[currentIdx.value] || null);
const isLastQuestion = computed(() => currentIdx.value >= questions.value.length - 1);
const progress = computed(() => {
  if (!questions.value.length) return 0;
  const answered = questions.value.filter(q => q.evaluation).length;
  return Math.round((answered / questions.value.length) * 100);
});

// ─── Fetch topics on mount ──────────────────────────────
onMounted(async () => {
  try {
    const res = await api.get('/api/interview/topics');
    topics.value = res.data.topics;
    if (topics.value.length) selectedTopic.value = topics.value[0].topic_id;
  } catch (err) {
    error.value = err.response?.data?.message || 'Failed to load topics.';
  }
});

// ─── Start session ──────────────────────────────────────
async function startSession() {
  loading.value = true;
  error.value = '';
  try {
    const res = await api.post('/api/interview/sessions', {
      topic_id: selectedTopic.value,
      difficulty: selectedDifficulty.value,
    });
    session.value = res.data.session;
    await generateQuestions();
  } catch (err) {
    error.value = err.response?.data?.message || 'Failed to start session.';
  } finally {
    loading.value = false;
  }
}

async function generateQuestions() {
  loading.value = true;
  try {
    const res = await api.post(`/api/interview/sessions/${session.value.session_id}/questions`);
    questions.value = res.data.questions;
    currentIdx.value = 0;
    resetAnswers();
  } catch (err) {
    error.value = err.response?.data?.message || 'Failed to generate questions.';
  } finally {
    loading.value = false;
  }
}

// ─── Submit answer ──────────────────────────────────────
async function submitAnswer() {
  if (!currentQuestion.value) return;
  submitting.value = true;
  error.value = '';
  try {
    const res = await api.post(`/api/interview/questions/${currentQuestion.value.question_id}/answer`, {
      voice_answer: voiceAnswer.value,
      code_answer: codeAnswer.value,
    });
    // Update the question in our local array with the evaluation
    questions.value[currentIdx.value] = {
      ...questions.value[currentIdx.value],
      evaluation: res.data.evaluation,
    };
  } catch (err) {
    error.value = err.response?.data?.message || 'Failed to submit answer.';
  } finally {
    submitting.value = false;
  }
}

// ─── Navigation ─────────────────────────────────────────
function nextQuestion() {
  if (currentIdx.value < questions.value.length - 1) {
    currentIdx.value++;
    resetAnswers();
  }
}

function prevQuestion() {
  if (currentIdx.value > 0) {
    currentIdx.value--;
    resetAnswers();
  }
}

function resetAnswers() {
  voiceAnswer.value = '';
  codeAnswer.value = '';
}

function resetSession() {
  session.value = null;
  questions.value = [];
  currentIdx.value = 0;
  resetAnswers();
  error.value = '';
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

      <!-- ─── Error ─────────────────────────────────────── -->
      <div v-if="error" class="box status-box error">
        <p class="status-label">ERROR</p>
        <p class="status-text">{{ error }}</p>
        <button class="outline-btn" @click="error = ''">DISMISS</button>
      </div>

      <!-- ─── Setup Panel (no session yet) ──────────────── -->
      <template v-if="!session">
        <div class="box setup-box">
          <h2 class="section-title">Start an Interview</h2>
          <div class="setup-form">
            <div class="form-group">
              <label class="form-label">TOPIC</label>
              <select v-model="selectedTopic" class="form-select">
                <option v-for="t in topics" :key="t.topic_id" :value="t.topic_id">
                  {{ t.name }}
                </option>
              </select>
            </div>
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
            <button class="primary-btn" @click="startSession" :disabled="loading || !selectedTopic">
              {{ loading ? 'STARTING...' : 'START INTERVIEW' }}
            </button>
          </div>
        </div>
      </template>

      <!-- ─── Active Interview ──────────────────────────── -->
      <template v-else>
        <!-- Progress bar -->
        <div class="box progress-box">
          <div class="progress-header">
            <span class="progress-label">{{ session.topic?.name || 'Interview' }} &mdash; {{ session.difficulty.toUpperCase() }}</span>
            <span class="progress-count">{{ currentIdx + 1 }} / {{ questions.length }}</span>
          </div>
          <div class="progress-track">
            <div class="progress-fill" :style="{ width: progress + '%' }"></div>
          </div>
          <button class="outline-btn small" @click="resetSession">NEW SESSION</button>
        </div>

        <!-- Loading questions -->
        <div v-if="loading" class="box status-box">
          <p class="status-text">Generating questions...</p>
        </div>

        <!-- Question Card -->
        <template v-else-if="currentQuestion">
          <div class="box question-box">
            <span class="q-type-badge" :class="currentQuestion.question_type">
              {{ currentQuestion.question_type }}
            </span>
            <p class="question-text">{{ currentQuestion.question_text }}</p>
          </div>

          <!-- Answer area (only if not yet evaluated) -->
          <template v-if="!currentQuestion.evaluation">
            <div class="answer-section">
              <h3 class="section-title">Your Answer</h3>

              <!-- Voice input -->
              <VoiceInput v-model="voiceAnswer" />

              <!-- Code editor (for coding questions or optionally any) -->
              <div v-if="currentQuestion.question_type === 'coding'" class="editor-section">
                <CodeEditor v-model="codeAnswer" language="python" />
              </div>

              <button
                class="primary-btn"
                @click="submitAnswer"
                :disabled="submitting || (!voiceAnswer && !codeAnswer)"
              >
                {{ submitting ? 'EVALUATING...' : 'SUBMIT ANSWER' }}
              </button>
            </div>
          </template>

          <!-- Evaluation result -->
          <template v-else>
            <div class="box eval-box">
              <div class="eval-header">
                <span class="eval-label">AI EVALUATION</span>
                <span class="eval-score" :class="scoreClass(currentQuestion.evaluation.score)">
                  {{ currentQuestion.evaluation.score }} / 100
                </span>
              </div>

              <div class="eval-section">
                <h4 class="eval-sub">Strengths</h4>
                <p class="eval-text">{{ currentQuestion.evaluation.strengths }}</p>
              </div>
              <div class="eval-section">
                <h4 class="eval-sub">Areas to Improve</h4>
                <p class="eval-text">{{ currentQuestion.evaluation.improvements }}</p>
              </div>
              <div class="eval-section">
                <h4 class="eval-sub">Ideal Answer</h4>
                <p class="eval-text">{{ currentQuestion.evaluation.ideal_answer }}</p>
              </div>
            </div>
          </template>

          <!-- Navigation -->
          <div class="nav-row">
            <button class="outline-btn" @click="prevQuestion" :disabled="currentIdx === 0">PREV</button>
            <button
              v-if="!isLastQuestion"
              class="outline-btn"
              @click="nextQuestion"
            >NEXT</button>
            <button
              v-else
              class="primary-btn"
              @click="resetSession"
            >FINISH</button>
          </div>
        </template>
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
/* ── Setup Box ────────────────────────────────────────── */
.setup-box { padding: 28px; }
.section-title { margin-bottom: 18px; }
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
.q-type-badge {
  display: inline-block;
  padding: 3px 10px;
  font-size: 10px;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  border: 2px solid var(--ink);
  margin-bottom: 14px;
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
