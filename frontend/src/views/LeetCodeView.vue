<script setup>
import { ref, computed, onMounted } from 'vue';
import NavBar from '@/components/NavBar.vue';
import api from '@/services/api';

const stats = ref(null);
const advice = ref('');
const loading = ref(false);
const error = ref('');
const noUsername = ref(false);

const topTags = computed(() => {
  if (!stats.value || !stats.value.topics) return [];
  const entries = Object.entries(stats.value.topics);
  return entries.slice(0, 8);
});

const weakTags = computed(() => {
  if (!stats.value || !stats.value.topics) return [];
  const entries = Object.entries(stats.value.topics);
  // Weak tags are those with fewer problems solved (bottom of sorted list)
  return entries.slice(-5).reverse();
});

const fetchStats = async () => {
  loading.value = true;
  error.value = '';
  noUsername.value = false;

  try {
    // First, check if the user has a LeetCode username set
    const profileRes = await api.get('/profile');
    if (!profileRes.data.leetcode_username) {
      noUsername.value = true;
      return;
    }

    const res = await api.get('/api/leetcode/stats');
    stats.value = res.data.stats;
    advice.value = res.data.advice || '';
  } catch (err) {
    if (err.response?.data?.no_username) {
      noUsername.value = true;
      error.value = err.response.data.message;
    } else {
      error.value = err.response?.data?.message || 'Network error. Could not reach the server.';
    }
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchStats();
});
</script>

<template>
  <div class="page">
    <NavBar />
    <main class="main">
      <div class="page-header">
        <h1 class="page-title">LeetCode Dashboard</h1>
        <p class="page-sub">Live performance data from your LeetCode profile.</p>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="box status-box">
        <p class="status-text">Fetching your LeetCode data...</p>
      </div>

      <!-- No Username Set -->
      <div v-else-if="noUsername" class="box status-box warning">
        <p class="status-label">NO USERNAME</p>
        <p class="status-text">You haven't set a LeetCode username yet. Go to your <strong>Profile</strong> and add it to get started.</p>
        <router-link to="/profile" class="outline-btn">GO TO PROFILE</router-link>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="box status-box error">
        <p class="status-label">ERROR</p>
        <p class="status-text">{{ error }}</p>
        <button class="outline-btn" @click="fetchStats">RETRY</button>
      </div>

      <!-- Data Loaded -->
      <template v-else-if="stats">

        <!-- Username Banner -->
        <div class="box username-banner">
          <span class="username-label">LEETCODE USER</span>
          <span class="username-value">{{ stats.username }}</span>
        </div>

        <!-- AI Advice Card -->
        <div v-if="advice" class="box advice-card">
          <div class="advice-header">
            <span class="advice-icon">&#10023;</span>
            <span class="advice-label">AI STUDY ADVICE</span>
          </div>
          <p class="advice-text">{{ advice }}</p>
        </div>

        <!-- Stat Cards Row: Total / Easy / Medium / Hard -->
        <div class="stat-grid">
          <div class="box stat-card">
            <p class="stat-label">Total Solved</p>
            <p class="stat-value total">{{ stats.total_solved }}</p>
          </div>
          <div class="box stat-card">
            <p class="stat-label">Easy</p>
            <p class="stat-value easy">{{ stats.easy_solved }}</p>
          </div>
          <div class="box stat-card">
            <p class="stat-label">Medium</p>
            <p class="stat-value medium">{{ stats.medium_solved }}</p>
          </div>
          <div class="box stat-card">
            <p class="stat-label">Hard</p>
            <p class="stat-value hard">{{ stats.hard_solved }}</p>
          </div>
        </div>

        <!-- Two-Column Layout: Contest Ranking + Tags -->
        <div class="grid-two">

          <!-- Contest Ranking -->
          <div class="box section-box">
            <h3 class="section-title">Contest Performance</h3>
            <div class="contest-stats">
              <div class="contest-row">
                <span class="contest-label">Contests Attended</span>
                <span class="contest-value">{{ stats.contests.attended }}</span>
              </div>
              <div class="contest-row">
                <span class="contest-label">Rating</span>
                <span class="contest-value">{{ stats.contests.rating }}</span>
              </div>
              <div class="contest-row">
                <span class="contest-label">Top %</span>
                <span class="contest-value">{{ stats.contests.topPercentage }}%</span>
              </div>
            </div>
          </div>

          <!-- Strong Tags -->
          <div class="box section-box">
            <h3 class="section-title">Strongest Topics</h3>
            <div class="tag-list">
              <div v-for="([name, count], i) in topTags" :key="'s-'+i" class="tag-row">
                <span class="tag-name">{{ name }}</span>
                <span class="tag-badge strong">{{ count }}</span>
              </div>
              <p v-if="topTags.length === 0" class="empty-text">No topic data available.</p>
            </div>
          </div>
        </div>

        <!-- Weak Tags Section -->
        <div class="box section-box">
          <h3 class="section-title">Areas to Improve</h3>
          <div class="tag-list horizontal">
            <div v-for="([name, count], i) in weakTags" :key="'w-'+i" class="tag-chip weak">
              {{ name }} <span class="chip-count">{{ count }}</span>
            </div>
            <p v-if="weakTags.length === 0" class="empty-text">No topic data available.</p>
          </div>
        </div>

      </template>
    </main>
  </div>
