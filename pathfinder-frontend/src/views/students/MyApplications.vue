<script setup>
import { ref, onMounted } from 'vue';
import StudentNavBar from '@/components/StudentNavBar.vue';
import api from '@/services/api';

const applications = ref([]);
const loaded = ref(false);

const loadHistory = async () => {
  try {
    const res = await api.get('/student/applications');
    applications.value = res.data;
    loaded.value = true;
  } catch (err) {
    console.error('[ERROR] Failed to load tracking history:', err);
    loaded.value = true;
  }
};

const getStatusBadge = (status) => {
  const s = status.toLowerCase();
  if (s === 'selected') return 'nb-badge-green';
  if (s === 'rejected') return 'nb-badge-red';
  if (s === 'shortlisted') return 'nb-badge-yellow';
  return 'nb-badge-blue';
};

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString('en-IN', {
    day: 'numeric', month: 'short', year: 'numeric'
  });
};

onMounted(() => {
  loadHistory();
});
</script>

<template>
  <div class="main-wrapper">
    <StudentNavBar />
    
    <main class="container py-5">
      <div class="nb-header mb-5">
        <div>
          <h1 class="nb-title">My Applications</h1>
          <p class="nb-subtitle">Track the progress of your submitted placement applications.</p>
        </div>
      </div>

      <div v-if="!loaded" class="text-center py-5">
        <div class="nb-card p-5">Loading your applications...</div>
      </div>

      <div v-else-if="applications.length === 0" class="nb-card p-5 text-center">
        <h2 class="nb-cell-bold mb-2">No applications found.</h2>
        <p class="nb-subtitle mb-4">Explore the drives list to start your recruitment journey.</p>
        <router-link to="/placement-drives" class="nb-button nb-button-blue" style="text-decoration: none;">Browse Drives</router-link>
      </div>

      <div v-else class="nb-card overflow-hidden p-0">
        <div class="table-responsive">
          <table class="nb-table mb-0">
            <thead>
              <tr>
                <th class="ps-4">Applied Date</th>
                <th>Company</th>
                <th>Job Role</th>
                <th class="pe-4 text-center">Current Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="app in applications" :key="app.application_id">
                <td class="ps-4 font-monospace nb-subtitle" style="font-size: 0.9rem;">{{ formatDate(app.date) }}</td>
                <td class="nb-cell-bold">{{ app.company_name }}</td>
                <td>{{ app.job_title }}</td>
                <td class="pe-4 text-center">
                  <span :class="['nb-badge', getStatusBadge(app.status)]">
                    {{ app.status.toUpperCase() }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.main-wrapper {
  background-color: var(--main-bg);
  min-height: 100vh;
}
.nb-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
}
.nb-title { font-size: 2.5rem; font-weight: 900; margin: 0; }
.nb-subtitle { font-weight: 600; color: #666; font-size: 1.1rem; }

.nb-table {
  width: 100%;
  border-collapse: collapse;
}
.nb-table thead {
  background-color: #323232;
  color: white;
}
.nb-table th {
  padding: 15px 10px;
  text-transform: uppercase;
  font-weight: 900;
  font-size: 13px;
  text-align: left;
}
.nb-table td {
  padding: 12px 10px;
  border-bottom: 2px solid #323232;
  font-weight: 600;
}
.nb-cell-bold { font-weight: 900; color: #323232; }

.nb-badge-green  { background: #58cc02; color: white; border: 2px solid #323232; }
.nb-badge-red    { background: #ff5c5c; color: white; border: 2px solid #323232; }
.nb-badge-yellow { background: #fdfd96; color: #323232; border: 2px solid #323232; }
.nb-badge-blue   { background: #2d8cf0; color: white; border: 2px solid #323232; }

.font-monospace {
  font-family: monospace;
}
</style>
