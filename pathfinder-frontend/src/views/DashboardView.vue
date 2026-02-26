<template>
  <div class="p-5">
    <h1 class="fw-bold">Welcome to Pathfinder Dashboard</h1>
    <p>Role: {{ userRole }}</p>
    <button @click="logout" class="btn btn-danger">Logout</button>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
const router = useRouter();
const userRole = localStorage.getItem('role');

const logout = () => {
  localStorage.clear();
  router.push('/login');
};
</script>