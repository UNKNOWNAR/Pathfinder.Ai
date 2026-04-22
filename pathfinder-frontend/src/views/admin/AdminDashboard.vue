<script setup>
import { ref, onMounted, computed } from 'vue';
import AdminNavBar from '@/components/AdminNavBar.vue';
import api from '@/services/api';
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
  ArcElement
} from 'chart.js';
import { Doughnut } from 'vue-chartjs';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement);

const stats = ref({ student_count: 0, company_count: 0, placement_drive_count: 0 });
const loaded = ref(false);

const loadStats = async () => {
  try {
    const res = await api.get('/admin/stats');
    stats.value = res.data;
    loaded.value = true;
  } catch (err) {
    console.error('[ERROR] Failed to load stats:', err);
    loaded.value = true;
  }
};

const userChartData = computed(() => ({
  labels: ['Students', 'Companies', 'Drives'],
  datasets: [
    {
      backgroundColor: ['#2d8cf0', '#fdfd96', '#58cc02'],
      data: [stats.value.student_count, stats.value.company_count, stats.value.placement_drive_count],
      borderWidth: 2,
      borderColor: '#323232'
    }
  ]
}));

const exportData = async (target) => {
  try {
    const res = await api.get(`/admin/export/${target}`);
    alert(res.data.message);
  } catch (err) {
    alert('Export failed.');
  }
};

const triggerMonthlyReport = async () => {
  try {
    const res = await api.get('/admin/monthly-report');
    alert(res.data.message);
  } catch (err) {
    alert('Failed to trigger report.');
  }
};

onMounted(() => {
  loadStats();
});
</script>

<template>
  <div class="main-wrapper">
    <AdminNavBar />

    <main class="container py-5">
      <div class="nb-header mb-5">
        <div>
          <h1 class="nb-title">Platform Analytics</h1>
          <p class="nb-subtitle">Master overview of all user and recruitment data.</p>
        </div>
        <div class="button-group gap-2">
          <button class="nb-button nb-button-yellow" @click="triggerMonthlyReport">📊 Send Monthly Report</button>
          <button class="nb-button nb-button-blue" @click="exportData('students')">📧 Export Students</button>
          <button class="nb-button nb-button-blue" @click="exportData('companies')">📧 Export Companies</button>
        </div>
      </div>

      <!-- Quick Stats -->
      <div class="row g-4 mb-5">
        <div class="col-md-4">
          <div class="nb-card h-100 text-center">
            <h6 class="nb-card-label">Total Students</h6>
            <h2 class="nb-card-value text-blue">{{ stats.student_count }}</h2>
          </div>
        </div>
        <div class="col-md-4">
          <div class="nb-card h-100 text-center">
            <h6 class="nb-card-label">Total Companies</h6>
            <h2 class="nb-card-value text-yellow">{{ stats.company_count }}</h2>
          </div>
        </div>
        <div class="col-md-4">
          <div class="nb-card h-100 text-center">
            <h6 class="nb-card-label">Total Drives</h6>
            <h2 class="nb-card-value text-green">{{ stats.placement_drive_count }}</h2>
          </div>
        </div>
      </div>

      <div class="row g-4" v-if="loaded">
        <!-- Chart -->
        <div class="col-lg-6">
          <div class="nb-card h-100">
            <h5 class="nb-section-title mb-4">User Distribution</h5>
            <div style="height: 300px;">
              <Doughnut :data="userChartData" :options="{ 
                responsive: true, 
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    labels: {
                      font: {
                        family: 'Outfit',
                        weight: '900',
                        size: 14
                      },
                      color: '#323232'
                    }
                  }
                }
              }" />
            </div>
          </div>
        </div>

        <!-- Quick Actions -->
        <div class="col-lg-6">
          <div class="nb-card h-100 p-4">
            <h5 class="nb-section-title">Pending Approvals</h5>
            <p class="nb-subtitle mb-4">Review new companies and job postings before they go live on the platform.</p>
            <div class="d-grid gap-4">
              <router-link to="/admin/companies" class="nb-button nb-button-blue">Approve Companies</router-link>
              <router-link to="/admin/placement-drives" class="nb-button nb-button-blue">Review Drives</router-link>
            </div>
          </div>
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
.nb-title {
  font-size: 2.5rem;
  font-weight: 900;
  margin: 0;
  text-transform: none;
}
.nb-subtitle {
  font-weight: 600;
  color: #666;
  font-size: 1.1rem;
}
.nb-card-label { text-transform: uppercase; font-weight: 900; opacity: 0.8; font-size: 0.9rem; color: #323232; }
.nb-card-value { font-size: 3.5rem; font-weight: 900; margin: 0; }

.text-blue { color: #2d8cf0; }
.text-yellow { color: #f9d71c; }
.text-green { color: #58cc02; }

.nb-section-title {
  font-weight: 900;
  text-transform: uppercase;
  margin: 0;
}
.nb-card-blue { background-color: #2d8cf0; color: white; }
.nb-card-title-white { font-weight: 900; color: #fdfd96; text-transform: uppercase; font-size: 1.5rem; }
.nb-card-text-white { font-weight: 600; opacity: 0.9; }

.nb-card-blue .nb-button {
  color: #323232;
}
.nb-button-dark {
  background-color: var(--main-white);
  color: #323232;
}
.nb-button-yellow {
  background-color: #fdfd96;
  color: #323232;
}

.button-group {
  display: flex;
}
</style>
