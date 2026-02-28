<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import NavBar from '@/components/NavBar.vue';

const router  = useRouter();
const activeTab = ref('overview');

const userRole = localStorage.getItem('role') || 'Student';
const userName = (localStorage.getItem('username') || 'Alex Rivera').toUpperCase();

const goToProfile = () => router.push('/profile');

const subTabs = [
  { id: 'overview',   label: 'Overview'      },
  { id: 'paths',      label: 'My Paths'      },
  { id: 'analytics',  label: 'AI Analytics'  },
  { id: 'settings',   label: 'Settings'      },
];

const savedPaths = [
  { title: 'Software Engineering', date: 'Feb 24' },
  { title: 'Data Science Route',   date: 'Feb 22' },
  { title: 'Product Management',   date: 'Feb 20' },
];
</script>

<template>
  <div class="page">

    <!-- Global nav -->
    <NavBar />

    <!-- Sub-tab strip -->
    <div class="sub-tabs">
      <button
        v-for="tab in subTabs"
        :key="tab.id"
        class="sub-tab"
        :class="{ 'sub-tab--active': activeTab === tab.id }"
        @click="activeTab = tab.id"
      >{{ tab.label }}</button>
    </div>

    <!-- Main content -->
    <main class="main">

      <!-- Profile header -->
      <section class="profile-header box">
        <div class="profile-left">
          <div class="avatar">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
              <circle cx="12" cy="7" r="4"/>
            </svg>
          </div>
          <div>
            <h2 class="profile-name">{{ userName }}</h2>
            <p class="profile-role">{{ userRole }} Explorer • Pro Tier</p>
          </div>
        </div>
        <button class="outline-btn" @click="goToProfile">
          EDIT PROFILE
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        </button>
      </section>

      <!-- Two-column grid -->
      <div class="grid">

        <!-- AI Insights -->
        <div class="col">
          <h3 class="section-title">AI Insights</h3>

          <div class="stat-row">
            <div class="box stat-card">
              <p class="stat-label">Efficiency</p>
              <p class="stat-value">94%</p>
            </div>
            <div class="box stat-card">
              <p class="stat-label">Path Credits</p>
              <p class="stat-value">1.2k</p>
            </div>
          </div>

          <div class="box activity-box">
            <div class="activity-top">
              <p class="activity-title">Activity Log</p>
              <button class="outline-btn small-btn">✦ Get Insight</button>
            </div>
            <div class="activity-list">
              <div v-for="i in 3" :key="i" class="activity-item">
                <div class="activity-dot"></div>
                <span>Path optimization computed for Sector {{ i * 7 }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Saved Paths -->
        <div class="col">
          <div class="paths-top">
            <h3 class="section-title">Saved Paths</h3>
            <button class="outline-btn small-btn">✦ Generate Path</button>
          </div>

          <div class="path-list">
            <div v-for="(path, idx) in savedPaths" :key="idx" class="box path-card">
              <div class="path-left">
                <div class="path-icon">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21"/><line x1="9" y1="3" x2="9" y2="18"/><line x1="15" y1="6" x2="15" y2="21"/></svg>
                </div>
                <div>
                  <p class="path-title">{{ path.title.toUpperCase() }}</p>
                  <p class="path-date">{{ path.date }}</p>
                </div>
              </div>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"/></svg>
            </div>
          </div>

          <button class="outline-btn archive-btn">
            VIEW ALL ARCHIVES
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          </button>
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
  --border:  2px solid var(--ink);
  --shadow:  4px 4px 0 var(--ink);

  min-height: 100vh;
  background: var(--bg);
  color: var(--ink);
  font-family: 'Segoe UI', sans-serif;
}

/* ── Sub-tab strip ──────────────────────────────────────────────────── */
.sub-tabs {
  display: flex;
  gap: 0;
  background: var(--surface);
  border-bottom: var(--border);
  padding: 0 28px;
}