</template>

<style scoped>
.main {
  max-width: 1100px;
  width: 100%;
  margin: 0 auto;
  padding: 28px 28px 60px;
  display: flex;
  flex-direction: column;
  gap: 22px;
}
.outline-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--surface);
  border: var(--border);
  box-shadow: var(--shadow);
  padding: 10px 18px;
  font-weight: 800;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  cursor: pointer;
  color: var(--ink);
  text-decoration: none;
  transition: box-shadow 0.1s, transform 0.1s;
}
.outline-btn:hover  { background: #f5f5f5; }
.outline-btn:active { box-shadow: 1px 1px 0 var(--ink); transform: translate(2px,2px); }
/* ── Page Header ───────────────────────────────────────────── */
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
/* ── Status / Loading / Error boxes ─────────────────────────── */
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
.status-box.warning { border-left: 6px solid #fbbf24; }
.status-box.error   { border-left: 6px solid #ef4444; }
/* ── Username Banner ────────────────────────────────────────── */
.username-banner {
  padding: 16px 24px;
  display: flex;
  align-items: center;
  gap: 14px;
}
.username-label {
  font-size: 10px;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  opacity: 0.5;
}
.username-value {
  font-size: 22px;
  font-weight: 900;
  letter-spacing: -0.5px;
}
/* ── Stat Cards Grid ────────────────────────────────────────── */
.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}
.stat-card {
  padding: 22px 18px;
}
.stat-label {
  font-size: 10px;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  opacity: 0.6;
}
.stat-value {
  font-size: 42px;
  font-weight: 900;
  margin-top: 6px;
}
.stat-value.total  { color: var(--ink); }
.stat-value.easy   { color: #22c55e; }
.stat-value.medium { color: #f59e0b; }
.stat-value.hard   { color: #ef4444; }
/* ── Two-Column Grid ────────────────────────────────────────── */
.grid-two {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 22px;
}
/* ── Section Box ────────────────────────────────────────────── */
.section-box {
  padding: 22px;
}
.section-title { margin-bottom: 16px; }
/* ── Contest Stats ──────────────────────────────────────────── */
.contest-stats {
  display: flex;
  flex-direction: column;
  gap: 0;
}
.contest-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #e0e0e0;
}
.contest-row:last-child { border-bottom: none; }
.contest-label {
  font-size: 14px;
  font-weight: 700;
}
.contest-value {
  font-size: 22px;
  font-weight: 900;
}
/* ── Tag Lists ──────────────────────────────────────────────── */
.tag-list {
  display: flex;
  flex-direction: column;
  gap: 0;
}
.tag-list.horizontal {
  flex-direction: row;
  flex-wrap: wrap;
  gap: 10px;
}
.tag-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #e0e0e0;
}
.tag-row:last-child { border-bottom: none; }
.tag-name {
  font-size: 13px;
  font-weight: 700;
}
.tag-badge {
  font-size: 12px;
  font-weight: 800;
  padding: 3px 10px;
  border: 2px solid var(--ink);
}
.tag-badge.strong {
  background: #34d399;
  box-shadow: 2px 2px 0 var(--ink);
}
.tag-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border: 2px solid var(--ink);
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
}
.tag-chip.weak {
  background: #fca5a5;
  box-shadow: 2px 2px 0 var(--ink);
}
.chip-count {
  background: var(--ink);
  color: #fff;
  padding: 1px 6px;
  font-size: 10px;
  font-weight: 900;
}
/* ── AI Advice Card ─────────────────────────────────────────── */
.advice-card {
  padding: 22px 28px;
  border-left: 6px solid var(--accent);
  background: #f0f7ff;
}
.advice-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}
.advice-icon {
  font-size: 18px;
  color: var(--accent);
}
.advice-label {
  font-size: 11px;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--accent);
}
.advice-text {
  font-size: 15px;
  font-weight: 600;
  line-height: 1.6;
}
.empty-text {
  font-size: 13px;
  font-weight: 600;
  opacity: 0.5;
  font-style: italic;
  padding: 12px 0;
}
/* ── Responsive ─────────────────────────────────────────────── */
@media (max-width: 860px) {
  .stat-grid { grid-template-columns: repeat(2, 1fr); }
.grid-two  { grid-template-columns: 1fr; }
.main      { padding: 16px; }
}
</style>
