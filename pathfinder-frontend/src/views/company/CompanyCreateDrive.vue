<template>
  <div class="main-wrapper">
    <CompanyNavBar />

    <main class="container py-5">
      <div class="row justify-content-center">
        <div class="col-md-8 col-lg-6">
          <div class="mb-4">
            <router-link to="/company/dashboard" class="nb-subtitle" style="text-decoration: none; font-size: 0.95rem;">← Back to Dashboard</router-link>
            <h1 class="nb-title mt-2">Post New Drive</h1>
            <p class="nb-subtitle">Create a new recruitment opportunity for qualified students.</p>
          </div>

          <div class="nb-card p-4">
            <form @submit.prevent="submitDrive">
              <!-- Job Title -->
              <div class="mb-3">
                <label class="nb-card-label d-block mb-2">Job Title</label>
                <input 
                  v-model="form.job_title" 
                  type="text" 
                  class="nb-input" 
                  placeholder="e.g. Senior Software Engineer" 
                  required 
                />
              </div>

              <!-- Description -->
              <div class="mb-3">
                <label class="nb-card-label d-block mb-2">Job Description</label>
                <textarea 
                  v-model="form.job_description" 
                  class="nb-input" 
                  style="height: auto; min-height: 100px; padding-top: 10px;"
                  rows="4" 
                  placeholder="Describe the role and responsibilities..." 
                  required
                ></textarea>
              </div>

              <div class="row">
                <!-- Branch -->
                <div class="col-md-6 mb-3">
                  <label class="nb-card-label d-block mb-2">Eligible Branch</label>
                  <select v-model="form.eligible_branch" class="nb-input" style="appearance: auto;" required>
                    <option value="All">All Branches</option>
                    <option value="Computer Science">Computer Science</option>
                    <option value="Information Technology">Information Technology</option>
                    <option value="Electronics">Electronics</option>
                    <option value="Mechanical">Mechanical</option>
                    <option value="Civil">Civil</option>
                  </select>
                </div>

                <!-- CGPA -->
                <div class="col-md-6 mb-3">
                  <label class="nb-card-label d-block mb-2">Min. CGPA Required</label>
                  <input 
                    v-model.number="form.cgpa_required" 
                    type="number" 
                    step="0.1" 
                    min="0" 
                    max="10" 
                    class="nb-input" 
                    required 
                  />
                </div>
              </div>

              <!-- Year -->
              <div class="mb-4">
                <label class="nb-card-label d-block mb-2">Eligible Batch Year</label>
                <input 
                  v-model.number="form.eligible_year" 
                  type="number" 
                  class="nb-input" 
                  placeholder="e.g. 2024" 
                  required 
                />
              </div>

              <div class="d-grid mt-4">
                <button type="submit" class="nb-button nb-button-blue w-100" style="height: 50px; font-size: 1.1rem;" :disabled="submitting">
                  {{ submitting ? 'Posting...' : 'Post Placement Drive' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import CompanyNavBar from '@/components/CompanyNavBar.vue';
import api from '@/services/api';

const router = useRouter();
const submitting = ref(false);

const form = ref({
  job_title: '',
  job_description: '',
  eligible_branch: 'All',
  cgpa_required: 6.0,
  eligible_year: 2024
});

const submitDrive = async () => {
  submitting.value = true;
  try {
    await api.post('/company/drive', form.value);
    alert('Drive successfully sent to Admin for approval! 🚀');
    router.push('/company/dashboard');
  } catch (err) {
    alert(err.response?.data?.message || 'Failed to post drive.');
  } finally {
    submitting.value = false;
  }
};
</script>

<style scoped>
.main-wrapper {
  background-color: var(--main-bg);
  min-height: 100vh;
}
.nb-title { font-size: 2.5rem; font-weight: 900; margin: 0; }
.nb-subtitle { font-weight: 600; color: #666; font-size: 1.1rem; }
.nb-card-label { text-transform: uppercase; font-weight: 900; opacity: 0.8; font-size: 0.9rem; color: #323232; }
</style>
