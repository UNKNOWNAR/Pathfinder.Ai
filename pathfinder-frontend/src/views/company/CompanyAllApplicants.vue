<template>
  <div class="main-wrapper">
    <CompanyNavBar />

    <main class="container py-5">
      <div class="nb-header mb-5">
        <div>
          <h1 class="nb-title">{{ pageTitle }}</h1>
          <p class="nb-subtitle">{{ pageSubtitle }}</p>
        </div>
      </div>

      <div v-if="!loaded" class="text-center py-5">
        <div class="nb-card p-5">Loading applicant data...</div>
      </div>

      <div v-else-if="applicants.length === 0" class="nb-card py-5 text-center">
        <h3 class="nb-cell-bold" style="font-size: 1.5rem;">No applicants yet! ⌛</h3>
        <p class="nb-subtitle mt-2 mb-4">Students who meet your criteria will appear here once they apply.</p>
      </div>

      <div v-else class="nb-card overflow-hidden p-0">
        <div class="table-responsive">
          <table class="nb-table mb-0">
            <thead>
              <tr>
                <th class="ps-4">Date</th>
                <th>Student Name</th>
                <th>Applied Position</th>
                <th>Application Status</th>
                <th class="text-end pe-4">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="app in filteredApplicants" :key="app.application_id">
                <td class="ps-4 font-monospace nb-subtitle" style="font-size: 0.9rem;">
                  {{ new Date(app.date).toLocaleDateString() }}
                </td>
                <td class="nb-cell-bold text-blue">{{ app.student_name }}</td>
                <td>{{ app.job_title }}</td>
                <td>
                  <span :class="['nb-badge', getStatusBadge(app.status)]">{{ app.status }}</span>
                </td>
                <td class="text-end pe-4">
                  <div class="d-flex justify-content-end gap-2">
                    <button 
                      class="nb-button small-btn" style="background-color: #fdfd96; color: #323232;"
                      @click="updateStatus(app.application_id, 'Shortlisted')"
                    >
                      Shortlist
                    </button>
                    <button 
                      class="nb-button small-btn nb-button-green" 
                      @click="updateStatus(app.application_id, 'Selected')"
                    >
                      Select
                    </button>
                    <button 
                      class="nb-button small-btn nb-button-red" 
                      @click="updateStatus(app.application_id, 'Rejected')"
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
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import CompanyNavBar from '@/components/CompanyNavBar.vue';
import api from '@/services/api';

const route = useRoute();

const applicants = ref([]);
const loaded = ref(false);

const filteredApplicants = computed(() => {
  const driveId = route.query.driveId;
  if (!driveId) return applicants.value;
  return applicants.value.filter(a => String(a.drive_id) === String(driveId));
});

const pageTitle = computed(() => {
  if (route.query.driveId && filteredApplicants.value.length > 0) {
    return `Applicants for ${filteredApplicants.value[0].job_title}`;
  }
  return 'All Applicants';
});

const pageSubtitle = computed(() => {
  if (route.query.driveId) {
    return 'Detailed view of candidates for this specific recruitment drive.';
  }
  return 'Review applications across all your active placement drives.';
});

const loadApplicants = async () => {
  try {
    const res = await api.get('/company/applicants');
    applicants.value = res.data.applicants;
    loaded.value = true;
  } catch (err) {
    console.error('[ERROR]', err);
    loaded.value = true;
  }
};

const updateStatus = async (appId, newStatus) => {
  try {
    await api.put(`/company/application/${appId}`, { status: newStatus });
    // Update local state smoothly
    const app = applicants.value.find(a => a.application_id === appId);
    if (app) app.status = newStatus;
  } catch (err) {
    alert('Failed to update status');
    loadApplicants(); // Revert
  }
};

const getStatusBadge = (status) => {
  const s = status.toLowerCase();
  if (s === 'selected') return 'nb-badge-green';
  if (s === 'rejected') return 'nb-badge-red';
  if (s === 'shortlisted') return 'nb-badge-yellow';
  return 'nb-badge-gray';
};

onMounted(() => { loadApplicants(); });
</script>

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
.text-blue { color: #2d8cf0; }

.nb-badge-gray   { background: #e0e0e0; border: 2px solid #323232; color: #323232; }
.nb-badge-green  { background: #58cc02; color: white; border: 2px solid #323232; }
.nb-badge-yellow { background: #fdfd96; color: #323232; border: 2px solid #323232; }
.nb-badge-red    { background: #ff5c5c; color: white; border: 2px solid #323232; }
.nb-button-green { background-color: #58cc02; color: white; }
.nb-button-red   { background-color: #ff5c5c; color: white; }

.small-btn {
  height: 32px;
  padding: 0 15px;
  font-size: 14px;
}
.font-monospace { font-family: monospace; }
</style>
