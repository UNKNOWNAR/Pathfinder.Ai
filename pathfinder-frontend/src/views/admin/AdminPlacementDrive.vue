<template>
  <div class="main-wrapper">
    <AdminNavBar />

    <main class="container py-5">
      <div class="nb-header mb-5">
        <div>
          <h1 class="nb-title">Placement Drives</h1>
          <p class="nb-subtitle">Review and authorize job postings from companies.</p>
        </div>
      </div>

      <div v-if="!loaded" class="text-center py-5">
        <div class="nb-card p-5">Loading placement drives...</div>
      </div>

      <div v-else-if="drives.length === 0" class="nb-card p-5 text-center">
        <h3 class="nb-cell-bold" style="font-size: 1.5rem;">No drives to review! ✅</h3>
        <p class="nb-subtitle mt-2">All submitted placement drives have been processed.</p>
      </div>

      <div v-else class="nb-card overflow-hidden p-0">
        <div class="table-responsive">
          <table class="nb-table mb-0">
            <thead>
              <tr>
                <th class="ps-4">Company</th>
                <th>Role</th>
                <th>Min CGPA</th>
                <th>Branch</th>
                <th>Deadline</th>
                <th>Status</th>
                <th class="pe-4">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="drive in drives" :key="drive.drive_id">
                <td class="ps-4 nb-cell-bold">{{ drive.company_name }}</td>
                <td>{{ drive.job_title }}</td>
                <td class="nb-cell-bold">{{ drive.cgpa_required }}</td>
                <td>
                  <span class="nb-badge nb-badge-gray">{{ drive.eligible_branch || 'Any' }}</span>
                </td>
                <td class="nb-cell-bold">{{ formatDate(drive.application_deadline) }}</td>
                <td>
                  <span :class="['nb-badge', statusBadge(drive.status)]">
                    {{ drive.status.toUpperCase() }}
                  </span>
                </td>
                <td class="pe-4">
                  <div class="d-flex gap-2" v-if="drive.status === 'pending'">
                    <button class="nb-button small-btn nb-button-green" @click="setStatus(drive.drive_id, 'approved')">Approve</button>
                    <button class="nb-button small-btn nb-button-red" @click="setStatus(drive.drive_id, 'rejected')">Reject</button>
                  </div>
                  <span v-else class="nb-badge nb-badge-gray">Processed</span>
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
import AdminNavBar from '@/components/AdminNavBar.vue';
import api from '@/services/api';

const drives = ref([]);
const loaded = ref(false);

const loadDrives = async () => {
  try {
    const res = await api.get('/admin/all-drives');
    drives.value = res.data;
    loaded.value = true;
  } catch (err) {
    console.error('[ERROR] Failed to load all drives:', err);
    loaded.value = true;
  }
};

const setStatus = async (id, status) => {
  try {
    await api.patch(`/admin/drive/${id}`, { status });
    loadDrives();
  } catch (err) {
    alert('Action failed.');
  }
};

const statusBadge = (status) => {
  if (status === 'approved') return 'nb-badge-green';
  if (status === 'rejected') return 'nb-badge-red';
  return 'nb-badge-yellow';
};

const formatDate = (dateStr) => {
  if (!dateStr) return 'N/A';
  return new Date(dateStr).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
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

.nb-badge-gray   { background: #e0e0e0; border: 2px solid #323232; }
.nb-badge-green  { background: #58cc02; color: white; border: 2px solid #323232; }
.nb-badge-red    { background: #ff5c5c; color: white; border: 2px solid #323232; }
.nb-badge-yellow { background: #fdfd96; color: #323232; border: 2px solid #323232; }

.nb-button-red   { background-color: #ff5c5c; color: white; }
.nb-button-green { background-color: #58cc02; color: white; }

.small-btn {
  height: 32px;
  padding: 0 15px;
  font-size: 14px;
}
</style>