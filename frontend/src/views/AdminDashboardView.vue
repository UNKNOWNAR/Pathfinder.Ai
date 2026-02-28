<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const username = ref(localStorage.getItem('username') || 'Admin');
</script>

<template>
  <div class="admin-wrapper">
    <div class="admin-header">
      <h1 class="admin-title">Admin Dashboard</h1>
      <span class="admin-badge">ADMIN</span>
    </div>

    <div class="admin-grid">
      <div class="admin-card">
        <div class="card-label">Logged in as</div>
        <div class="card-value">{{ username }}</div>
      </div>

      <div class="admin-card">
        <div class="card-label">Role</div>
        <div class="card-value">Administrator</div>
      </div>

      <div class="admin-card admin-card--wide">
        <div class="card-label">Harvester Engine</div>
        <div class="card-value card-value--muted">Coming soon — Task 8</div>
      </div>
    </div>

    <button class="back-btn" @click="router.push('/dashboard')">← Back to Dashboard</button>
  </div>
</template>

<style scoped>
.admin-wrapper {
  padding: 40px;
  min-height: 100vh;
  background: #e8e8e8;
}

.admin-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 36px;
}

.admin-title {
  font-size: 32px;
  font-weight: 900;
  color: #111;
  margin: 0;
}

.admin-badge {
  padding: 4px 12px;
  background: #111;
  color: #fff;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.1em;
  border: 2px solid #111;
  box-shadow: 3px 3px 0 #555;
}

.admin-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.admin-card {
  background: #fff;
  border: 2px solid #111;
  box-shadow: 5px 5px 0 #111;
  padding: 24px;
}

.admin-card--wide {
  grid-column: 1 / -1;
}

.card-label {
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #777;
  margin-bottom: 8px;
}

.card-value {
  font-size: 20px;
  font-weight: 900;
  color: #111;
}

.card-value--muted {
  color: #aaa;
  font-size: 16px;
}

.back-btn {
  padding: 10px 24px;
  background: #fff;
  border: 2px solid #111;
  box-shadow: 4px 4px 0 #111;
  font-size: 14px;
  font-weight: 800;
  cursor: pointer;
  transition: box-shadow 0.1s, transform 0.1s;
}

.back-btn:active {
  box-shadow: 1px 1px 0 #111;
  transform: translate(3px, 3px);
}
</style>
