<script setup>
import { ref, onMounted, watch } from 'vue';
import NavBar from '@/components/NavBar.vue';
import api from '@/services/api';

const jobs      = ref([]);
const total     = ref(0);
const pages     = ref(1);
const page      = ref(1);
const search    = ref('');
const loading   = ref(false);
const error     = ref('');

const fetchJobs = async () => {
  loading.value = true;
  error.value   = '';
  try {
    const res = await api.get('/admin/jobs', {
      params: { page: page.value, per_page: 20, q: search.value }
    });
    jobs.value  = res.data.jobs;
    total.value = res.data.total;
    pages.value = res.data.pages;
  } catch {
    error.value = 'Failed to load jobs from database.';
  } finally {
    loading.value = false;
  }
};

// Debounce search input — wait 400ms after user stops typing
let debounceTimer = null;
watch(search, () => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    page.value = 1;
    fetchJobs();
  }, 400);
});

const prevPage = () => { if (page.value > 1) { page.value--; fetchJobs(); } };
const nextPage = () => { if (page.value < pages.value) { page.value++; fetchJobs(); } };

const deleteJob = async (jobId) => {
  if (!confirm('Are you sure you want to delete this job? This action cannot be undone.')) return;

  try {
    await api.delete(`/admin/jobs/${jobId}`);
    // Remove from local list
    jobs.value = jobs.value.filter(j => j.job_id !== jobId);
    total.value--;
  } catch (err) {
    alert('Failed to delete job.');
    console.error(err);
  }
};

onMounted(fetchJobs);
</script>

<template>
  <div class="page">
    <NavBar />

    <main class="main">
      <!-- Header -->
      <section class="page-header box">
        <div>
          <h1 class="page-title">▤ JOBS DATABASE</h1>
          <p class="page-sub">{{ total.toLocaleString() }} harvested jobs in PostgreSQL</p>
        </div>
      </section>

      <!-- Search Bar -->
      <div class="search-row">
        <input
          class="search-input"
          v-model="search"
          placeholder="Search by title, company or location..."
          type="text"
        />
      </div>

      <!-- Error -->
      <div v-if="error" class="error-box box">{{ error }}</div>

      <!-- Loading -->
      <div v-if="loading" class="loading-box">Fetching jobs...</div>

      <!-- Jobs Grid -->
      <div v-else-if="jobs.length" class="jobs-grid">
        <div v-for="job in jobs" :key="job.job_id" class="box job-card">
          <div class="job-top">
            <span class="job-source">{{ job.source }}</span>
          </div>
          <h3 class="job-title">{{ job.title }}</h3>
          <p class="job-company">{{ job.company }}</p>
          <p class="job-location">📍 {{ job.location || 'Remote' }}</p>
          <a
            v-if="job.url"
            :href="job.url"
            target="_blank"
            rel="noopener noreferrer"
            class="job-link"
          >
            View Posting →
          </a>
          <button class="brutal-btn delete-btn" @click="deleteJob(job.job_id)">
            DELETE
          </button>
        </div>
      </div>

      <!-- Empty state -->
      <div v-else class="empty-box box">
        <p>No jobs found. Run a harvest from the Control Room first.</p>
      </div>

      <!-- Pagination -->
      <div v-if="pages > 1" class="pagination">
        <button class="page-btn" @click="prevPage" :disabled="page === 1">← Prev</button>
        <span class="page-indicator">Page {{ page }} of {{ pages }}</span>
        <button class="page-btn" @click="nextPage" :disabled="page === pages">Next →</button>
      </div>

    </main>
  </div>
</template>

<style scoped>
.main { max-width: 1100px; width: 100%; margin: 0 auto; padding: 28px 28px 60px; display: flex; flex-direction: column; gap: 20px; }
.page-header  { padding: 20px 24px; }
.page-title   { font-size: 28px; font-weight: 900; text-transform: uppercase; }
.page-sub     { font-size: 13px; font-weight: 600; opacity: 0.6; margin-top: 4px; }
.search-row   { display: flex; gap: 12px; }
.search-input {
  flex: 1;
  height: 44px;
  padding: 0 14px;
  font-size: 14px;
  font-weight: 600;
  border: var(--border);
  box-shadow: var(--shadow);
  background: var(--surface);
  outline: none;
}
.search-input:focus { box-shadow: 6px 6px 0 var(--ink); }
.error-box   { padding: 16px; color: var(--accent); font-weight: 700; }
.loading-box { text-align: center; font-weight: 700; padding: 40px; opacity: 0.5; }
.jobs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}
.job-card    { padding: 20px; display: flex; flex-direction: column; gap: 8px; }
.job-top     { display: flex; justify-content: flex-end; }
.job-source  { font-size: 10px; font-weight: 900; text-transform: uppercase; letter-spacing: 0.1em; background: var(--ink); color: #fff; padding: 2px 8px; }
.job-title   { font-size: 16px; font-weight: 900; line-height: 1.3; margin: 0; }
.job-company { font-size: 13px; font-weight: 700; opacity: 0.75; margin: 0; }
.job-location{ font-size: 12px; font-weight: 600; opacity: 0.55; margin: 0; }
.job-link    {
  margin-top: 8px;
  display: inline-block;
  padding: 7px 14px;
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  text-decoration: none;
  color: var(--ink);
  border: var(--border);
  box-shadow: 3px 3px 0 var(--ink);
  background: var(--surface);
  transition: box-shadow 0.1s, transform 0.1s;
  align-self: flex-start;
}
.job-link:hover  { background: #f5f5f5; }
.job-link:active { box-shadow: 1px 1px 0 var(--ink); transform: translate(2px, 2px); }
.delete-btn {
  margin-top: 8px;
  background: #ff7675;
  color: var(--ink);
  font-size: 11px;
  padding: 6px 12px;
  align-self: flex-start;
}
.delete-btn:hover { background: #ff5252; }
.empty-box { padding: 40px; text-align: center; font-weight: 700; opacity: 0.5; }
.pagination      { display: flex; align-items: center; justify-content: center; gap: 16px; }
.page-btn {
  padding: 8px 20px;
  font-weight: 800;
  font-size: 13px;
  border: var(--border);
  box-shadow: 3px 3px 0 var(--ink);
  background: var(--surface);
  cursor: pointer;
  transition: box-shadow 0.1s, transform 0.1s;
}
.page-btn:disabled { opacity: 0.35; cursor: not-allowed; box-shadow: none; }
.page-btn:not(:disabled):active { box-shadow: 1px 1px 0 var(--ink); transform: translate(2px, 2px); }
.page-indicator { font-weight: 800; font-size: 13px; }
@media (max-width: 640px) {
  .jobs-grid { grid-template-columns: 1fr; }
}
</style>
