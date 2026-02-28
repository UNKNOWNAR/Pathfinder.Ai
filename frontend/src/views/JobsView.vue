<template>
  <div class="page">
    <NavBar />
    <div class="content">
      <div class="header">
        <h1 class="title">Student Job Feed</h1>
        <p class="sub">View all available career opportunities tailored for you.</p>
      </div>

      <div class="controls">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search for jobs, companies, or locations..."
          class="search-bar"
          @keyup.enter="fetchJobs"
        />
        <button class="btn search-btn" @click="fetchJobs">Search</button>
      </div>

      <div class="jobs-list" v-if="jobs.length > 0">
        <div class="job-card" v-for="job in jobs" :key="job.job_id">
          <div class="job-header">
            <h2 class="job-title">{{ job.title }}</h2>
            <span class="source-badge" :class="job.source.toLowerCase()">{{ job.source }}</span>
          </div>
          <p class="company-name">{{ job.company }} &mdash; <span>{{ job.location || 'Remote' }}</span></p>
          <div class="job-desc" v-html="truncateDesc(job.description)"></div>
          <div class="job-actions">
            <a v-if="job.url" :href="job.url" target="_blank" class="btn link-btn">Apply / View Source</a>
            <span v-else class="btn link-btn disabled">Apply / View Source</span>
          </div>
        </div>
      </div>

      <div v-else-if="!loading" class="no-jobs">
        <p>No jobs found. Try adjusting your search.</p>
      </div>

      <div class="pagination" v-if="totalPages > 1">
        <button class="btn page-btn" :disabled="currentPage === 1" @click="changePage(currentPage - 1)">Previous</button>
        <span class="page-info">Page {{ currentPage }} of {{ totalPages }}</span>
        <button class="btn page-btn" :disabled="currentPage === totalPages" @click="changePage(currentPage + 1)">Next</button>
      </div>

      <div v-if="loading" class="loading-state">
        <p>Loading jobs...</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import NavBar from '@/components/NavBar.vue';

const jobs = ref([]);
const searchQuery = ref('');
const currentPage = ref(1);
const totalPages = ref(1);
const loading = ref(false);

const fetchJobs = async () => {
  loading.value = true;
  try {
    const token = localStorage.getItem('token');
    const response = await fetch(`http://localhost:5000/api/jobs?page=${currentPage.value}&q=${encodeURIComponent(searchQuery.value)}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (!response.ok) {
      console.error('Failed to fetch jobs');
      return;
    }

    const data = await response.json();
    jobs.value = data.jobs;
    totalPages.value = data.pages;
    currentPage.value = data.page;
  } catch (err) {
    console.error('Error fetching jobs:', err);
  } finally {
    loading.value = false;
  }
};

const changePage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page;
    fetchJobs();
    window.scrollTo(0, 0);
  }
};

const truncateDesc = (desc) => {
  if (!desc) return 'No description available.';
  // Strip basic HTML if any and truncate
  const temp = document.createElement('div');
  temp.innerHTML = desc;
  const text = temp.textContent || temp.innerText || '';
  if (text.length > 250) {
    return text.substring(0, 250) + '...';
  }
  return text;
};

onMounted(() => {
  fetchJobs();
});
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #DEDEDE;
}
.content {
  padding: 40px;
  max-width: 900px;
  margin: 0 auto;
}
.header {
  margin-bottom: 30px;
}
.title {
  font-size: 40px;
  font-weight: 900;
  text-transform: uppercase;
  margin-bottom: 10px;
}
.sub {
  font-size: 16px;
  font-weight: 600;
  opacity: 0.7;
}

.controls {
  display: flex;
  gap: 15px;
  margin-bottom: 30px;
}
.search-bar {
  flex-grow: 1;
  padding: 12px 20px;
  border: 2px solid #111;
  box-shadow: 4px 4px 0 #111;
  font-family: inherit;
  font-size: 16px;
  font-weight: 600;
  outline: none;
}
.search-bar:focus {
  transform: translate(-2px, -2px);
  box-shadow: 6px 6px 0 #111;
}
.btn {
  background: #fff;
  border: 2px solid #111;
  box-shadow: 4px 4px 0 #111;
  padding: 12px 24px;
  font-family: inherit;
  font-weight: 800;
  text-transform: uppercase;
  cursor: pointer;
  transition: all 0.1s;
  text-decoration: none;
  display: inline-block;
  color: #111;
}
.btn:active {
  transform: translate(2px, 2px);
  box-shadow: 2px 2px 0 #111;
}
.btn:disabled, .btn.disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
  box-shadow: 4px 4px 0 #111;
  opacity: 0.7;
}

.search-btn {
  background: #34d399; /* Neo-brutalist green */
}

.jobs-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.job-card {
  background: #fff;
  border: 2px solid #111;
  box-shadow: 5px 5px 0 #111;
  padding: 25px;
}
.job-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}
.job-title {
  font-size: 24px;
  font-weight: 900;
  margin: 0;
}
.source-badge {
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
  padding: 4px 8px;
  border: 2px solid #111;
  background: #e5e7eb;
}
.source-badge.remotive { background: #60a5fa; }
.source-badge.jsearch { background: #f472b6; }
.source-badge.activejobsdb { background: #fbbf24; }
.source-badge.direct { background: #34d399; } /* Company posted */

.company-name {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 15px;
}
.company-name span {
  font-weight: 600;
  opacity: 0.8;
  font-style: italic;
}

.job-desc {
  font-size: 15px;
  line-height: 1.5;
  margin-bottom: 20px;
  color: #333;
}

.job-actions {
  display: flex;
  justify-content: flex-end;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin-top: 40px;
}
.page-info {
  font-weight: 800;
  font-size: 16px;
}

.no-jobs, .loading-state {
  text-align: center;
  padding: 50px;
  background: #fff;
  border: 2px solid #111;
  box-shadow: 5px 5px 0 #111;
  font-weight: 800;
  font-size: 18px;
}
</style>
