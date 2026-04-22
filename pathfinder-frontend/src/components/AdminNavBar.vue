<template>
  <nav class="nb-nav sticky-top">
    <div class="container d-flex align-items-center justify-content-between py-2">
      <!-- Logo/Title -->
      <router-link class="nb-logo-link" to="/admin/dashboard">
        <span class="nb-logo-text-small">Admin Panel</span>
      </router-link>

      <!-- Desktop Links -->
      <div class="d-none d-lg-flex align-items-center gap-4">
        <router-link class="nb-nav-link" to="/admin/dashboard">Reports</router-link>
        <router-link class="nb-nav-link" to="/admin/companies">Approvals</router-link>
        <router-link class="nb-nav-link" to="/admin/placement-drives">Drives</router-link>
        <router-link class="nb-nav-link" to="/admin/students">Students</router-link>
      </div>

      <!-- Right Side -->
      <div class="d-flex align-items-center gap-3">
        <button class="nb-button nb-button-red small-btn" @click="logout">Logout</button>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { useRouter } from 'vue-router';

const router = useRouter();

const logout = () => {
  localStorage.clear();
  router.push('/login');
};
</script>

<style scoped>
.nb-nav {
  background-color: #2d8cf0; /* Admin blue */
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
  color: white;
  text-shadow: 2px 2px 0px #323232;
  text-transform: uppercase;
}
.nb-nav-link {
  text-decoration: none;
  font-weight: 900;
  color: white;
  text-transform: uppercase;
  font-size: 0.9rem;
  padding: 5px 10px;
  border: 2px solid transparent;
  transition: all 0.2s;
}
.nb-nav-link:hover, .nb-nav-link.router-link-active {
  background: white;
  color: #323232;
  border-color: #323232;
  box-shadow: 3px 3px 0px #323232;
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