<script setup>
import { computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';

const router = useRouter();
const route  = useRoute();

const userName = computed(() => localStorage.getItem('username') || 'Student');

const navLinks = [
  { label: 'Dashboard', to: '/dashboard' },
  { label: 'Placements', to: '/placement-drives' },
  { label: 'My Apps', to: '/my-applications' },
  { label: 'Profile', to: '/student/profile' },
];

const logout = () => {
  localStorage.clear();
  router.push('/login');
};
</script>

<template>
  <nav class="nb-nav sticky-top">
    <div class="container d-flex align-items-center justify-content-between py-2">
      <!-- Logo/Title -->
      <router-link class="nb-logo-link" to="/dashboard">
        <span class="nb-logo-text-small">Pathfinder.Ai</span>
      </router-link>

      <!-- Desktop Links -->
      <div class="d-none d-lg-flex align-items-center gap-4">
        <router-link 
          v-for="link in navLinks" 
          :key="link.to"
          class="nb-nav-link" 
          :to="link.to"
          :class="{ 'active': route.path === link.to }"
        >
          {{ link.label }}
        </router-link>
      </div>

      <!-- Right Side -->
      <div class="d-flex align-items-center gap-3">
        <span class="nb-user-badge d-none d-md-inline">{{ userName }}</span>
        <button class="nb-button nb-button-red small-btn" @click="logout">Logout</button>
      </div>
    </div>
  </nav>
</template>

<style scoped>
.nb-nav {
  background-color: #ffffff;
  border-bottom: 3px solid #323232;
  box-shadow: 0 4px #323232;
  z-index: 1000;
}
.nb-logo-link {
  text-decoration: none;
}
.nb-logo-text-small {
  font-size: 1.5rem;
  font-weight: 900;
  color: #323232;
  text-transform: uppercase;
}
.nb-nav-link {
  text-decoration: none;
  font-weight: 900;
  color: #323232;
  text-transform: uppercase;
  font-size: 0.9rem;
  padding: 5px 10px;
  border: 2px solid transparent;
  transition: all 0.2s;
}
.nb-nav-link:hover, .nb-nav-link.active {
  background: #2d8cf0;
  color: white;
  border-color: #323232;
  box-shadow: 3px 3px 0px #323232;
}
.nb-user-badge {
  font-weight: 600;
  border: 2px solid #323232;
  padding: 2px 10px;
  border-radius: 4px;
  background: #fdfd96; /* Pastel Yellow */
}
.nb-button-red {
  background-color: #ff5c5c;
  color: white;
}
.small-btn {
  height: 32px;
  padding: 0 12px;
  font-size: 14px;
}
</style>
