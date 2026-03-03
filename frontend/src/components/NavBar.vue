<script setup>
import { computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import logoImg from '@/assets/logo.png';

const router = useRouter();
const route  = useRoute();

const userName = computed(() => localStorage.getItem('username') || 'User');
const isAdmin  = computed(() => localStorage.getItem('role') === 'admin');
const isCompany = computed(() => localStorage.getItem('role') === 'company');

const studentLinks = [
  { label: 'Jobs',      to: '/jobs'      },
  { label: 'LeetCode',  to: '/leetcode'  },
  { label: 'Interview', to: '/interview' },
  { label: 'Profile',   to: '/profile'   },
];

const adminLinks = [
  { label: 'Dashboard',  to: '/admin' },
  { label: 'Harvesters',   to: '/admin/harvesters' },
  { label: 'Jobs DB',      to: '/admin/jobs' },
  { label: 'Companies',    to: '/admin/companies' },
];

const companyLinks = [
  { label: 'Dashboard', to: '/company' }
];

const navLinks = computed(() => {
  if (isAdmin.value) return adminLinks;
  if (isCompany.value) return companyLinks;
  return studentLinks;
});

const isActive = (path) => {
  if (path === '/admin') return route.path === '/admin';
  return route.path.startsWith(path);
};

const logout = () => {
  localStorage.clear();
  router.push('/login');
};
</script>

<template>
  <header class="navbar">
    <!-- Left: Logo + name -->
    <div class="navbar-brand" @click="router.push(isAdmin ? '/admin' : isCompany ? '/company' : '/jobs')">
      <img :src="logoImg" class="nav-logo" alt="Pathfinder logo" />
      <span class="nav-title">Pathfinder.Ai</span>
    </div>

    <!-- Center: Page links -->
    <nav class="navbar-links">
      <button
        v-for="link in navLinks"
        :key="link.to"
        class="nav-link"
        :class="[
          { 'nav-link--active': isActive(link.to) },
          isAdmin ? 'admin-nav-link' : ''
        ]"
        @click="router.push(link.to)"
      >
        {{ link.label }}
      </button>
    </nav>

    <div class="navbar-right">
      <span class="nav-user">{{ userName }}</span>
      <button class="nav-logout" @click="logout">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
          <polyline points="16 17 21 12 16 7"/>
          <line x1="21" y1="12" x2="9" y2="12"/>
        </svg>
        Logout
      </button>
    </div>
  </header>
</template>

<style scoped>
.navbar {
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 28px;
  height: 68px;
  background: #fff;
  border-bottom: 2px solid #111;
  box-shadow: 0 4px 0 #111;
  gap: 24px;
}

/* ── Brand ─────────────────────────────────────────────── */
.navbar-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  flex-shrink: 0;
}

.nav-logo {
  height: 48px;
  width: 48px;
  object-fit: contain;
  flex-shrink: 0;
}

.nav-title {
  font-weight: 900;
  font-size: 18px;
  letter-spacing: -0.4px;
  white-space: nowrap;
}

/* ── Nav links ─────────────────────────────────────────── */
.navbar-links {
  display: flex;
  align-items: center;
  gap: 6px;
  flex: 1;
  justify-content: flex-end;
}

.nav-link {
  padding: 8px 20px;
  font-weight: 800;
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  background: transparent;
  border: 2px solid transparent;
  cursor: pointer;
  color: #111;
  transition: background 0.1s, border-color 0.1s, box-shadow 0.1s, transform 0.1s;
}
.nav-link:hover {
  background: #f5f5f5;
  border-color: #111;
}
.nav-link:active {
  box-shadow: 2px 2px 0 #111;
  transform: translate(2px, 2px);
}
.nav-link--active {
  background: #2d8cf0;
  color: #fff;
  border: 2px solid #111;
  box-shadow: 3px 3px 0 #111;
}

.admin-nav-link.nav-link--active {
  background: #ff4757; /* Red admin accent */
}

/* ── Right ─────────────────────────────────────────────── */
.navbar-right {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-shrink: 0;
}

.nav-user {
  font-weight: 800;
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  opacity: 0.75;
}

.nav-logout {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: #fff;
  border: 2px solid #111;
  box-shadow: 3px 3px 0 #111;
  font-weight: 800;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  cursor: pointer;
  color: #111;
  transition: box-shadow 0.1s, transform 0.1s;
}
.nav-logout:hover  { background: #f5f5f5; }
.nav-logout:active { box-shadow: 1px 1px 0 #111; transform: translate(2px, 2px); }

/* ── Responsive ────────────────────────────────────────── */
@media (max-width: 640px) {
  .navbar { padding: 0 16px; height: auto; flex-wrap: wrap; padding: 10px 16px; gap: 10px; }
  .navbar-links { order: 3; width: 100%; justify-content: flex-start; flex-wrap: wrap; }
  .nav-user { display: none; }
}
</style>
