<script setup>
import { ref, onMounted } from 'vue';
import CompanyNavBar from '@/components/CompanyNavBar.vue';
import api from '@/services/api';

const profile = ref({
  name: '',
  email: ''
});

const loaded = ref(false);
const saving = ref(false);
const message = ref({ text: '', type: '' });

const loadProfile = async () => {
  try {
    const res = await api.get('/company/profile');
    profile.value = {
        name: res.data.name,
        email: res.data.email
    };
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
    await api.put('/company/profile', profile.value);
    
    // Update local storage username since the top right relies on it
    if (profile.value.name) {
        localStorage.setItem('username', profile.value.name);
    }
    message.value = { text: 'Company profile updated! ✨', type: 'success' };
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
    <CompanyNavBar />
    
    <main class="container py-5">
      <div class="row justify-content-center">
        <div class="col-lg-8">
          <div class="nb-header mb-5 text-center text-lg-start d-block">
            <h1 class="nb-title">Company Profile</h1>
            <p class="nb-subtitle">Review or revise your registered company organization profile details.</p>
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
                  <label class="nb-card-label d-block mb-2">Company Registered Name</label>
                  <input v-model="profile.name" type="text" disabled class="nb-input w-100" style="background-color: #f0f0f0; opacity: 0.8;" />
                </div>

                <div class="col-md-6">
                  <label class="nb-card-label d-block mb-2">Organization Email</label>
                  <input v-model="profile.email" type="email" disabled class="nb-input w-100" style="background-color: #f0f0f0; opacity: 0.8;" />
                </div>

                <div class="col-12 mt-4 text-center">
                    <p class="nb-card-label" style="color: #ff5c5c; font-weight: 900;">Profile is read-only. Contact Admin to request changes.</p>
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

.w-100 { width: 100%; }
</style>
