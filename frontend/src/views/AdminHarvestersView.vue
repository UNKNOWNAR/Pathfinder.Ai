<script setup>
import { ref, onMounted } from 'vue';
import NavBar from '@/components/NavBar.vue';
import api from '@/services/api';

const systemLogs = ref(["> [SYSTEM] Connecting to database..."]);
const harvesting = ref(false);

const roles = ref('software engineer'); // default selection
const locations = ref('');

const quotas = ref({
  usage: {},
  limits: {}
});

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

const loadQuotas = async () => {
  try {
    const res = await api.get('/admin/quotas');
    quotas.value = res.data;
  } catch {
    systemLogs.value.push('> [ERROR] Failed to load quotas.');
  }
};

const getRemainingStr = (source) => {
  const limit = quotas.value.limits[source];
  if (limit === undefined) return '';
  if (limit === -1) return '(Unlimited)';

  const usage = quotas.value.usage[source] || 0;
  const remaining = Math.max(0, limit - usage);
  return `[${remaining}/${limit} total requests left]`;
};

const isQuotaExhausted = (source) => {
  const limit = quotas.value.limits[source];
  if (limit === undefined || limit === -1) return false;
  const usage = quotas.value.usage[source] || 0;
  return usage >= limit;
};

const triggerHarvest = async (sourceTarget = 'all') => {
  if (harvesting.value) return;
  if (sourceTarget !== 'all' && isQuotaExhausted(sourceTarget)) {
      systemLogs.value.push(`> [ERROR] Total limit exhausted for ${sourceTarget}.`);
      return;
  }

  harvesting.value = true;
  const label = sourceTarget === 'all' ? 'ALL SOURCES' : sourceTarget;
  systemLogs.value.push(`> [SYSTEM] Harvest triggered for ${label} — running in background...`);

  const payload = { source: sourceTarget };
  if (roles.value.trim()) {
      payload.roles = roles.value.split(',').map(r => r.trim()).filter(r => r);
  }
  if (locations.value.trim()) {
      payload.locations = locations.value.split(',').map(l => l.trim()).filter(l => l);
  }

  try {
    await api.post('/admin/harvest', payload);
    systemLogs.value.push(`> [SYSTEM] ${label} harvest started. Refreshing logs in 10s...`);
    setTimeout(async () => {
      await loadLogs();
      await loadQuotas();
      harvesting.value = false;
    }, 10000);
  } catch {
    systemLogs.value.push('> [ERROR] Failed to trigger harvest.');
    harvesting.value = false;
  }
};

onMounted(async () => {
  await loadLogs();
  await loadQuotas();
});
</script>

