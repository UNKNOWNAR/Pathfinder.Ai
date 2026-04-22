<template>
  <div class="main-wrapper">
    <AdminNavBar />

    <main class="container py-5">
      <div class="nb-header mb-4">
        <div>
          <h1 class="nb-title">Company Management</h1>
          <p class="nb-subtitle">Review and manage company registrations and status.</p>
        </div>
        <div class="d-flex gap-3 align-items-center">
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Search companies..." 
            class="nb-input" 
            style="width: 300px; height: 45px;"
          />
          <button class="nb-button nb-button-blue" @click="exportCompanies">📧 Export CSV</button>
        </div>
      </div>

      <div v-if="!loaded" class="text-center py-5">
        <div class="nb-card p-5">Loading companies...</div>
      </div>

      <div v-else class="nb-card overflow-hidden p-0">
        <div class="table-responsive">
          <table class="nb-table mb-0">
            <thead>
              <tr>
                <th class="ps-4">ID</th>
                <th>Company Name</th>
                <th>Apprv Status</th>
                <th>Account Status</th>
                <th class="text-end pe-4">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="c in filteredCompanies" :key="c.user_id">
                <td class="ps-4 font-monospace">#{{ c.user_id }}</td>
                <td class="nb-cell-bold">{{ c.name }}</td>
                <td>
                  <span :class="['nb-badge', c.status === 'approved' ? 'nb-badge-green' : 'nb-badge-yellow']">
                    {{ c.status.toUpperCase() }}
                  </span>
                </td>
                <td>
                  <span :class="['nb-badge', c.active ? 'nb-badge-blue' : 'nb-badge-red']">
                    {{ c.active ? 'ACTIVE' : 'DEACTIVATED' }}
                  </span>
                </td>
                <td class="text-end pe-4">
                  <div class="d-flex justify-content-end gap-2">
                    <button 
                      v-if="c.status !== 'approved'" 
                      class="nb-button nb-button-green small-btn" 
                      @click="approveCompany(c.user_id)"
                    >Approve</button>
                    
                    <button 
                      :class="['nb-button small-btn', c.active ? 'nb-button-red' : 'nb-button-blue']"
                      @click="toggleStatus(c)"
                    >
                      {{ c.active ? 'Deactivate' : 'Activate' }}
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
import AdminNavBar from '@/components/AdminNavBar.vue';
import api from '@/services/api';

const companies = ref([]);
const loaded = ref(false);
const searchQuery = ref('');

const filteredCompanies = computed(() => {
  if (!searchQuery.value) return companies.value;
  const q = searchQuery.value.toLowerCase();
  return companies.value.filter(c => c.name.toLowerCase().includes(q));
});

const loadCompanies = async () => {
  try {
    const res = await api.get('/admin/companies');
    companies.value = res.data;
    loaded.value = true;
  } catch (err) {
    console.error('[ERROR]', err);
    loaded.value = true;
  }
};

const approveCompany = async (id) => {
  try {
    const res = await api.post(`/admin/approve-company/${id}`);
    alert(res.data.message);
    loadCompanies();
  } catch (err) {
    alert('Approval failed.');
  }
};

const toggleStatus = async (company) => {
  try {
    const res = await api.post(`/admin/toggle-status/${company.user_id}`);
    company.active = res.data.active;
    alert(res.data.message);
  } catch (err) {
    alert(err.response?.data?.message || 'Toggle failed');
  }
};

const exportCompanies = async () => {
  try {
    const res = await api.get('/admin/export/companies');
    alert(res.data.message);
  } catch (err) {
    alert('Export failed.');
  }
};

onMounted(() => { loadCompanies(); });
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
.nb-badge-yellow { background: #fdfd96; color: #323232; border: 2px solid #323232; }
.nb-badge-green { background: #58cc02; color: white; border: 2px solid #323232; }
.nb-badge-blue { background: #2d8cf0; color: white; border: 2px solid #323232; }
.nb-badge-red { background: #ff5c5c; color: white; border: 2px solid #323232; }

.nb-button-red { background-color: #ff5c5c; color: white; }
.nb-button-green { background-color: #58cc02; color: white; }
.nb-button-blue { background-color: #2d8cf0; color: white; }

.small-btn {
  height: 32px;
  padding: 0 15px;
  font-size: 14px;
}
</style>