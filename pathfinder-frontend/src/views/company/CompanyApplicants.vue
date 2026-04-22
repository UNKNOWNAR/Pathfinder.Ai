<template>
  <div class="main-wrapper">
    <CompanyNavBar />

    <main class="container py-5">
      <div class="mb-5">
        <router-link to="/company/dashboard" class="nb-subtitle" style="text-decoration: none; font-size: 0.95rem;">← Back to Dashboard</router-link>
        <h1 class="nb-title mt-2">Drive Applicants</h1>
        <p class="nb-subtitle">Review students and manage their selection status.</p>
      </div>

      <!-- Loading State -->
      <div v-if="!loaded" class="text-center py-5">
        <div class="nb-card p-5">Loading applications...</div>
      </div>

      <!-- Empty State -->
      <div v-else-if="applicants.length === 0" class="nb-card py-5 text-center">
        <h3 class="nb-cell-bold" style="font-size: 1.5rem;">No applications yet! ⏳</h3>
        <p class="nb-subtitle">Students who meet your criteria will appear here once they apply.</p>
      </div>

      <!-- Applicants Table -->
      <div v-else class="nb-card overflow-hidden p-0">
        <div class="table-responsive">
          <table class="nb-table mb-0">
            <thead>
              <tr>
                <th class="ps-4">Student Name</th>
                <th>Applied Date</th>
                <th>Current Status</th>
                <th class="text-end pe-4">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="app in applicants" :key="app.application_id">
                <td class="ps-4">
                  <span class="nb-cell-bold">{{ app.student_name }}</span>
                </td>
                <td class="nb-subtitle font-monospace" style="font-size: 0.85rem;">
                  {{ new Date(app.date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }) }}
                </td>
                <td>
                  <span :class="['nb-badge', getBadgeClass(app.status)]">{{ app.status.toUpperCase() }}</span>
                </td>
                <td class="text-end pe-4">
                  <div class="d-flex justify-content-end gap-2">
                    <button 
                      class="nb-button small-btn" style="background-color: #fdfd96; color: #323232;"
                      @click="updateStatus(app.application_id, 'shortlisted')"
                    >
                      Shortlist
                    </button>
                    <button 
                      class="nb-button small-btn nb-button-green" 
                      @click="updateStatus(app.application_id, 'selected')"
                    >
                      Select
                    </button>
                    <button 
                      class="nb-button small-btn nb-button-red" 
                      @click="updateStatus(app.application_id, 'rejected')"
                    >
                      Reject
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import CompanyNavBar from '@/components/CompanyNavBar.vue';
import api from '@/services/api';

const route = useRoute();
const applicants = ref([]);
const loaded = ref(false);
const driveId = route.params.id;

const loadApplicants = async () => {
  try {
    const res = await api.get(`/company/drive/${driveId}`);
    applicants.value = res.data.applicants;
    loaded.value = true;
  } catch (err) {
    console.error('[ERROR] Failed to load applicants:', err);
    loaded.value = true;
  }
};

const updateStatus = async (appId, status) => {
  try {
    await api.put(`/company/application/${appId}`, { status });
    loadApplicants(); // Refresh list
  } catch (err) {
    alert('Failed to update status.');
  }
};

const getBadgeClass = (status) => {
  const s = status.toLowerCase();
  if (s === 'selected') return 'nb-badge-green';
  if (s === 'rejected') return 'nb-badge-red';
  if (s === 'shortlisted') return 'nb-badge-yellow';
  return 'nb-badge-blue';
};

onMounted(() => {
  loadApplicants();
});
</script>

<style scoped>
.main-wrapper {
  background-color: var(--main-bg);
  min-height: 100vh;
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

.nb-button-red   { background-color: #ff5c5c; color: white; }
.nb-button-green { background-color: #58cc02; color: white; }

.small-btn {
  height: 32px;
  padding: 0 15px;
  font-size: 14px;
}
.font-monospace {
  font-family: inherit;
}
</style>
