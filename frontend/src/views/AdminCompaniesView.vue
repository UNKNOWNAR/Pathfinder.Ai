<script setup>
import { ref, onMounted, watch } from 'vue';
import NavBar from '@/components/NavBar.vue';
import api from '@/services/api';

const companies = ref([]);
const total     = ref(0);
const pages     = ref(1);
const page      = ref(1);
const search    = ref('');
const loading   = ref(true);
const error     = ref('');

const loadCompanies = async () => {
  loading.value = true;
  error.value = '';
  try {
    const res = await api.get('/admin/companies', {
      params: { page: page.value, per_page: 20, q: search.value }
    });
    companies.value = res.data.companies;
    total.value     = res.data.total;
    pages.value     = res.data.pages;
  } catch (err) {
    error.value = 'Failed to load companies.';
    console.error(err);
  } finally {
    loading.value = false;
  }
};

// Debounce search
let debounceTimer = null;
watch(search, () => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    page.value = 1;
    loadCompanies();
  }, 400);
});

const prevPage = () => { if (page.value > 1) { page.value--; loadCompanies(); } };
const nextPage = () => { if (page.value < pages.value) { page.value++; loadCompanies(); } };

const approveCompany = async (companyId) => {
  try {
    await api.post(`/admin/companies/${companyId}/approve`);
    // Update local state
    const company = companies.value.find(c => c.company_id === companyId);
    if (company) {
      company.is_approved = true;
    }
  } catch (err) {
    alert('Failed to approve company.');
    console.error(err);
  }
};

onMounted(loadCompanies);
</script>

<template>
  <div class="page">
    <NavBar />

    <main class="main">
      <div class="header-row box">
        <div>
          <h3 class="section-title">▤ COMPANY APPROVALS</h3>
          <p class="page-sub">{{ total.toLocaleString() }} registered companies</p>
        </div>
        <button class="brutal-btn" @click="loadCompanies">REFRESH</button>
      </div>

      <!-- Search Bar -->
      <div class="search-row">
        <input
          class="search-input"
          v-model="search"
          placeholder="Search by company name or email..."
          type="text"
        />
      </div>

      <div v-if="loading" class="status-msg">Loading companies...</div>
      <div v-else-if="error" class="status-msg error">{{ error }}</div>

      <div v-else-if="companies.length === 0" class="empty-box box">
        <p>No companies found matching your search.</p>
      </div>

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

      <!-- Pagination -->
      <div v-if="pages > 1" class="pagination">
        <button class="page-btn" @click="prevPage" :disabled="page === 1">← Prev</button>
        <span class="page-indicator">Page {{ page }} of {{ pages }}</span>
        <button class="page-btn" @click="nextPage" :disabled="page === pages">Next →</button>
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
  padding: 20px 24px;
}
.page-sub { font-size: 13px; font-weight: 600; opacity: 0.6; margin-top: 4px; }

.search-row   { display: flex; gap: 12px; }
.search-input {
  flex: 1;
  height: 44px;
  padding: 0 14px;
  font-size: 14px;
  font-weight: 600;
  border: var(--border);
  box-shadow: var(--shadow);
  background: var(--surface);
  outline: none;
}
.search-input:focus { box-shadow: 6px 6px 0 var(--ink); }

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
.empty-box { padding: 40px; text-align: center; font-weight: 700; opacity: 0.5; }

.pagination { display: flex; align-items: center; justify-content: center; gap: 16px; margin-top: 20px; }
.page-btn {
  padding: 8px 20px;
  font-weight: 800;
  font-size: 13px;
  border: var(--border);
  box-shadow: 3px 3px 0 var(--ink);
  background: var(--surface);
  cursor: pointer;
  transition: box-shadow 0.1s, transform 0.1s;
}
.page-btn:disabled { opacity: 0.35; cursor: not-allowed; box-shadow: none; }
.page-btn:not(:disabled):active { box-shadow: 1px 1px 0 var(--ink); transform: translate(2px, 2px); }
.page-indicator { font-weight: 800; font-size: 13px; }

@media (max-width: 600px) {
  .companies-grid {
    grid-template-columns: 1fr;
  }
}
</style>