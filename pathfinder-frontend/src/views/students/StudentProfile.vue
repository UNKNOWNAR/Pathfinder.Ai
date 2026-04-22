<script setup>
import { ref, onMounted } from 'vue';
import StudentNavBar from '@/components/StudentNavBar.vue';
import api from '@/services/api';

const profile = ref({
  name: '',
  email: '',
  branch: '',
  cgpa: 0,
  batch_year: 2024
});

const loaded = ref(false);
const saving = ref(false);
const message = ref({ text: '', type: '' });

const loadProfile = async () => {
  try {
    const res = await api.get('/student/profile');
    profile.value = res.data;
    loaded.value = true;
  } catch (err) {
    console.error('[ERROR] Failed to load profile:', err);
    loaded.value = true;
  }
};

const saveProfile = async () => {
  saving.value = true;
  message.value = { text: '', type: '' };
  try {
    await api.put('/student/profile', profile.value);
    message.value = { text: 'Academic profile updated! ✨', type: 'success' };
  } catch (err) {
    message.value = { text: 'Update failed. Please check your data.', type: 'danger' };
  } finally {
    saving.value = false;
  }
};

onMounted(() => {
  loadProfile();
});
</script>

<template>
  <div class="main-wrapper">
    <StudentNavBar />
    
    <main class="container py-5">
      <div class="row justify-content-center">
        <div class="col-lg-8">
          <div class="nb-header mb-5 text-center text-lg-start d-block">
            <h1 class="nb-title">Academic Profile</h1>
            <p class="nb-subtitle">Ensure your details are correct to match with the best placement drives.</p>
          </div>

          <div v-if="!loaded" class="text-center py-5">
            <div class="nb-card p-5">Loading profile data...</div>
          </div>

          <div v-else class="nb-card p-4 p-md-5">
            <div v-if="message.text" :class="['alert-box mb-4 py-3 px-4', message.type === 'success' ? 'alert-success' : 'alert-danger']">
              <span class="nb-cell-bold">{{ message.text }}</span>
            </div>

            <form @submit.prevent="saveProfile">
              <div class="row g-4">
                <div class="col-md-6">
                  <label class="nb-card-label d-block mb-2">Full Name</label>
                  <input v-model="profile.name" type="text" disabled class="nb-input" style="background-color: #f0f0f0; opacity: 0.8;" />
                </div>

                <div class="col-md-6">
                  <label class="nb-card-label d-block mb-2">Email ID</label>
                  <input v-model="profile.email" type="email" class="nb-input" />
                </div>

                <div class="col-md-6">
                  <label class="nb-card-label d-block mb-2">Academic Branch</label>
                  <select v-model="profile.branch" class="nb-input" style="appearance: auto;">
                     <option value="Computer Science">Computer Science (CSE)</option>
                     <option value="Information Technology">Information Technology (IT)</option>
                     <option value="Electronics">Electronics (ECE)</option>
                     <option value="Mechanical">Mechanical (ME)</option>
                     <option value="Civil">Civil Engineering</option>
                  </select>
                </div>

                <div class="col-md-3">
                  <label class="nb-card-label d-block mb-2">Current CGPA</label>
                  <input v-model.number="profile.cgpa" type="number" step="0.01" class="nb-input" />
                </div>

                <div class="col-md-3">
                  <label class="nb-card-label d-block mb-2">Batch Year</label>
                  <input v-model.number="profile.batch_year" type="number" class="nb-input" />
                </div>

                <div class="col-12 mt-5">
                  <button type="submit" :disabled="saving" class="nb-button nb-button-blue w-100" style="height: 50px; font-size: 1.2rem;">
                    {{ saving ? 'Syncing...' : 'Update Records' }}
                  </button>
                </div>
              </div>
            </form>
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
  margin-bottom: 20px;
}
.nb-title { font-size: 2.5rem; font-weight: 900; margin: 0; }
.nb-subtitle { font-weight: 600; color: #666; font-size: 1.1rem; margin-top: 10px; }

.nb-card-label { text-transform: uppercase; font-weight: 900; opacity: 0.8; font-size: 0.9rem; color: #323232; }
.nb-cell-bold { font-weight: 900; color: #323232; }

.alert-box {
  border: 2px solid #323232;
  box-shadow: 4px 4px 0px #323232;
  border-radius: 5px;
}
.alert-success { background-color: #58cc02; color: #fff; }
.alert-danger { background-color: #ff5c5c; color: #fff; }
.alert-success .nb-cell-bold { color: #fff; }
.alert-danger .nb-cell-bold { color: #fff; }
</style>
