<template>
  <div class="main-wrapper">
    <CompanyNavBar />

    <main class="container py-5">
      <div class="nb-header mb-5">
        <div>
          <h1 class="nb-title">My Placement Drives</h1>
          <p class="nb-subtitle">Manage your live active recruitment roles.</p>
        </div>
        <router-link to="/company/create-drive" class="nb-button nb-button-blue" style="text-decoration: none;">
          + Create New Drive
        </router-link>
      </div>

      <div v-if="!loaded" class="text-center py-5">
        <div class="nb-card p-5">Loading placement drives...</div>
      </div>

      <div v-else-if="drives.length === 0" class="nb-card py-5 text-center">
        <h3 class="nb-cell-bold" style="font-size: 1.5rem;">No drives posted yet! 💨</h3>
        <p class="nb-subtitle mt-2 mb-4">Start by posting your first placement drive.</p>
        <router-link to="/company/create-drive" class="nb-button nb-button-blue" style="text-decoration: none;">Post My First Drive</router-link>
      </div>

      <div v-else class="nb-card overflow-hidden p-0">
        <div class="table-responsive">
          <table class="nb-table mb-0">
            <thead>
              <tr>
                <th class="ps-4">Job Title</th>
                <th>Min. CGPA</th>
                <th>Status</th>
                <th class="text-end pe-4">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="drive in drives" :key="drive.drive_id">
                <td class="ps-4">
                  <span class="nb-cell-bold d-block">{{ drive.job_title }}</span>
                  <small class="nb-subtitle" style="font-size: 0.8rem;">ID: #{{ drive.drive_id }}</small>
                </td>
                <td class="nb-cell-bold">{{ drive.cgpa_required }}</td>
                <td>
                  <span :class="['nb-badge', getStatusBadge(drive.status)]">{{ drive.status }}</span>
                </td>
                <td class="text-end pe-4">
                  <div class="d-flex justify-content-end gap-2">
                    <router-link :to="{ path: '/company/applicants', query: { driveId: drive.drive_id } }" class="nb-button small-btn nb-button-blue" style="text-decoration: none;">
                      Drive Details
                    </router-link>
                    <button class="nb-button small-btn" @click="exportApplicants(drive.drive_id)">
                      📧 CSV
                    </button>
                    <button class="nb-button small-btn nb-button-red" @click="deleteDrive(drive.drive_id)">
                      Delete
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
import CompanyNavBar from '@/components/CompanyNavBar.vue';
import api from '@/services/api';

const drives = ref([]);
const loaded = ref(false);

const loadDrives = async () => {
  try {
    const res = await api.get('/company/drive');
    drives.value = res.data;
    loaded.value = true;
  } catch (err) {
    console.error('[ERROR]', err);
    loaded.value = true;
  }
};

const deleteDrive = async (id) => {
  if (confirm('Delete this drive?')) {
    try {
      await api.delete(`/company/drive/${id}`);
      loadDrives();
    } catch (err) {
      alert('Failed to delete.');
    }
  }
};

const exportApplicants = async (driveId) => {
  try {
    const res = await api.get(`/company/export/drive/${driveId}`);
    alert(res.data.message);
  } catch (err) {
    alert('Export failed.');
  }
};

const getStatusBadge = (status) => {
  if (status === 'approved') return 'nb-badge-green';
  if (status === 'pending') return 'nb-badge-yellow';
  return 'nb-badge-gray';
};

onMounted(() => { loadDrives(); });
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

.nb-badge-gray { background: #e0e0e0; border: 2px solid #323232; color: #323232; }
.nb-badge-green  { background: #58cc02; color: white; border: 2px solid #323232; }
.nb-badge-yellow { background: #fdfd96; color: #323232; border: 2px solid #323232; }

.nb-button-red   { background-color: #ff5c5c; color: white; }

.small-btn {
  height: 32px;
  padding: 0 15px;
  font-size: 14px;
}
</style>
