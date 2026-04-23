<template>
  <div class="page">
    <NavBar />
    <div class="content">
      <div class="header">
        <h1 class="title">Student Job Feed</h1>
        <p class="sub">
          <span v-if="totalJobs > 0" class="job-count">{{ totalJobs.toLocaleString() }} jobs available</span>
          <span v-else>View all available career opportunities tailored for you.</span>
        </p>
      </div>

      <div class="controls">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search for jobs, companies, or locations..."
          class="search-bar"
          @keyup.enter="fetchJobs"
        />
        <button class="btn search-btn" @click="fetchJobs">Search</button>
      </div>

      <div class="jobs-list" v-if="jobs.length > 0">
        <div class="job-card" v-for="job in jobs" :key="job.job_id">
          <div class="job-header">
            <h2 class="job-title">{{ job.title }}</h2>
            <div class="badges">
              <span v-if="job.match_score !== undefined && job.match_score > 0" class="match-badge" :class="getMatchClass(job.match_score)">
                {{ job.match_score }}% Match
              </span>
              <span class="source-badge" :class="job.source.toLowerCase()">{{ job.source }}</span>
            </div>
          </div>
          <p class="company-name">{{ job.company }} &mdash; <span>{{ job.location || 'Remote' }}</span></p>
          <div class="job-desc" v-html="truncateDesc(job.description)"></div>
          <div class="job-actions">
            <button class="btn readiness-btn" @click="toggleReadiness(job)">
              {{ activeReadiness === job.job_id ? 'HIDE' : 'CHECK READINESS' }}
            </button>
            <a v-if="job.url" :href="job.url" target="_blank" class="btn link-btn">Apply / View Source</a>
            <span v-else class="btn link-btn disabled">Apply / View Source</span>
          </div>

          <!-- Readiness Panel -->
          <div v-if="activeReadiness === job.job_id" class="readiness-panel">
            <div v-if="readinessLoading" class="readiness-loading">
              <p>Analyzing your readiness...</p>
            </div>
            <div v-else-if="readinessData">
              <!-- No data for this company -->
              <div v-if="!readinessData.has_data" class="readiness-empty">
                <p>No interview data available for <strong>{{ readinessData.company }}</strong>.</p>
              </div>

              <!-- Readiness data available -->
              <template v-else>
                <div class="readiness-header">
                  <div class="readiness-score-box">
                    <span class="readiness-label">READINESS</span>
                    <span class="readiness-pct" :class="readinessColor(readinessData.readiness_pct)">{{ readinessData.readiness_pct }}%</span>
                  </div>
                  <div class="readiness-meta">
                    <p class="readiness-company">{{ readinessData.company }}</p>
                    <p class="readiness-total">{{ readinessData.total_questions }} questions in database</p>
                    <div class="difficulty-pills">
                      <span class="pill easy">Easy {{ readinessData.difficulty_breakdown.EASY }}</span>
                      <span class="pill medium">Med {{ readinessData.difficulty_breakdown.MEDIUM }}</span>
                      <span class="pill hard">Hard {{ readinessData.difficulty_breakdown.HARD }}</span>
                    </div>
                  </div>
                </div>

                <div v-if="!readinessData.leetcode_username" class="readiness-warning">
                  Set your LeetCode username in your <router-link to="/profile">Profile</router-link> to see personalized topic comparison.
                </div>

                <div class="topic-comparison">
                  <h3 class="topic-section-title">Topic Coverage & Recommendations</h3>
                  <div class="topic-cards-grid">
                    <div v-for="(t, i) in readinessData.topics" :key="i" class="topic-card" :class="{ 'is-missing': t.is_missing }">
                      <div class="topic-card-header">
                        <span class="topic-name">{{ t.topic }}</span>
                        <span class="topic-badge" :class="t.is_missing ? 'weak' : 'strong'">
                          {{ t.is_missing ? 'NEEDS PRACTICE' : 'STRONG' }} ({{ t.solved }} solved)
                        </span>
                      </div>
                      
                      <div v-if="t.is_missing && t.recommended_questions && t.recommended_questions.length > 0" class="recommended-qs">
                        <p class="rq-title">Top <span>{{ readinessData.company }}</span> {{ t.topic }} Questions:</p>
                        <ul class="rq-list">
                          <li v-for="(q, j) in t.recommended_questions" :key="j">
                            <a v-if="q.url" :href="q.url" target="_blank">{{ q.title }}</a>
                            <span v-else>{{ q.title }}</span>
                            <span class="q-diff" :class="q.difficulty.toLowerCase()">{{ q.difficulty[0] }}</span>
                          </li>
                        </ul>
                      </div>
                      <div v-else-if="!t.is_missing" class="strong-status">
                        <p>Solid experience! Keep it up.</p>
                      </div>
                    </div>
                  </div>
                </div>
              </template>
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="!loading" class="no-jobs">
        <p>No jobs found. Try adjusting your search.</p>
      </div>

      <div class="pagination" v-if="totalPages > 1">
        <button class="btn page-btn" :disabled="currentPage === 1" @click="changePage(currentPage - 1)">Previous</button>
        <span class="page-info">Page {{ currentPage }} of {{ totalPages }}</span>
        <button class="btn page-btn" :disabled="currentPage === totalPages" @click="changePage(currentPage + 1)">Next</button>
      </div>

      <div v-if="loading" class="loading-state">
        <p>Loading jobs...</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import NavBar from '@/components/NavBar.vue';
