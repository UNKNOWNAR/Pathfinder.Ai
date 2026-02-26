<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const activeTab = ref('dashboard');

const userRole = localStorage.getItem('role') || 'Student';
const userName = localStorage.getItem('username') || 'Alex Rivera';

const logout = () => {
  localStorage.clear();
  router.push('/login');
};

const navItems = [
  { id: 'dashboard', label: 'Overview' },
  { id: 'paths',     label: 'My Paths' },
  { id: 'analytics', label: 'AI Analytics' },
  { id: 'settings',  label: 'Settings' },
];

const savedPaths = [
  { title: 'Software Engineering', date: 'Feb 24', color: '#FF90E8' },
  { title: 'Data Science Route',   date: 'Feb 22', color: '#76E4F7' },
  { title: 'Product Management',   date: 'Feb 20', color: '#FFDE03' },
];
</script>

<template>
  <div class="page">
    <div class="layout">

      <!-- ── Sidebar ─────────────────────────────────────────────── -->
      <aside class="sidebar">
        <div class="brand">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="currentColor"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
          <span>PATHFINDER</span>
        </div>

        <nav class="nav">
          <button
            v-for="item in navItems"
            :key="item.id"
            class="nav-btn"
            :class="{ 'nav-btn--active': activeTab === item.id }"
            @click="activeTab = item.id"
          >
            <!-- icons by tab -->
            <svg v-if="item.id === 'dashboard'" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>
            <svg v-if="item.id === 'paths'"     width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21"/><line x1="9" y1="3" x2="9" y2="18"/><line x1="15" y1="6" x2="15" y2="21"/></svg>
            <svg v-if="item.id === 'analytics'" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6"  y1="20" x2="6"  y2="14"/><line x1="2"  y1="20" x2="22" y2="20"/></svg>
            <svg v-if="item.id === 'settings'"  width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
            {{ item.label }}
          </button>
        </nav>

        <button class="logout-btn" @click="logout">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
          Logout
        </button>
      </aside>

      <!-- ── Main ──────────────────────────────────────────────────── -->
      <main class="main">

        <!-- Profile Header -->
        <section class="profile-header">
          <div class="profile-left">
            <div class="avatar">
              <svg width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
            </div>
            <div>
              <h2 class="profile-name">{{ userName }}</h2>
              <p class="profile-role">{{ userRole }} Explorer • Pro Tier</p>
            </div>
          </div>
          <button class="neo-btn edit-btn">
            Edit Profile
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          </button>
        </section>

        <!-- Grid -->
        <div class="grid">

          <!-- AI Insights Column -->
          <div class="col">
            <h3 class="section-title">AI Insights</h3>

            <div class="stat-row">
              <div class="stat-card" style="background:#4ade80;">
                <p class="stat-label">Efficiency</p>
                <p class="stat-value">94%</p>
              </div>
              <div class="stat-card" style="background:#fb923c;">
                <p class="stat-label">Path Credits</p>
                <p class="stat-value">1.2k</p>
              </div>
            </div>

            <div class="neo-box activity-box">
              <p class="activity-title">Activity Log</p>

              <div class="activity-list">
                <div v-for="i in 3" :key="i" class="activity-item">
                  <div class="activity-dot"></div>
                  <p>Path optimization computed for Sector {{ i * 7 }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Saved Paths Column -->
          <div class="col">
            <div class="paths-header">
              <h3 class="section-title">Saved Paths</h3>
            </div>

            <div class="path-list">
              <div
                v-for="(path, idx) in savedPaths"
                :key="idx"
                class="path-card neo-box"
                :style="{ background: path.color }"
              >
                <div class="path-left">
                  <div class="path-icon">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21"/><line x1="9" y1="3" x2="9" y2="18"/><line x1="15" y1="6" x2="15" y2="21"/></svg>
                  </div>
                  <div>
                    <p class="path-title">{{ path.title }}</p>
                    <p class="path-date">{{ path.date }}</p>
                  </div>
                </div>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="9 18 15 12 9 6"/></svg>
              </div>
            </div>

            <button class="neo-btn archive-btn">
              View All Archives
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
            </button>
          </div>

        </div>
      </main>
    </div>

  </div>
</template>

<style scoped>
/* ── Reset / Base ─────────────────────────────────────────────────── */
* { box-sizing: border-box; margin: 0; padding: 0; }

.page {
  min-height: 100vh;
  background: #F0F0F0;
  color: #111;
  font-family: 'Segoe UI', sans-serif;
  padding: 24px;
}

/* ── Layout ────────────────────────────────────────────────────────── */
.layout {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  gap: 28px;
}

/* ── Neo-Brutalist util ─────────────────────────────────────────────── */
.neo-box {
  background: #fff;
  border: 3px solid #111;
  box-shadow: 5px 5px 0 #111;
}

.neo-btn {
  border: 3px solid #111;
  box-shadow: 4px 4px 0 #111;
  cursor: pointer;
  font-weight: 900;
  font-size: 13px;
  text-transform: uppercase;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: box-shadow 0.1s, transform 0.1s;
  letter-spacing: 0.03em;
  background: #fff;
  color: #111;
}
.neo-btn:active:not(:disabled) {
  box-shadow: 1px 1px 0 #111;
  transform: translate(3px, 3px);
}
.neo-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ── Sidebar ────────────────────────────────────────────────────────── */
.sidebar {
  width: 220px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.brand {
  background: #3B82F6;
  color: #fff;
  border: 3px solid #111;
  box-shadow: 5px 5px 0 #111;
  padding: 18px 16px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 20px;
  font-weight: 900;
  font-style: italic;
  letter-spacing: -0.5px;
}

.nav {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.nav-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  border: 3px solid #111;
  box-shadow: 4px 4px 0 #111;
  background: #fff;
  font-weight: 900;
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  cursor: pointer;
  transition: background 0.15s, box-shadow 0.1s, transform 0.1s;
  text-align: left;
}
.nav-btn:hover { background: #f5f5f5; }
.nav-btn:active {
  box-shadow: 1px 1px 0 #111;
  transform: translate(3px, 3px);
}
.nav-btn--active {
  background: #FFDE03 !important;
}

.logout-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  border: 3px solid #111;
  box-shadow: 4px 4px 0 #111;
  background: #f87171;
  font-weight: 900;
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  cursor: pointer;
  margin-top: auto;
  transition: box-shadow 0.1s, transform 0.1s;
}
.logout-btn:hover { background: #ef4444; }
.logout-btn:active {
  box-shadow: 1px 1px 0 #111;
  transform: translate(3px, 3px);
}

/* ── Main ────────────────────────────────────────────────────────────── */
.main {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* ── Profile Header ──────────────────────────────────────────────────── */
.profile-header {
  background: #A5B4FC;
  border: 3px solid #111;
  box-shadow: 5px 5px 0 #111;
  padding: 28px 32px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  flex-wrap: wrap;
}

.profile-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.avatar {
  width: 88px;
  height: 88px;
  background: #FFDE03;
  border: 3px solid #111;
  box-shadow: 4px 4px 0 #111;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.profile-name {
  font-size: 32px;
  font-weight: 900;
  text-transform: uppercase;
  line-height: 1.1;
}

.profile-role {
  font-size: 15px;
  font-weight: 700;
  opacity: 0.75;
  font-style: italic;
  margin-top: 4px;
}

.edit-btn {
  padding: 14px 28px;
  font-size: 15px;
}
.edit-btn:hover { background: #f5f5f5; }

/* ── Grid ──────────────────────────────────────────────────────────── */
.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.col {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.section-title {
  font-size: 20px;
  font-weight: 900;
  text-transform: uppercase;
  text-decoration: underline;
  text-underline-offset: 5px;
  text-decoration-thickness: 3px;
}

/* ── Stat Cards ─────────────────────────────────────────────────────── */
.stat-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.stat-card {
  border: 3px solid #111;
  box-shadow: 4px 4px 0 #111;
  padding: 22px 18px;
}

.stat-label {
  font-size: 11px;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.stat-value {
  font-size: 38px;
  font-weight: 900;
  margin-top: 6px;
}

/* ── Activity Box ─────────────────────────────────────────────────────── */
.activity-box {
  padding: 20px;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.activity-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.activity-title {
  font-weight: 900;
  text-transform: uppercase;
  font-size: 13px;
  text-decoration: underline;
  text-underline-offset: 3px;
}

.insight-btn {
  background: #FF90E8;
  padding: 6px 12px;
  font-size: 11px;
}
.insight-btn:hover { background: #f472d0; }

.insight-result {
  padding: 12px 14px;
  background: #fef9c3;
  border: 2px dashed #111;
  font-weight: 700;
  font-style: italic;
  font-size: 13px;
  line-height: 1.5;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border: 2px solid #111;
  background: #f9f9f9;
  font-weight: 700;
  font-size: 13px;
}

.activity-dot {
  width: 14px;
  height: 14px;
  background: #2563eb;
  border: 2px solid #111;
  flex-shrink: 0;
}

/* ── Paths Column ────────────────────────────────────────────────────── */
.paths-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.gen-btn {
  background: #76E4F7;
  padding: 8px 14px;
}
.gen-btn:hover { background: #38bdf8; }

.path-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.path-card {
  padding: 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  transition: transform 0.15s;
}
.path-card:hover { transform: translateX(4px); }

.path-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.path-icon {
  padding: 8px;
  background: #fff;
  border: 2px solid #111;
  display: flex;
  align-items: center;
  justify-content: center;
}

.path-title {
  font-weight: 900;
  text-transform: uppercase;
  font-size: 13px;
}

.path-date {
  font-size: 11px;
  font-weight: 700;
  opacity: 0.7;
  margin-top: 2px;
}

.archive-btn {
  padding: 18px;
  justify-content: center;
  font-size: 14px;
  margin-top: auto;
}
.archive-btn:hover { background: #f5f5f5; }

/* ── Modal ──────────────────────────────────────────────────────────── */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  z-index: 100;
}

.modal {
  width: 100%;
  max-width: 520px;
  padding: 36px;
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 18px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-close {
  position: absolute;
  top: 14px;
  right: 14px;
  background: none;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  transition: transform 0.15s;
}
.modal-close:hover { transform: scale(1.15); }

.modal-title-row {
  display: flex;
  align-items: center;
  gap: 14px;
}

.modal-icon {
  padding: 10px;
  background: #FFDE03;
  border: 3px solid #111;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-title {
  font-size: 26px;
  font-weight: 900;
  text-transform: uppercase;
  font-style: italic;
}

.modal-hint {
  font-weight: 700;
  font-size: 14px;
  line-height: 1.5;
}

.modal-textarea {
  width: 100%;
  height: 120px;
  padding: 14px;
  border: 3px solid #111;
  background: #fff;
  font-size: 14px;
  font-weight: 700;
  font-family: inherit;
  resize: none;
  outline: none;
  transition: background 0.2s;
}
.modal-textarea:focus { background: #fef9c3; }

.plan-btn {
  width: 100%;
  justify-content: center;
  padding: 16px;
  background: #3B82F6;
  color: #fff;
  font-size: 17px;
  border-color: #111;
}
.plan-btn:hover:not(:disabled) { background: #2563eb; }

.ai-result {
  padding: 20px;
  border: 3px solid #111;
  background: #f9f9f9;
  box-shadow: 4px 4px 0 #111;
  max-height: 180px;
  overflow-y: auto;
}

.ai-result-label {
  font-size: 10px;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: #2563eb;
  margin-bottom: 10px;
}

.ai-result-text {
  font-weight: 700;
  line-height: 1.7;
  font-size: 14px;
  white-space: pre-wrap;
}

/* ── Animations ─────────────────────────────────────────────────────── */
@keyframes spin { 100% { transform: rotate(360deg); } }
.spin { animation: spin 0.8s linear infinite; }

.fade-enter-active, .fade-leave-active { transition: opacity 0.25s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.slide-enter-active { transition: all 0.3s ease; }
.slide-enter-from { opacity: 0; transform: translateY(-10px); }

/* ── Responsive ─────────────────────────────────────────────────────── */
@media (max-width: 900px) {
  .layout { flex-direction: column; }
  .sidebar { width: 100%; flex-direction: row; flex-wrap: wrap; }
  .nav { flex-direction: row; flex-wrap: wrap; }
  .grid { grid-template-columns: 1fr; }
}
</style>