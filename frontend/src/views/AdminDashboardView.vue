<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import NavBar from '@/components/NavBar.vue';

const router = useRouter();
const userName = (localStorage.getItem('username') || 'Admin').toUpperCase();
const userRole = (localStorage.getItem('role') || 'System Admin').toUpperCase();

// Mock stats for now until Task 6 connects the database perfectly
const stats = ref({
  students: 1240,
  companies: 34,
  jobs: 42091
});

const systemLogs = ref([
  "> [SYSTEM] Database securely linked in production mode.",
  "> [SYSTEM] Awaiting Harvester trigger...",
]);

</script>

<template>
  <div class="page">
    <NavBar />

    <div class="sub-tabs">
      <button class="sub-tab sub-tab--active">Control Room</button>
      <button class="sub-tab">Harvesters</button>
      <button class="sub-tab">Jobs DB</button>
      <button class="sub-tab">Settings</button>
    </div>

    <main class="main">
      <!-- Admin Identity Header -->
      <section class="profile-header box">
        <div class="profile-left">
          <div class="avatar admin-avatar">
            <!-- Shield/Server Icon -->
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            </svg>
          </div>
          <div>
            <h2 class="profile-name">{{ userName }}</h2>
            <p class="profile-role">{{ userRole }} • Superuser Tier</p>
          </div>
        </div>
        <button class="outline-btn" @click="router.push('/dashboard')">
          ✦ BACK TO MAIN
        </button>
      </section>

      <!-- IIFR BAR BANNER -->
      <div class="banner">
         ================= IIFR BAR: HARVESTER ENGINE ==========================
      </div>

      <!-- Main Two Column Grid -->
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

        <!-- Right Col: Live Logs -->
        <div class="col">
           <h3 class="section-title">▤ LIVE HARVESTER LOGS</h3>
           
           <div class="box terminal-box">
             <div v-for="(log, idx) in systemLogs" :key="idx" class="terminal-line">
               {{ log }}
             </div>
             <div class="terminal-line cursor">_</div>
           </div>
        </div>
      </div>

      <!-- Triggers Grid -->
      <h3 class="section-title" style="margin-top: 20px;">▤ HARVESTER TRIGGERS</h3>
      <div class="grid trigger-grid">
         <button class="box trigger-btn adzuna-btn">
            <span class="trigger-title">⚡ RUN ADZUNA HARVEST</span>
            <span class="trigger-sub">(Tier A - Rapid Fetch)</span>
         </button>
         
         <button class="box trigger-btn proxy-btn">
            <span class="trigger-title">⚡ RUN PROXY SCRAPE</span>
            <span class="trigger-sub">(Tier B - Headless Playwright)</span>
         </button>
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

.terminal-box { background: var(--ink); color: #00ff00; padding: 20px; font-family: monospace; font-size: 13px; min-height: 250px; flex: 1; display: flex; flex-direction: column; gap: 8px;}
.terminal-line { word-wrap: break-word;}
.cursor { animation: blink 1s step-end infinite;}
@keyframes blink { 50% { opacity: 0; } }

.trigger-grid { grid-template-columns: 1fr 1fr; gap: 20px; }
.trigger-btn { padding: 24px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 8px; cursor: pointer; transition: transform 0.1s;}
.trigger-btn:active { box-shadow: 1px 1px 0 var(--ink); transform: translate(3px,3px); }
.trigger-title { font-size: 18px; font-weight: 900; }
.trigger-sub { font-size: 12px; font-weight: 600; opacity: 0.7; }
.adzuna-btn { background: #ffeaa7; }
.proxy-btn { background: #dfe6e9; opacity: 0.7; }

@media (max-width: 860px) {
  .grid { grid-template-columns: 1fr; }
  .trigger-grid { grid-template-columns: 1fr; }
}
</style>
