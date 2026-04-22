<template>
  <div class="main-wrapper">
    <StudentNavBar />
    
    <main class="container py-5">
      <div class="nb-header mb-5">
        <div>
          <h1 class="nb-title">Available Placement Drives</h1>
          <p class="nb-subtitle">Jobs matching your profile criteria.</p>
        </div>
        <input 
          v-model="searchQuery" 
          type="text" 
          placeholder="Search roles or companies..." 
          class="nb-input" 
          style="width: 350px; height: 50px;"
        />
      </div>

      <div v-if="!loaded" class="text-center py-5">
        <div class="nb-card p-5">Loading placement drives...</div>
      </div>
      
      <div v-else-if="drives.length === 0" class="nb-card p-5 text-center">
        <h4 class="nb-cell-bold mb-2">No placement drives available for you right now.</h4>
        <p class="nb-subtitle m-0">Check back later or ensure your profile CGPA is correct.</p>
      </div>

      <div v-else class="row g-4">
        <div v-for="drive in filteredDrives" :key="drive.drive_id" class="col-md-6 col-lg-4">
          <div class="nb-card h-100 d-flex flex-column p-4">
            <div class="d-flex justify-content-between align-items-start mb-3">
              <h5 class="nb-cell-bold text-blue mb-0" style="font-size: 1.3rem;">{{ drive.job_title }}</h5>
              <span class="nb-badge nb-badge-green">{{ drive.status ? drive.status.toUpperCase() : '' }}</span>
            </div>
            
            <h6 class="nb-cell-bold mb-3" style="font-size: 1.1rem;">{{ drive.company_name }}</h6>
            
            <div class="mb-3">
              <div class="mb-1"><span class="nb-subtitle" style="font-size: 0.9rem;">Req. CGPA:</span> <span class="nb-cell-bold">{{ drive.cgpa_required }}</span></div>
              <div><span class="nb-subtitle" style="font-size: 0.9rem;">Batch:</span> <span class="nb-cell-bold">{{ drive.eligible_year }}</span></div>
            </div>

            <p class="nb-subtitle small mb-4 flex-grow-1" style="font-size: 0.95rem; color: #555;">{{ drive.job_description }}</p>
            
            <button class="nb-button w-100 nb-button-blue" @click="apply(drive.drive_id)">
              Apply Now
            </button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import StudentNavBar from '@/components/StudentNavBar.vue';
import api from '@/services/api';

const drives = ref([]);
const loaded = ref(false);
const searchQuery = ref('');

const filteredDrives = computed(() => {
  if (!searchQuery.value) return drives.value;
  const q = searchQuery.value.toLowerCase();
  return drives.value.filter(d => 
    d.job_title.toLowerCase().includes(q) || 
    d.company_name.toLowerCase().includes(q)
  );
});

const loadDrives = async () => {
  try {
    const res = await api.get('/student/drives');
    drives.value = res.data;
    loaded.value = true;
  } catch (err) {
    console.error('[ERROR] Failed to load drives:', err);
    loaded.value = true;
  }
};

const apply = async (driveId) => {
  try {
    const res = await api.put('/student/drives', { drive_id: driveId });
    alert(res.data.message || 'Applied successfully!');
    await loadDrives();
  } catch (err) {
    alert(err.response?.data?.message || 'Failed to apply.');
  }
};

onMounted(() => {
  loadDrives();
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

.nb-cell-bold { font-weight: 900; color: #323232; }

.text-blue { color: #2d8cf0; }

.nb-badge-green  { background: #58cc02; color: white; border: 2px solid #323232; }
</style>