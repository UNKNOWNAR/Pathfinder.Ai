<script setup>
import { ref, onMounted } from 'vue';
import NavBar from '@/components/NavBar.vue';
import api from '@/services/api';

const stats = ref({ students: '...', companies: '...', jobs: '...', sources: {} });

const loadStats = async () => {
  try {
    const res = await api.get('/admin/stats');
    stats.value = res.data;
  } catch {
    console.error('[ERROR] Failed to load platform stats.');
  }
};

onMounted(async () => {
  await loadStats();
});
</script>

<template>
  <div class="page">
    <NavBar />

    <main class="main">
      <!-- Main Two Column Grid (Now acting as 2 layout columns) -->
      <div class="grid">
        
        <!-- Left Col: Platform Stats -->
        <div class="col">
          <h3 class="section-title">▤ PLATFORM STATISTICS</h3>

          <div class="stat-col">
            <div class="box stat-card">
              <p class="stat-label">TOTAL STUDENTS REG.</p>
              <p class="stat-value">{{ stats.students.toLocaleString() }}</p>
            </div>
            <div class="box stat-card">
              <p class="stat-label">TOTAL COMPANIES MAPPED</p>
              <p class="stat-value">{{ stats.companies }}</p>
            </div>
            <div class="box stat-card highlight-card">
              <p class="stat-label">JOBS IN DATABASE</p>
              <p class="stat-value">{{ stats.jobs.toLocaleString() }}</p>
            </div>
          </div>
        </div>

        <!-- Right Col: Job Sources Grid -->
        <div class="col">
          <h3 class="section-title">▤ JOB SOURCES</h3>
          
          <div class="source-grid" v-if="stats.sources && Object.keys(stats.sources).length">
            <div class="box source-card" v-for="(count, sourceName) in stats.sources" :key="sourceName">
              <span class="source-name">{{ sourceName }}</span>
              <span class="source-count">{{ count.toLocaleString() }}</span>
            </div>
          </div>
          <div v-else class="box source-card">
            <span class="source-name" style="opacity:0.5;">Awaiting initial harvest...</span>
          </div>
        </div>

      </div>

    </main>
  </div>
</template>

<style scoped>
.page {
  --ink:     #111111;
  --bg:      #DEDEDE;
  --surface: #FFFFFF;
  --accent:  #2d8cf0;
  --admin-accent: #ff4757; /* Red accent for admin */
  --border:  2px solid var(--ink);
  --shadow:  4px 4px 0 var(--ink);

  min-height: 100vh;
  background: var(--bg);
  color: var(--ink);
  font-family: 'Segoe UI', sans-serif;
}

.sub-tabs { display: flex; gap: 0; background: var(--surface); border-bottom: var(--border); padding: 0 28px; }
.sub-tab { padding: 14px 22px; font-weight: 800; font-size: 12px; text-transform: uppercase; letter-spacing: 0.06em; background: transparent; border: none; border-bottom: 3px solid transparent; cursor: pointer; color: var(--ink); margin-bottom: -2px; transition: color 0.1s, border-color 0.1s; }
.sub-tab:hover { background: #f5f5f5; }
.sub-tab--active { border-bottom: 3px solid var(--ink); background: var(--admin-accent); color: white;}

.main { max-width: 1100px; width: 100%; margin: 0 auto; padding: 28px 28px 60px; display: flex; flex-direction: column; gap: 24px; }
.box { background: var(--surface); border: var(--border); box-shadow: var(--shadow); }

.outline-btn { display: inline-flex; align-items: center; gap: 6px; background: var(--surface); border: var(--border); box-shadow: var(--shadow); padding: 10px 18px; font-weight: 800; font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; cursor: pointer; color: var(--ink); transition: box-shadow 0.1s, transform 0.1s; }
.outline-btn:hover  { background: #f5f5f5; }
.outline-btn:active { box-shadow: 1px 1px 0 var(--ink); transform: translate(2px,2px); }

.profile-header { padding: 20px 24px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 16px; }
.profile-left { display: flex; align-items: center; gap: 18px; }
.avatar { width: 72px; height: 72px; background: var(--accent); border: var(--border); box-shadow: var(--shadow); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.admin-avatar { background: var(--admin-accent); color: white;}
.profile-name { font-size: 26px; font-weight: 900; letter-spacing: -0.5px; }
.profile-role { font-size: 13px; font-weight: 600; opacity: 0.65; font-style: italic; margin-top: 2px; color: var(--admin-accent);}

.banner { text-align: center; font-family: monospace; font-size: 16px; font-weight: bold; padding: 10px 0; color: var(--admin-accent); letter-spacing: 2px;}

.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
.col  { display: flex; flex-direction: column; gap: 14px; }
.section-title { font-size: 18px; font-weight: 900; text-transform: uppercase; text-decoration: underline; text-underline-offset: 4px; text-decoration-thickness: 2px; }

.stat-col { display: flex; flex-direction: column; gap: 12px; }
.stat-card { padding: 20px 16px; display: flex; justify-content: space-between; align-items: center;}
.highlight-card { background: var(--ink); color: white; }
.highlight-card .stat-label { color: #ccc;}
.stat-label { font-size: 11px; font-weight: 900; text-transform: uppercase; letter-spacing: 0.08em; opacity: 0.8; }
.stat-value { font-size: 28px; font-weight: 900; }

.source-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.source-card { padding: 12px; display: flex; justify-content: space-between; align-items: center; background: #f0f0f0; }
.source-name { font-weight: 800; font-size: 13px; text-transform: uppercase; }
.source-count { font-weight: 900; font-size: 16px; color: var(--accent); }

@media (max-width: 860px) {
  .grid { grid-template-columns: 1fr; }
}
</style>