import api from '@/services/api';
import cache from '@/services/cache';

const jobs = ref([]);
const totalJobs = ref(0);
const searchQuery = ref('');
const currentPage = ref(1);
const totalPages = ref(1);
const loading = ref(false);

// Readiness state
const activeReadiness = ref(null);
const readinessData = ref(null);
const readinessLoading = ref(false);

const fetchJobs = async () => {
  // 1. Try to load from cache for the first page (no search) for instant UI
  if (currentPage.value === 1 && !searchQuery.value) {
    const cachedJobs = cache.get('jobs_page_1');
    if (cachedJobs) {
      jobs.value = cachedJobs.jobs;
      totalJobs.value = cachedJobs.total || 0;
      totalPages.value = cachedJobs.pages;
      currentPage.value = cachedJobs.page;
    }
  }

  loading.value = true;
  try {
    const response = await api.get(`/api/jobs?page=${currentPage.value}&q=${encodeURIComponent(searchQuery.value)}`);

    if (response.status !== 200) {
      console.error('Failed to fetch jobs');
      return;
    }

    const data = response.data;
    jobs.value = data.jobs;
    totalJobs.value = data.total || 0;
    totalPages.value = data.pages;
    currentPage.value = data.page;

    // 2. Cache the first page for next time
    if (currentPage.value === 1 && !searchQuery.value) {
      cache.set('jobs_page_1', data, 30); // Cache job feed for 30 minutes
    }
  } catch (err) {
    console.error('Error fetching jobs:', err);
  } finally {
    loading.value = false;
  }
};

// Dynamic search: debounce 400ms so every keystroke doesn't fire an API call
let _searchDebounce = null;
watch(searchQuery, () => {
  clearTimeout(_searchDebounce);
  _searchDebounce = setTimeout(() => {
    currentPage.value = 1;
    fetchJobs();
  }, 400);
});

const toggleReadiness = async (job) => {
  if (activeReadiness.value === job.job_id) {
    activeReadiness.value = null;
    readinessData.value = null;
    return;
  }

  activeReadiness.value = job.job_id;
  readinessLoading.value = true;
  readinessData.value = null;

  try {
    const res = await api.get(`/api/jobs/${job.job_id}/readiness`);
    const data = res.data;
    readinessData.value = data;
  } catch (err) {
    console.error('Error fetching readiness:', err);
    readinessData.value = { has_data: false, company: job.company };
  } finally {
    readinessLoading.value = false;
  }
};



const readinessColor = (pct) => {
  if (pct >= 70) return 'high';
  if (pct >= 40) return 'mid';
  return 'low';
};

const getMatchClass = (score) => {
  if (score >= 40) return 'match-high';
  if (score >= 20) return 'match-med';
  return 'match-low';
};

