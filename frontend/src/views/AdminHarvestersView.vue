<script setup>
import { ref, onMounted } from 'vue';
import NavBar from '@/components/NavBar.vue';
import api from '@/services/api';

const userName = (localStorage.getItem('username') || 'Admin').toUpperCase();
const userRole = (localStorage.getItem('role') || 'System Admin').toUpperCase();

const systemLogs = ref(["> [SYSTEM] Connecting to database..."]);
const harvesting = ref(false);

const loadLogs = async () => {
  try {
    const res = await api.get('/admin/logs');
    if (res.data.length === 0) {
      systemLogs.value = ['> [SYSTEM] No harvest runs yet. Trigger one below.'];
      return;
    }
    systemLogs.value = res.data.map(l => {
      const dateObj = new Date(l.timestamp + 'Z');
      const istTime = dateObj.toLocaleString('en-IN', {
        timeZone: 'Asia/Kolkata',
        dateStyle: 'short',
        timeStyle: 'medium'
      });
      return `> [${l.status.toUpperCase()}] Run #${l.log_id} — ${l.jobs_added} jobs added @ ${istTime} (IST)`;
    });
  } catch {
    systemLogs.value.push('> [ERROR] Failed to load harvest logs.');
  }
};

const triggerHarvest = async (sourceTarget = 'all') => {
  if (harvesting.value) return;
  harvesting.value = true;
  const label = sourceTarget === 'all' ? 'ALL SOURCES' : sourceTarget;
  systemLogs.value.push(`> [SYSTEM] Harvest triggered for ${label} — running in background...`);
  try {
    await api.post('/admin/harvest', { source: sourceTarget });
    systemLogs.value.push(`> [SYSTEM] ${label} harvest started. Refreshing logs in 10s...`);
    setTimeout(async () => {
      await loadLogs();
      harvesting.value = false;
    }, 10000);
  } catch {
    systemLogs.value.push('> [ERROR] Failed to trigger harvest.');
    harvesting.value = false;
  }
};

onMounted(async () => {
  await loadLogs();
});
</script>

<template>
  <div class="page">
    <NavBar />

    <main class="main">
      <!-- Admin Identity Header -->
      <section class="profile-header box">
        <div class="profile-left">
          <div class="avatar admin-avatar">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            </svg>
          </div>
          <div>
            <h2 class="profile-name">{{ userName }}</h2>
            <p class="profile-role">{{ userRole }} • Superuser Tier</p>
          </div>
        </div>
      </section>

      <!-- IIFR BAR BANNER -->
      <div class="banner">
         ================= IIFR BAR: HARVESTER ENGINE ==========================
      </div>

      <!-- Triggers Grid -->
      <h3 class="section-title">▤ HARDWARE / API CONFIGURATION</h3>
      <div class="grid trigger-grid">
         <button class="box trigger-btn remotive-btn" @click="triggerHarvest('Remotive')" :disabled="harvesting">
            <span class="trigger-title">⚡ FETCH REMOTIVE</span>
            <span class="trigger-sub">{{ harvesting ? 'Running...' : '(Tier A - Rapid Fetch)' }}</span>
         </button>

         <button class="box trigger-btn jsearch-btn" @click="triggerHarvest('LinkedIn')" :disabled="harvesting">
            <span class="trigger-title">⚡ FETCH JSEARCH</span>
            <span class="trigger-sub">{{ harvesting ? 'Running...' : '(LinkedIn via RapidAPI)' }}</span>
         </button>

         <button class="box trigger-btn activejobs-btn" @click="triggerHarvest('ActiveJobsDB')" :disabled="harvesting">
            <span class="trigger-title">⚡ FETCH ACTIVE JOBS DB</span>
            <span class="trigger-sub">{{ harvesting ? 'Running...' : '(Active Jobs RapidAPI)' }}</span>
         </button>

         <button class="box trigger-btn master-btn" @click="triggerHarvest('all')" :disabled="harvesting">
            <span class="trigger-title">🚀 RUN MASTER HARVEST</span>
            <span class="trigger-sub">{{ harvesting ? 'Running...' : '(All Sources Combined)' }}</span>
         </button>
      </div>

      <div class="col" style="margin-top: 20px;">
         <h3 class="section-title">▤ LIVE HARVESTER LOGS</h3>
         <div class="box terminal-box">
           <div v-for="(log, idx) in systemLogs" :key="idx" class="terminal-line">
             {{ log }}
           </div>
           <div class="terminal-line cursor">_</div>
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

.main { max-width: 1100px; width: 100%; margin: 0 auto; padding: 28px 28px 60px; display: flex; flex-direction: column; gap: 24px; }
.box { background: var(--surface); border: var(--border); box-shadow: var(--shadow); }

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

.terminal-box { background: var(--ink); color: #00ff00; padding: 20px; font-family: monospace; font-size: 13px; min-height: 250px; flex: 1; display: flex; flex-direction: column; gap: 8px;}
.terminal-line { word-wrap: break-word;}
.cursor { animation: blink 1s step-end infinite;}
@keyframes blink { 50% { opacity: 0; } }

.trigger-grid { grid-template-columns: 1fr 1fr; gap: 20px; }
.trigger-btn { padding: 24px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 8px; cursor: pointer; transition: transform 0.1s;}
.trigger-btn:active { box-shadow: 1px 1px 0 var(--ink); transform: translate(3px,3px); }
.trigger-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.trigger-title { font-size: 18px; font-weight: 900; }
.trigger-sub { font-size: 12px; font-weight: 600; opacity: 0.7; }
.remotive-btn { background: #ffeaa7; }
.jsearch-btn { background: #74b9ff; }
.activejobs-btn { background: #a29bfe; }
.master-btn { background: var(--admin-accent); color: white; }

@media (max-width: 860px) {
  .grid { grid-template-columns: 1fr; }
  .trigger-grid { grid-template-columns: 1fr; }
}
</style>
