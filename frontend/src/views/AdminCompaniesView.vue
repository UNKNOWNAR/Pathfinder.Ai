<script setup>
import { ref, onMounted } from 'vue';
import NavBar from '@/components/NavBar.vue';
import api from '@/services/api';

const companies = ref([]);
const loading = ref(true);
const error = ref('');

const loadCompanies = async () => {
  try {
    const res = await api.get('/admin/companies');
    companies.value = res.data;
  } catch (err) {
    error.value = 'Failed to load companies.';
    console.error(err);
  } finally {
    loading.value = false;
  }
};

const approveCompany = async (companyId) => {
  try {
    await api.post(`/admin/companies/${companyId}/approve`);
    // Update local state without re-fetching
    const company = companies.value.find(c => c.company_id === companyId);
    if (company) {
      company.is_approved = true;
    }
  } catch (err) {
    alert('Failed to approve company.');
    console.error(err);
  }
};

onMounted(() => {
  loadCompanies();
});
</script>

<template>
  <div class="page">
    <NavBar />

    <main class="main">
      <div class="header-row">
        <h3 class="section-title">▤ COMPANY APPROVALS</h3>
        <button class="brutal-btn" @click="loadCompanies">REFRESH</button>
      </div>

      <div v-if="loading" class="status-msg">Loading companies...</div>
      <div v-else-if="error" class="status-msg error">{{ error }}</div>
      <div v-else-if="companies.length === 0" class="status-msg">No companies registered yet.</div>

      <div v-else class="companies-grid">
        <div v-for="company in companies" :key="company.company_id" class="box company-card">
          <div class="card-header">
            <h4 class="company-name">{{ company.name.toUpperCase() }}</h4>
            <span class="status-badge" :class="company.is_approved ? 'approved' : 'pending'">
              {{ company.is_approved ? 'APPROVED' : 'PENDING' }}
            </span>
          </div>

          <div class="card-body">
            <p class="company-email"><strong>EMAIL:</strong> {{ company.email }}</p>
            <p class="company-date"><strong>REGISTERED:</strong> {{ new Date(company.created_at).toLocaleDateString() }}</p>
          </div>

          <div class="card-actions" v-if="!company.is_approved">
            <button class="primary-btn approve-btn" @click="approveCompany(company.company_id)">
              APPROVE ACCOUNT
            </button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.main {
  max-width: 1100px;
  width: 100%;
  margin: 0 auto;
  padding: 28px 28px 60px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}
.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.companies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
}
.company-card {
  display: flex;
  flex-direction: column;
}
.card-header {
  padding: 16px;
  border-bottom: var(--border);
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  background: #fafafa;
}
.company-name {
  font-weight: 900;
  font-size: 16px;
  margin: 0;
  word-break: break-all;
}
.status-badge {
  font-size: 10px;
  font-weight: 900;
  padding: 4px 8px;
  border: 2px solid var(--ink);
  box-shadow: 2px 2px 0 var(--ink);
}
.status-badge.approved { background: #55efc4; }
.status-badge.pending { background: #ffeaa7; }
.card-body {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
}
.company-email, .company-date {
  font-size: 13px;
  margin: 0;
}
.card-actions {
  padding: 16px;
  border-top: 2px dashed var(--ink);
  background: #fafafa;
}
@media (max-width: 600px) {
  .companies-grid {
    grid-template-columns: 1fr;
  }
}
</style>