const changePage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page;
    activeReadiness.value = null;
    readinessData.value = null;
    fetchJobs();
    window.scrollTo(0, 0);
  }
};

const truncateDesc = (desc) => {
  if (!desc) return 'No description available.';
  const temp = document.createElement('div');
  temp.innerHTML = desc;
  const text = temp.textContent || temp.innerText || '';
  if (text.length > 250) {
    return text.substring(0, 250) + '...';
  }
  return text;
};

onMounted(() => {
  fetchJobs();
});
</script>

<style scoped>
.content {
  padding: 40px;
  max-width: 900px;
  margin: 0 auto;
}
.header {
  margin-bottom: 30px;
}
.title {
  font-size: 40px;
  font-weight: 900;
  text-transform: uppercase;
  margin-bottom: 10px;
}
.sub {
  font-size: 16px;
  font-weight: 600;
  opacity: 0.7;
}
.controls {
  display: flex;
  gap: 15px;
  margin-bottom: 30px;
}
.search-bar {
  flex-grow: 1;
  padding: 12px 20px;
  border: var(--border);
  box-shadow: var(--shadow);
  font-family: inherit;
  font-size: 16px;
  font-weight: 600;
  outline: none;
}
.search-bar:focus {
  transform: translate(-2px, -2px);
  box-shadow: 6px 6px 0 var(--ink);
}
.btn {
  background: var(--surface);
  border: var(--border);
  box-shadow: var(--shadow);
  padding: 12px 24px;
  font-family: inherit;
  font-weight: 800;
  text-transform: uppercase;
  cursor: pointer;
  transition: all 0.1s;
  text-decoration: none;
  display: inline-block;
  color: var(--ink);
  font-size: 13px;
}
.btn:active {
  transform: translate(2px, 2px);
  box-shadow: 2px 2px 0 var(--ink);
}
.btn:disabled, .btn.disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
  box-shadow: var(--shadow);
  opacity: 0.7;
}
.search-btn { background: #34d399; }
.jobs-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.job-card {
  background: var(--surface);
  border: var(--border);
  box-shadow: 5px 5px 0 var(--ink);
  padding: 25px;
}
.job-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}
.job-title {
  font-size: 24px;
  font-weight: 900;
  margin: 0;
}
.badges {
  display: flex;
  gap: 8px;
  align-items: center;
}
.match-badge {
  font-size: 11px;
  font-weight: 800;
  border: 2px solid var(--ink);
  padding: 4px 10px;
  text-transform: uppercase;
  white-space: nowrap;
  box-shadow: 2px 2px 0 var(--ink);
}
.match-high { background-color: #bbf7d0; color: #166534; }
.match-med { background-color: #fef08a; color: #854d0e; }
.match-low { background-color: #fca5a5; color: #991b1b; }

.source-badge {
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
  padding: 4px 8px;
  border: var(--border);
  background: #e5e7eb;
}
.source-badge.remotive { background: #60a5fa; }
.source-badge.jsearch { background: #f472b6; }
.source-badge.activejobsdb { background: #fbbf24; }
.source-badge.direct { background: #34d399; }
.company-name {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 15px;
}
.company-name span {
  font-weight: 600;
  opacity: 0.8;
  font-style: italic;
}
.job-desc {
  font-size: 15px;
  line-height: 1.5;
  margin-bottom: 20px;
  color: #333;
}
.job-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
.readiness-btn {
  background: #a78bfa;
}
/* ── Readiness Panel ─────────────────────────────────────────── */
.readiness-panel {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 2px dashed var(--ink);
}
.readiness-loading, .readiness-empty {
  text-align: center;
  padding: 24px;
  font-weight: 800;
  font-size: 15px;
}
.readiness-header {
  display: flex;
  gap: 24px;
  align-items: center;
  margin-bottom: 18px;
}
.readiness-score-box {
  background: var(--surface);
  border: var(--border);
  box-shadow: var(--shadow);
  padding: 18px 24px;
  text-align: center;
  min-width: 120px;
}
.readiness-label {
  font-size: 9px;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  opacity: 0.5;
  display: block;
  margin-bottom: 4px;
}
.readiness-pct {
  font-size: 40px;
  font-weight: 900;
}
.readiness-pct.high { color: #22c55e; }
.readiness-pct.mid  { color: #f59e0b; }
.readiness-pct.low  { color: #ef4444; }
.readiness-meta {
  flex: 1;
}
.readiness-company {
  font-size: 20px;
  font-weight: 900;
  text-transform: uppercase;
  margin-bottom: 4px;
}
.readiness-total {
  font-size: 13px;
  font-weight: 600;
  opacity: 0.6;
  margin-bottom: 10px;
}
.difficulty-pills {
  display: flex;
  gap: 8px;
}
.pill {
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
  padding: 3px 10px;
  border: 2px solid var(--ink);
}
.pill.easy   { background: #bbf7d0; }
.pill.medium { background: #fde68a; }
.pill.hard   { background: #fca5a5; }
.readiness-warning {
  background: #fef3c7;
  border: var(--border);
  padding: 12px 16px;
  font-size: 13px;
  font-weight: 700;
  margin-bottom: 16px;
}
.readiness-warning a {
  color: var(--ink);
  font-weight: 900;
}
/* ── Topic Cards & Recommendations ───────────────────────────────────── */
.topic-comparison {
  margin-top: 24px;
}
.topic-section-title {
  font-size: 16px;
  font-weight: 900;
  text-transform: uppercase;
  margin-bottom: 16px;
  text-decoration: underline;
  text-underline-offset: 4px;
  text-decoration-thickness: 2px;
}
.topic-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}
.topic-card {
  background: var(--surface);
  border: 2px solid var(--ink);
  padding: 16px;
  box-shadow: 3px 3px 0 var(--ink);
  display: flex;
  flex-direction: column;
}
.topic-card.is-missing {
  background: #fef2f2; /* extremely light red */
}
.topic-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
  padding-bottom: 10px;
  border-bottom: 2px solid var(--ink);
}
.topic-name {
  font-size: 16px;
  font-weight: 900;
}
.topic-badge {
  font-size: 10px;
  font-weight: 900;
  padding: 4px 8px;
  border: 2px solid var(--ink);
  text-transform: uppercase;
  white-space: nowrap;
}
.topic-badge.strong {
  background: #bbf7d0;
  box-shadow: 2px 2px 0 var(--ink);
}
.topic-badge.weak {
  background: #fca5a5;
  box-shadow: 2px 2px 0 var(--ink);
}
.recommended-qs {
  margin-top: 4px;
}
.rq-title {
  font-size: 12px;
  font-weight: 800;
  margin-bottom: 8px;
  color: var(--ink);
}
.rq-title span {
  font-style: italic;
}
.rq-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.rq-list li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  font-weight: 600;
  background: #fff;
  border: 1px solid var(--ink);
  padding: 6px 10px;
}
.rq-list a {
  color: #2563eb;
  text-decoration: none;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 200px;
}
.rq-list a:hover {
  text-decoration: underline;
}
.q-diff {
  font-size: 10px;
  font-weight: 900;
  padding: 2px 6px;
}
.q-diff.easy { color: #16a34a; }
.q-diff.medium { color: #d97706; }
.q-diff.hard { color: #dc2626; }
.strong-status {
  font-size: 13px;
  font-weight: 700;
  color: #16a34a;
  padding-top: 10px;
}
/* ── Pagination ───────────────────────────────────────────────── */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin-top: 40px;
}
.page-info {
  font-weight: 800;
  font-size: 16px;
}
.no-jobs, .loading-state {
  text-align: center;
  padding: 50px;
  background: var(--surface);
  border: var(--border);
  box-shadow: 5px 5px 0 var(--ink);
  font-weight: 800;
  font-size: 18px;
}
/* ── Responsive ───────────────────────────────────────────────── */
@media (max-width: 860px) {
  .content { padding: 16px; }
.readiness-header { flex-direction: column; align-items: flex-start; }
.topic-row { grid-template-columns: 1fr 50px 50px 80px; }
}
</style>
