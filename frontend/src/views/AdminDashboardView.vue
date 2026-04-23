<script setup>
import { ref, onMounted, computed } from 'vue';
import NavBar from '@/components/NavBar.vue';
import api from '@/services/api';
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
  ArcElement,
  PointElement,
  LineElement,
  Filler
} from 'chart.js';
import { Doughnut, Bar } from 'vue-chartjs';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement, PointElement, LineElement, Filler);

const stats = ref({ students: 0, companies: 0, jobs: 0, sources: {}, roles: {} });
const loaded = ref(false);

const loadStats = async () => {
  try {
    const res = await api.get('/admin/stats');
    stats.value = res.data;
    loaded.value = true;
  } catch {
    console.error('[ERROR] Failed to load platform stats.');
  }
};

onMounted(async () => {
  await loadStats();
});

// Chart Configurations
const userChartData = computed(() => ({
  labels: ['Students', 'Companies'],
  datasets: [
    {
      backgroundColor: ['#2d8cf0', '#ff4757'],
      data: [stats.value.students, stats.value.companies],
      borderWidth: 2,
      borderColor: '#111111'
    }
  ]
}));

const userChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom',
      labels: { font: { family: "'Segoe UI', sans-serif", weight: 'bold' }, color: '#111111' }
    }
  }
};

const sourceChartData = computed(() => {
    const labels = Object.keys(stats.value.sources);
    const data = Object.values(stats.value.sources);
    return {
        labels,
        datasets: [{
            label: 'Jobs Harvested',
            backgroundColor: '#00b894',
            borderColor: '#111111',
            borderWidth: 2,
            data
        }]
    };
});

const sourceChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: { display: false }
    },
    scales: {
        y: { beginAtZero: true, grid: { color: 'rgba(17, 17, 17, 0.1)' } },
        x: { grid: { display: false } }
    }
};

const roleChartData = computed(() => {
    const labels = Object.keys(stats.value.roles).filter(k => k !== 'Other');
    const data = labels.map(l => stats.value.roles[l]);

    // Custom colors for different roles
    const colors = ['#ffeaa7', '#74b9ff', '#55efc4', '#fab1a0', '#a29bfe', '#81ecec', '#fdcb6e'];

    return {
        labels,
        datasets: [{
            backgroundColor: colors,
            borderColor: '#111111',
            borderWidth: 2,
            data
        }]
    };
});
</script>

<template>
  <div class="page">
    <NavBar />

    <main class="main">
      <h3 class="section-title">▤ PLATFORM ANALYTICS DASHBOARD</h3>

      <!-- Top Overview Metrics -->
      <div class="metrics-grid">
        <div class="box metric-box bg-blue" title="Active students vs total registered">
            <span class="metric-title">STUDENTS (ACTIVE/TOTAL)</span>
            <span class="metric-value">{{ stats.students_active }} / {{ stats.students }}</span>
        </div>
        <div class="box metric-box bg-red" title="Approved companies vs total registered">
            <span class="metric-title">COMPANIES (APPV/TOTAL)</span>
            <span class="metric-value">{{ stats.companies_approved }} / {{ stats.companies }}</span>
        </div>
        <div class="box metric-box bg-green">
            <span class="metric-title">ACTIVE JOBS</span>
            <span class="metric-value">{{ stats.jobs.toLocaleString() }}</span>
        </div>
        <div class="box metric-box bg-purple">
            <span class="metric-title">JOB SOURCES</span>
            <span class="metric-value">{{ Object.keys(stats.sources).length }}</span>
        </div>
      </div>

      <!-- Main Two Column Grid -->
      <div class="grid" v-if="loaded">

        <!-- Left Col: Demographics & Roles -->
        <div class="col">
          <div class="box chart-card">
              <h4 class="chart-title">User Demographics</h4>
              <div class="chart-container" style="height: 250px;">
                  <Doughnut :data="userChartData" :options="userChartOptions" />
              </div>
          </div>

          <div class="box chart-card">
              <h4 class="chart-title">Job Role Distribution</h4>
              <div class="chart-container" style="height: 280px;">
                  <Doughnut :data="roleChartData" :options="userChartOptions" />
              </div>
          </div>
        </div>

        <!-- Right Col: API Sourcing -->
        <div class="col">
          <div class="box chart-card" style="flex: 1;">
              <h4 class="chart-title">Harvesting Source Yield</h4>
              <div class="chart-container" style="height: 100%; min-height: 400px;">
                  <Bar :data="sourceChartData" :options="sourceChartOptions" />
              </div>
          </div>
        </div>

      </div>

    </main>
  </div>
</template>

<style scoped>
.page {
   /* Red accent for admin */}
.main { max-width: 1100px; width: 100%; margin: 0 auto; padding: 28px 28px 60px; display: flex; flex-direction: column; gap: 24px; }
/* Metrics Banner */
.metrics-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
.metric-box { padding: 20px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 4px; transition: transform 0.1s; cursor: default; }
.metric-box:hover { transform: translate(-2px, -2px); box-shadow: 6px 6px 0 var(--ink); }
.metric-title { font-weight: 900; font-size: 12px; letter-spacing: 0.1em; opacity: 0.9; }
.metric-value { font-weight: 900; font-size: 32px; letter-spacing: -1px; }
.bg-blue { background: #74b9ff; color: var(--ink); }
.bg-red { background: #ff7675; color: var(--ink); }
.bg-green { background: #55efc4; color: var(--ink); }
.bg-purple { background: #a29bfe; color: var(--ink); }
/* Grid Layouts */
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
.col  { display: flex; flex-direction: column; gap: 24px; }
/* Charts */
.chart-card { padding: 24px; display: flex; flex-direction: column; gap: 16px; background: #fafafa; }
.chart-title { font-size: 14px; font-weight: 900; text-transform: uppercase; border-bottom: 2px solid var(--ink); padding-bottom: 8px; margin: 0; }
.chart-container { position: relative; width: 100%; }
@media (max-width: 860px) {
  .grid { grid-template-columns: 1fr; }
.metrics-grid { grid-template-columns: 1fr; }
}
</style>