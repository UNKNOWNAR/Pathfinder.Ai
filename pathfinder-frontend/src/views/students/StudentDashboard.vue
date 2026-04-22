<script setup>
import { ref, onMounted, computed } from 'vue';
import StudentNavBar from '@/components/StudentNavBar.vue';
import api from '@/services/api';
import {
  Chart as ChartJS, Title, Tooltip, Legend, ArcElement, CategoryScale, LinearScale
} from 'chart.js';
import { Doughnut } from 'vue-chartjs';

ChartJS.register(CategoryScale, LinearScale, ArcElement, Title, Tooltip, Legend);

const userName = localStorage.getItem('username') || 'Student';
const stats = ref({ applied: 0, shortlisted: 0, selected: 0 });
const recentDrives = ref([]);
const loaded = ref(false);

const chartData = computed(() => ({
  labels: ['Applied', 'Shortlisted', 'Selected'],
  datasets: [{
    backgroundColor: ['#2d8cf0', '#f9d71c', '#58cc02'],
    data: [stats.value.applied, stats.value.shortlisted, stats.value.selected],
    borderWidth: 2,
    borderColor: '#323232'
  }]
}));

const loadDashboard = async () => {
  try {
    const statsRes = await api.get('/student/stats');
    stats.value = statsRes.data;

    const drivesRes = await api.get('/student/drives');
    recentDrives.value = drivesRes.data.slice(0, 3);
    
    loaded.value = true;
  } catch (err) {
    console.error('[ERROR] Dashboard load failed:', err);
    loaded.value = true;
  }
};

const exportHistory = async () => {
  try {
    const res = await api.get('/student/export');
    alert(res.data.message);
  } catch (err) {
    alert('Export failed.');
  }
};

onMounted(() => {
  loadDashboard();
});
</script>

<template>
  <div class="main-wrapper">
    <StudentNavBar />
    
    <main class="container py-5">
      <!-- Header -->
      <div class="nb-header mb-5">
        <div>
          <h1 class="nb-title">Welcome back, {{ userName }}</h1>
          <p class="nb-subtitle">Your recruitment journey at a glance.</p>
        </div>
        <button class="nb-button nb-button-blue" @click="exportHistory">
          📧 Export My History
        </button>
      </div>

      <!-- Stats Section with Chart -->
      <div class="row g-4 mb-5" v-if="loaded">
        <div class="col-lg-6">
          <div class="nb-card h-100">
            <h5 class="nb-section-title mb-4">Application Progress</h5>
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

        <div class="col-lg-6">
          <div class="row g-4 rotate-layout">
            <div class="col-12">
              <div class="nb-card nb-card-blue h-100 py-3">
                <div class="d-flex justify-content-between align-items-center px-4">
                  <h6 class="nb-card-label mb-0">Total Applications</h6>
                  <h2 class="nb-card-value">{{ stats.applied }}</h2>
                </div>
              </div>
            </div>
            <div class="col-12">
              <div class="nb-card nb-card-yellow h-100 py-3">
                <div class="d-flex justify-content-between align-items-center px-4">
                  <h6 class="nb-card-label mb-0">Shortlisted</h6>
                  <h2 class="nb-card-value">{{ stats.shortlisted }}</h2>
                </div>
              </div>
            </div>
            <div class="col-12">
              <div class="nb-card nb-card-green h-100 py-3">
                <div class="d-flex justify-content-between align-items-center px-4">
                  <h6 class="nb-card-label mb-0">Final Selections</h6>
                  <h2 class="nb-card-value">{{ stats.selected }}</h2>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Main Content -->
      <div class="row g-5">
        <div class="col-lg-8">
          <div class="d-flex justify-content-between align-items-center mb-4">
            <h3 class="nb-section-title">Recommended Matches</h3>
            <router-link to="/placement-drives" class="nb-button small-btn">View All</router-link>
          </div>

          <div v-if="recentDrives.length === 0" class="nb-alert">
            No matches found yet. Keep your profile updated!
          </div>

          <div v-else>
            <div v-for="drive in recentDrives" :key="drive.drive_id" class="nb-card mb-3 drive-item">
              <div class="d-flex justify-content-between align-items-center">
                <div>
                  <h5 class="nb-item-title">{{ drive.job_title }}</h5>
                  <p class="nb-item-sub">{{ drive.company_name }}</p>
                </div>
                <router-link to="/placement-drives" class="nb-button small-btn">Details</router-link>
              </div>
            </div>
          </div>
        </div>

        <!-- Sidebar -->
        <div class="col-lg-4">
          <div class="nb-card nb-card-dark p-4">
            <h4 class="nb-card-title-white">Quick Tip</h4>
            <p class="nb-card-text-white">Make sure your branch and batch year are correct so you see the most relevant jobs.</p>
            <router-link to="/student/profile" class="nb-button nb-button-blue w-100 mt-3">Update Profile</router-link>
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
.nb-section-title {
  font-weight: 900;
  text-transform: uppercase;
  margin: 0;
}
.nb-card-blue { background-color: #2d8cf0; color: white; }
.nb-card-yellow { background-color: #fdfd96; color: #323232; }
.nb-card-green { background-color: #58cc02; color: white; }
.nb-card-dark { background-color: #323232; color: white; }

.nb-card-label { text-transform: uppercase; font-weight: 900; opacity: 0.8; font-size: 0.9rem; }
.nb-card-value { font-size: 3.5rem; font-weight: 900; margin: 0; }

.nb-item-title { font-weight: 900; margin: 0; font-size: 1.2rem; }
.nb-item-sub { font-weight: 600; color: #666; margin: 0; }

.nb-card-title-white { font-weight: 900; color: #fdfd96; text-transform: uppercase; }
.nb-card-text-white { font-weight: 400; opacity: 0.9; }

.nb-alert {
  padding: 20px;
  background: white;
  border: 2px solid #323232;
  box-shadow: 4px 4px #323232;
  font-weight: 600;
}
.small-btn {
  height: 32px;
  padding: 0 15px;
  font-size: 0.85rem;
}
.drive-item {
  transition: transform 0.2s;
}
.drive-item:hover {
  transform: translate(-2px, -2px);
  box-shadow: 6px 6px #323232;
}
</style>