<template>
  <div class="page">
    <NavBar />

    <main class="main">
      <h3 class="section-title">▤ CONFIGURATION</h3>
      <div class="box config-box">
          <div class="input-group">
            <label>ROLES</label>
            <select v-model="roles" class="brutal-input brutal-select">
              <option value="software engineer">Software Engineer</option>
              <option value="data scientist">Data Scientist</option>
              <option value="data engineer">Data Engineer</option>
              <option value="machine learning engineer">Machine Learning Engineer</option>
              <option value="frontend developer">Frontend Developer</option>
              <option value="backend developer">Backend Developer</option>
              <option value="full stack developer">Full Stack Developer</option>
            </select>
          </div>
          <div class="input-group">
            <label>LOCATIONS (comma-separated)</label>
            <input v-model="locations" type="text" placeholder="e.g. India, Remote, United States" class="brutal-input"/>
            <small class="helper-text">Leave blank for default locations.</small>
          </div>
      </div>

      <!-- Triggers Grid -->
      <h3 class="section-title">▤ HARDWARE / API TRIGGERS</h3>
      <div class="grid trigger-grid">
         <button class="box trigger-btn remotive-btn" @click="triggerHarvest('Remotive')" :disabled="harvesting">
            <span class="trigger-title">⚡ FETCH REMOTIVE</span>
            <span class="trigger-sub">{{ harvesting ? 'Running...' : '(Tier A - Rapid Fetch)' }}</span>
            <span class="trigger-quota">{{ getRemainingStr('Remotive') }}</span>
         </button>

         <button class="box trigger-btn jsearch-btn" @click="triggerHarvest('LinkedIn')" :disabled="harvesting || isQuotaExhausted('LinkedIn')">
            <span class="trigger-title">⚡ FETCH JSEARCH</span>
            <span class="trigger-sub">{{ harvesting ? 'Running...' : '(LinkedIn via RapidAPI)' }}</span>
            <span class="trigger-quota">{{ getRemainingStr('LinkedIn') }}</span>
         </button>

         <button class="box trigger-btn internships-btn" @click="triggerHarvest('Internships')" :disabled="harvesting || isQuotaExhausted('Internships')">
            <span class="trigger-title">⚡ FETCH INTERNSHIPS</span>
            <span class="trigger-sub">{{ harvesting ? 'Running...' : '(Internships API)' }}</span>
            <span class="trigger-quota">{{ getRemainingStr('Internships') }}</span>
         </button>

         <button class="box trigger-btn google-btn" @click="triggerHarvest('GoogleJobs')" :disabled="harvesting || isQuotaExhausted('GoogleJobs')">
            <span class="trigger-title">⚡ FETCH GOOGLE JOBS</span>
            <span class="trigger-sub">{{ harvesting ? 'Running...' : '(Global Aggregator)' }}</span>
            <span class="trigger-quota">{{ getRemainingStr('GoogleJobs') }}</span>
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
   /* Red accent for admin */}
.main { max-width: 1100px; width: 100%; margin: 0 auto; padding: 28px 28px 60px; display: flex; flex-direction: column; gap: 24px; }
.config-box {
    padding: 20px;
    display: flex;
    flex-direction: column;
    gap: 16px;
}
.input-group {
    display: flex;
    flex-direction: column;
    gap: 6px;
}
.input-group label {
    font-size: 14px;
    font-weight: 800;
}
.brutal-select {
    appearance: none;
    -webkit-appearance: none;
    cursor: pointer;
    background-image: linear-gradient(45deg, transparent 50%, var(--ink) 50%),
                      linear-gradient(135deg, var(--ink) 50%, transparent 50%);
    background-position: calc(100% - 20px) calc(1em + 2px),
                         calc(100% - 15px) calc(1em + 2px);
    background-size: 5px 5px,
                     5px 5px;
    background-repeat: no-repeat;
}
.helper-text {
    font-size: 12px;
    font-weight: 600;
    opacity: 0.6;
}
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
.col  { display: flex; flex-direction: column; gap: 14px; }
.terminal-box { background: var(--ink); color: #00ff00; padding: 20px; font-family: monospace; font-size: 13px; min-height: 250px; flex: 1; display: flex; flex-direction: column; gap: 8px;}
.terminal-line { word-wrap: break-word;}
.cursor { animation: blink 1s step-end infinite;}
@keyframes blink { 50% { opacity: 0; } }
.trigger-grid { grid-template-columns: 1fr 1fr; gap: 20px; }
.trigger-btn { padding: 24px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 8px; cursor: pointer; transition: transform 0.1s;}
.trigger-btn:active:not(:disabled) { box-shadow: 1px 1px 0 var(--ink); transform: translate(3px,3px); }
.trigger-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.trigger-title { font-size: 18px; font-weight: 900; }
.trigger-sub { font-size: 12px; font-weight: 600; opacity: 0.7; }
.trigger-quota { font-size: 12px; font-weight: 700; color: #d63031; margin-top: 4px; }
.remotive-btn { background: #ffeaa7; }
.jsearch-btn { background: #74b9ff; }
.internships-btn { background: #55efc4; }
.google-btn { background: #fab1a0; }
.master-btn { background: var(--admin-accent); color: white; }
.master-btn .trigger-quota { color: #fff; }
@media (max-width: 860px) {
  .grid { grid-template-columns: 1fr; }
.trigger-grid { grid-template-columns: 1fr; }
}
</style>