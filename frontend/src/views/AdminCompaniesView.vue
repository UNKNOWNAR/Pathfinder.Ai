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
.page {
  --ink:     #111111;
  --bg:      #DEDEDE;
  --surface: #FFFFFF;
  --accent:  #2d8cf0;
  --admin-accent: #ff4757;
  --border:  2px solid var(--ink);
  --shadow:  4px 4px 0 var(--ink);

  min-height: 100vh;
  background: var(--bg);
  color: var(--ink);
  font-family: 'Segoe UI', sans-serif;
}

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

.section-title {
  font-size: 18px;
  font-weight: 900;
  text-transform: uppercase;
  text-decoration: underline;
  text-underline-offset: 4px;
  text-decoration-thickness: 2px;
}

.brutal-btn {
  padding: 8px 16px;
  background: var(--surface);
  border: var(--border);
  box-shadow: 3px 3px 0 var(--ink);
  font-weight: 900;
  font-size: 13px;
  cursor: pointer;
  transition: transform 0.1s, box-shadow 0.1s;
}

.brutal-btn:active {
  box-shadow: 1px 1px 0 var(--ink);
  transform: translate(2px, 2px);
}

.status-msg {
  padding: 24px;
  background: var(--surface);
  border: var(--border);
  box-shadow: var(--shadow);
  font-weight: 800;
  text-align: center;
}

.error {
  background: #ff7675;
}

.box {
  background: var(--surface);
  border: var(--border);
  box-shadow: var(--shadow);
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

.primary-btn {
  width: 100%;
  padding: 12px;
  background: #55efc4;
  border: var(--border);
  box-shadow: 3px 3px 0 var(--ink);
  font-weight: 900;
  font-size: 14px;
  cursor: pointer;
  transition: transform 0.1s, box-shadow 0.1s;
}

.primary-btn:active {
  box-shadow: 1px 1px 0 var(--ink);
  transform: translate(2px, 2px);
}

@media (max-width: 600px) {
  .companies-grid {
    grid-template-columns: 1fr;
  }
}
</style>