<template>
  <div class="main-wrapper">
    <AdminNavBar />

    <main class="container py-5">
      <div class="nb-header mb-4">
        <div>
          <h1 class="nb-title">Student Directory</h1>
          <p class="nb-subtitle">Master list of all registered students.</p>
        </div>
        <div class="d-flex gap-3 align-items-center">
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Search students..." 
            class="nb-input" 
            style="width: 300px; height: 45px;"
          />
          <button class="nb-button nb-button-blue" @click="exportStudents">📧 Export CSV</button>
        </div>
      </div>

      <div v-if="!loaded" class="text-center py-5">
        <div class="nb-card p-5">Loading directory data...</div>
      </div>

      <div v-else class="nb-card overflow-hidden p-0">
        <div class="table-responsive">
          <table class="nb-table mb-0">
            <thead>
              <tr>
                <th class="ps-4">UID</th>
                <th>Student Name</th>
                <th>Branch</th>
                <th>Batch Year</th>
                <th>Status</th>
                <th class="pe-4">Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="s in filteredStudents" :key="s.user_id">
                <td class="ps-4 font-monospace">#{{ s.user_id }}</td>
                <td class="nb-cell-bold">{{ s.name }}</td>
                <td>
                  <span class="nb-badge nb-badge-gray">
                    {{ s.branch || 'N/A' }}
                  </span>
                </td>
                <td class="nb-cell-bold">{{ s.batch_year || 'N/A' }}</td>
                <td>
                  <span :class="['nb-badge', s.active ? 'nb-badge-green' : 'nb-badge-red']">
                    {{ s.active ? 'ACTIVE' : 'DEACTIVATED' }}
                  </span>
                </td>
                <td class="pe-4">
                  <button 
                    :class="['nb-button small-btn', s.active ? 'nb-button-red' : 'nb-button-green']"
                    @click="toggleStatus(s)"
                  >
                    {{ s.active ? 'Deactivate' : 'Activate' }}
                  </button>
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
import AdminNavBar from '@/components/AdminNavBar.vue';
import api from '@/services/api';

const students = ref([]);
const loaded = ref(false);
const searchQuery = ref('');

const filteredStudents = computed(() => {
  if (!searchQuery.value) return students.value;
  const q = searchQuery.value.toLowerCase();
  return students.value.filter(s => 
    s.name.toLowerCase().includes(q) || 
    (s.branch && s.branch.toLowerCase().includes(q))
  );
});

const loadStudents = async () => {
  try {
    const res = await api.get('/admin/students');
    students.value = res.data;
    loaded.value = true;
  } catch (err) {
    console.error('[ERROR]', err);
    loaded.value = true;
  }
};

const toggleStatus = async (student) => {
  try {
    const res = await api.post(`/admin/toggle-status/${student.user_id}`);
    student.active = res.data.active;
    alert(res.data.message);
  } catch (err) {
    alert(err.response?.data?.message || 'Toggle failed');
  }
};

const exportStudents = async () => {
  try {
    const res = await api.get('/admin/export/students');
    alert(res.data.message);
  } catch (err) {
    alert('Export failed.');
  }
};

onMounted(() => { loadStudents(); });
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
.nb-badge-gray { background: #e0e0e0; border: 2px solid #323232; }
.nb-badge-green { background: #58cc02; color: white; border: 2px solid #323232; }
.nb-badge-red { background: #ff5c5c; color: white; border: 2px solid #323232; }

.nb-button-red { background-color: #ff5c5c; color: white; }
.nb-button-green { background-color: #58cc02; color: white; }

.small-btn {
  height: 32px;
  padding: 0 15px;
  font-size: 14px;
}
</style>