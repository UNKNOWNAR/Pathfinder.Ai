<template>
  <div class="main-wrapper">
    <CompanyNavBar />

    <main class="container py-5">
      <div class="nb-header mb-5">
        <div>
          <h1 class="nb-title">Dashboard</h1>
          <p class="nb-subtitle">Overview of your recruitment activities and statistics.</p>
        </div>
        <div class="d-flex gap-3">
          <router-link to="/company/drives" class="nb-button nb-button-blue" style="text-decoration: none;">
            Manage Drives
          </router-link>
          <router-link to="/company/applicants" class="nb-button nb-button-yellow" style="text-decoration: none;">
            All Applicants
          </router-link>
        </div>
      </div>

      <!-- Quick Stats -->
      <div class="row g-4 mb-5" v-if="statsLoaded">
        <div class="col-md-3">
          <div class="nb-card h-100 text-center">
            <h6 class="nb-card-label">Total Applied</h6>
            <h2 class="nb-card-value text-blue">{{ stats.total_applied }}</h2>
          </div>
        </div>
        <div class="col-md-3">
          <div class="nb-card h-100 text-center">
            <h6 class="nb-card-label">Selected</h6>
            <h2 class="nb-card-value text-green">{{ stats.selected }}</h2>
          </div>
        </div>
        <div class="col-md-3">
          <div class="nb-card h-100 text-center">
            <h6 class="nb-card-label">Shortlisted</h6>
            <h2 class="nb-card-value text-yellow">{{ stats.shortlisted }}</h2>
          </div>
        </div>
        <div class="col-md-3">
          <div class="nb-card h-100 text-center">
            <h6 class="nb-card-label">Pending</h6>
            <h2 class="nb-card-value" style="color: #666;">{{ stats.pending }}</h2>
          </div>
        </div>
      </div>

      <div class="row g-4 mb-5" v-if="statsLoaded">
        <!-- Chart -->
        <div class="col-lg-6">
          <div class="nb-card h-100">
            <h5 class="nb-section-title mb-4">Application Distribution</h5>
            <div style="height: 300px;">
              <Doughnut :data="chartData" :options="{ 
                responsive: true, 
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    labels: {
                      font: { family: 'Outfit', weight: '900', size: 14 },
                      color: '#323232'
                    }
                  }
                }
              }" />
            </div>
          </div>
        </div>
        
        <!-- Info Card -->
        <div class="col-lg-6">
          <div class="nb-card h-100 p-4 d-flex flex-column justify-content-center">
            <h5 class="nb-section-title">Manage Your Candidates</h5>
            <p class="nb-subtitle mb-4">Track applications directly from specific drives below. Review applicant profiles, filter by eligibility, and export shortlisted students as CSV!</p>
          </div>
        </div>
      </div>


    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import CompanyNavBar from '@/components/CompanyNavBar.vue';
import api from '@/services/api';
import {
  Chart as ChartJS, Title, Tooltip, Legend, ArcElement, CategoryScale, LinearScale
} from 'chart.js';
import { Doughnut } from 'vue-chartjs';

ChartJS.register(CategoryScale, LinearScale, ArcElement, Title, Tooltip, Legend);



const stats = ref({ selected: 0, shortlisted: 0, pending: 0, total_applied: 0, total_drives: 0 });
const statsLoaded = ref(false);

const chartData = computed(() => ({
  labels: ['Selected', 'Shortlisted', 'Pending'],
  datasets: [{
    backgroundColor: ['#58cc02', '#f9d71c', '#cccccc'],
    data: [stats.value.selected, stats.value.shortlisted, stats.value.pending],
    borderWidth: 2,
    borderColor: '#323232'
  }]
}));

const loadStats = async () => {
  try {
    const res = await api.get('/company/stats');
    stats.value = res.data;
    statsLoaded.value = true;
  } catch (err) {
    console.error('[ERROR] Failed to load stats:', err);
    statsLoaded.value = true;
  }
};



onMounted(() => {
  loadStats();
});
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

.nb-card-label { text-transform: uppercase; font-weight: 900; opacity: 0.8; font-size: 0.9rem; color: #323232; }
.nb-card-value { font-size: 3.5rem; font-weight: 900; margin: 0; }
.text-blue { color: #2d8cf0; }
.text-yellow { color: #f9d71c; }
.text-green { color: #58cc02; }
.nb-section-title { font-weight: 900; text-transform: uppercase; margin: 0; }
</style>