.sub-tab {
  padding: 14px 22px;
  font-weight: 800;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  background: transparent;
  border: none;
  border-bottom: 3px solid transparent;
  cursor: pointer;
  color: var(--ink);
  margin-bottom: -2px;
  transition: color 0.1s, border-color 0.1s;
}
.sub-tab:hover { background: #f5f5f5; }
.sub-tab--active {
  border-bottom: 3px solid var(--ink);
  background: var(--accent);
}

/* ── Main content ───────────────────────────────────────────────────── */
.main {
  max-width: 1100px;
  width: 100%;
  margin: 0 auto;
  padding: 28px 28px 60px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* ── Shared ─────────────────────────────────────────────────────────── */
.box {
  background: var(--surface);
  border: var(--border);
  box-shadow: var(--shadow);
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
  transition: box-shadow 0.1s, transform 0.1s;
}
.outline-btn:hover  { background: #f5f5f5; }
.outline-btn:active { box-shadow: 1px 1px 0 var(--ink); transform: translate(2px,2px); }

.small-btn { padding: 5px 10px; font-size: 10px; box-shadow: 2px 2px 0 var(--ink); }

/* ── Profile header ─────────────────────────────────────────────────── */
.profile-header {
  padding: 20px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 16px;
}

.profile-left { display: flex; align-items: center; gap: 18px; }

.avatar {
  width: 72px; height: 72px;
  background: var(--accent);
  border: var(--border);
  box-shadow: var(--shadow);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}

.profile-name { font-size: 26px; font-weight: 900; letter-spacing: -0.5px; }
.profile-role { font-size: 13px; font-weight: 600; opacity: 0.65; font-style: italic; margin-top: 2px; }

/* ── Grid ───────────────────────────────────────────────────────────── */
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
.col  { display: flex; flex-direction: column; gap: 14px; }

.section-title {
  font-size: 18px; font-weight: 900; text-transform: uppercase;
  text-decoration: underline; text-underline-offset: 4px; text-decoration-thickness: 2px;
}

/* ── Stat cards ─────────────────────────────────────────────────────── */
.stat-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }

.stat-card { padding: 20px 16px; }
.stat-label { font-size: 10px; font-weight: 900; text-transform: uppercase; letter-spacing: 0.08em; opacity: 0.7; }
.stat-value { font-size: 36px; font-weight: 900; margin-top: 4px; }

/* ── Activity ───────────────────────────────────────────────────────── */
.activity-box { padding: 18px; flex: 1; display: flex; flex-direction: column; gap: 12px; }
.activity-top { display: flex; align-items: center; justify-content: space-between; }
.activity-title { font-weight: 900; font-size: 12px; text-transform: uppercase; letter-spacing: 0.06em; text-decoration: underline; text-underline-offset: 3px; }
.activity-list { display: flex; flex-direction: column; gap: 8px; }
.activity-item { display: flex; align-items: center; gap: 10px; padding: 10px 12px; border: var(--border); background: var(--surface); font-weight: 700; font-size: 12px; }
.activity-dot { width: 12px; height: 12px; background: var(--ink); flex-shrink: 0; }

/* ── Paths ──────────────────────────────────────────────────────────── */
.paths-top { display: flex; align-items: center; justify-content: space-between; }
.path-list { display: flex; flex-direction: column; gap: 10px; }
.path-card { padding: 14px 16px; display: flex; align-items: center; justify-content: space-between; cursor: pointer; transition: transform 0.12s; }
.path-card:hover { transform: translateX(3px); }
.path-left { display: flex; align-items: center; gap: 12px; }
.path-icon { padding: 6px; border: var(--border); display: flex; align-items: center; justify-content: center; }
.path-title { font-weight: 900; font-size: 12px; letter-spacing: 0.03em; }
.path-date  { font-size: 11px; font-weight: 600; opacity: 0.6; margin-top: 2px; }
.archive-btn { width: 100%; justify-content: center; padding: 16px; font-size: 13px; margin-top: auto; }

/* ── Responsive ─────────────────────────────────────────────────────── */
@media (max-width: 860px) {
  .grid { grid-template-columns: 1fr; }
  .main { padding: 16px; }
  .sub-tabs { padding: 0 12px; overflow-x: auto; }
}
</style>