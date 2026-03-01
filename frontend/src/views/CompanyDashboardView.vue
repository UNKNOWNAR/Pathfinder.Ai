<script setup>
import { reactive, ref, computed } from 'vue';
import NavBar from '@/components/NavBar.vue';
import api from '@/services/api';

const userName = computed(() => localStorage.getItem('username') || 'Company');
const isSubmitting = ref(false);
const message = ref('');
const isError = ref(false);

const jobData = reactive({
  title: '',
  location: '',
  url: '',
  description: ''
});

const submitJob = async () => {
  if (isSubmitting.value) return;
  isSubmitting.value = true;
  message.value = '';
  isError.value = false;

  try {
    await api.post('/company/jobs', jobData);
    message.value = 'Job posted successfully!';
    isError.value = false;

    // Reset form
    jobData.title = '';
    jobData.location = '';
    jobData.url = '';
    jobData.description = '';
  } catch (err) {
    message.value = err.response?.data?.message || 'Failed to post job. Make sure you are an approved company.';
    isError.value = true;
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<template>
  <div class="page">
    <NavBar />

    <main class="main">
      <div class="header-section">
        <h2 class="company-greeting">WELCOME, {{ userName.toUpperCase() }}</h2>
        <p class="company-sub">Post your open roles directly to our student network.</p>
      </div>

      <div class="content-wrapper">
        <div class="form-card box">
          <h3 class="section-title">▤ CREATE NEW JOB POSTING</h3>

          <form @submit.prevent="submitJob" class="job-form">

            <div class="form-group">
              <label>JOB TITLE</label>
              <input type="text" v-model="jobData.title" class="brutal-input" placeholder="e.g. Frontend Developer" required />
            </div>

            <div class="form-row">
              <div class="form-group half">
                <label>LOCATION</label>
                <input type="text" v-model="jobData.location" class="brutal-input" placeholder="e.g. Remote, San Francisco" required />
              </div>

              <div class="form-group half">
                <label>APPLICATION URL</label>
                <input type="url" v-model="jobData.url" class="brutal-input" placeholder="https://..." required />
              </div>
            </div>

            <div class="form-group">
              <label>JOB DESCRIPTION</label>
              <textarea v-model="jobData.description" class="brutal-input brutal-textarea" rows="8" placeholder="Enter full job description, requirements, etc..." required></textarea>
            </div>

            <div class="form-actions">
              <button type="submit" class="primary-btn" :disabled="isSubmitting">
                {{ isSubmitting ? 'POSTING...' : 'POST JOB NOW' }}
              </button>
            </div>

            <!-- Status Message -->
            <div v-if="message" class="status-msg" :class="{ 'error-msg': isError, 'success-msg': !isError }">
              {{ message }}
            </div>

          </form>
        </div>

        <div class="side-panel">
          <div class="info-card box bg-yellow">
            <h4 class="info-title">POSTING GUIDELINES</h4>
            <ul class="guidelines-list">
              <li>Keep titles concise and standard.</li>
              <li>Include salary bands in the description if possible.</li>
              <li>Ensure your application URL is valid and publicly accessible.</li>
              <li>All jobs are instantly visible to our student network once posted.</li>
            </ul>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.main {
  max-width: 1000px;
  width: 100%;
  margin: 0 auto;
  padding: 40px 28px 60px;
  display: flex;
  flex-direction: column;
  gap: 32px;
}
/* ── Header ─────────────────────────────────────────────── */
.header-section {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.company-greeting {
  font-size: 32px;
  font-weight: 900;
  letter-spacing: -1px;
  margin: 0;
}
.company-sub {
  font-size: 16px;
  font-weight: 600;
  opacity: 0.8;
  margin: 0;
}
/* ── Layout ─────────────────────────────────────────────── */
.content-wrapper {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 32px;
  align-items: start;
}
.section-title { margin: 0 0 24px 0; }
/* ── Form ───────────────────────────────────────────────── */
.form-card {
  padding: 32px;
}
.job-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.form-row {
  display: flex;
  gap: 20px;
}
.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.half {
  flex: 1;
}
.form-group label {
  font-size: 13px;
  font-weight: 900;
  letter-spacing: 0.05em;
}
.form-actions {
  margin-top: 8px;
}
.primary-btn { width: 100%; }
/* ── Messages ───────────────────────────────────────────── */
.status-msg { margin-top: 16px; }
/* ── Side Panel ─────────────────────────────────────────── */
.info-card {
  padding: 24px;
}
.bg-yellow {
  background: #ffeaa7;
}
.info-title {
  font-size: 14px;
  font-weight: 900;
  margin: 0 0 16px 0;
  text-transform: uppercase;
  border-bottom: 2px solid var(--ink);
  padding-bottom: 8px;
}
.guidelines-list {
  margin: 0;
  padding-left: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  font-size: 14px;
  font-weight: 600;
  line-height: 1.4;
}
/* ── Responsive ─────────────────────────────────────────── */
@media (max-width: 860px) {
  .content-wrapper { grid-template-columns: 1fr; }
.form-row { flex-direction: column; gap: 20px; }
.side-panel { order: -1; }
}
</style>