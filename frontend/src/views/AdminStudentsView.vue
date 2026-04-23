<script setup>
import { ref, onMounted, watch } from 'vue';
import NavBar from '@/components/NavBar.vue';
import api from '@/services/api';

const students  = ref([]);
const total     = ref(0);
const pages     = ref(1);
const page      = ref(1);
const search    = ref('');
const loading   = ref(false);
const error     = ref('');

const fetchStudents = async () => {
  loading.value = true;
  error.value   = '';
  try {
    const res = await api.get('/admin/students', {
      params: { page: page.value, per_page: 20, q: search.value }
    });
    students.value = res.data.students;
    total.value    = res.data.total;
    pages.value    = res.data.pages;
  } catch {
    error.value = 'Failed to load student list.';
  } finally {
    loading.value = false;
  }
};

// Debounce search input
let debounceTimer = null;
watch(search, () => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    page.value = 1;
    fetchStudents();
  }, 400);
});

const prevPage = () => { if (page.value > 1) { page.value--; fetchStudents(); } };
const nextPage = () => { if (page.value < pages.value) { page.value++; fetchStudents(); } };

const toggleStatus = async (student) => {
  try {
    const newStatus = !student.active;
    await api.put('/admin/students', {
      user_id: student.user_id,
      active: newStatus
    });
    student.active = newStatus;
  } catch {
    alert('Failed to update student status.');
  }
};

onMounted(fetchStudents);
</script>

<template>
  <div class="page">
    <NavBar />

    <main class="main">
      <!-- Header -->
      <section class="page-header box">
        <div>
          <h1 class="page-title">▤ STUDENT MANAGEMENT</h1>
          <p class="page-sub">{{ total.toLocaleString() }} registered students</p>
        </div>
      </section>

      <!-- Search Bar -->
      <div class="search-row">
        <input
          class="search-input"
          v-model="search"
          placeholder="Search by username or email..."
          type="text"
        />
      </div>

      <!-- Error -->
      <div v-if="error" class="error-box box">{{ error }}</div>

      <!-- Loading -->
      <div v-if="loading" class="loading-box">Fetching students...</div>

      <!-- Students Table-like List -->
      <div v-else-if="students.length" class="student-list">
        <div v-for="student in students" :key="student.user_id" class="box student-card">
          <div class="student-info">
            <div class="student-main">
              <h3 class="student-name">{{ student.name }}</h3>
              <span class="student-id">ID: {{ student.user_id }}</span>
              <span class="status-tag" :class="student.active ? 'active' : 'inactive'">
                {{ student.active ? 'ACTIVE' : 'INACTIVE' }}
              </span>
            </div>
            <p class="student-email">{{ student.email }}</p>
            <p v-if="student.headline" class="student-headline">"{{ student.headline }}"</p>
            <div v-if="student.location" class="student-meta">
              <span>📍 {{ student.location }}</span>
            </div>
          </div>
          <div class="student-actions">
            <button
              class="brutal-btn status-btn"
              :class="student.active ? 'deactivate' : 'activate'"
              @click="toggleStatus(student)"
            >
              {{ student.active ? 'DEACTIVATE' : 'ACTIVATE' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Empty state -->
      <div v-else class="empty-box box">
        <p>No students found matches your search.</p>
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
.main { max-width: 1100px; width: 100%; margin: 0 auto; padding: 28px 28px 60px; display: flex; flex-direction: column; gap: 20px; }
.page-header  { padding: 20px 24px; }
.page-title   { font-size: 28px; font-weight: 900; text-transform: uppercase; }
.page-sub     { font-size: 13px; font-weight: 600; opacity: 0.6; margin-top: 4px; }
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
.error-box   { padding: 16px; color: var(--accent); font-weight: 700; }
.loading-box { text-align: center; font-weight: 700; padding: 40px; opacity: 0.5; }

.student-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.student-card {
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  background: #fafafa;
}
.student-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.student-main {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}
.student-name {
  font-size: 18px;
  font-weight: 900;
  margin: 0;
}
.student-id {
  font-size: 11px;
  font-weight: 800;
  opacity: 0.5;
  background: #eee;
  padding: 2px 6px;
}
.status-tag {
  font-size: 10px;
  font-weight: 900;
  padding: 2px 8px;
  border: 1px solid var(--ink);
}
.status-tag.active { background: #55efc4; }
.status-tag.inactive { background: #fab1a0; }

.student-email {
  font-size: 14px;
  font-weight: 700;
  opacity: 0.8;
  margin: 0;
}
.student-headline {
  font-size: 13px;
  font-style: italic;
  font-weight: 600;
  opacity: 0.6;
  margin: 4px 0;
}
.student-meta {
  font-size: 12px;
  font-weight: 700;
  opacity: 0.7;
  margin-top: 4px;
}

.student-actions {
  display: flex;
  align-items: center;
}

.status-btn {
  font-size: 11px;
  padding: 6px 12px;
}

.status-btn.activate {
  background: #55efc4;
}

.status-btn.deactivate {
  background: #fab1a0;
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

@media (max-width: 640px) {
  .student-main { gap: 8px; }
}
</style>
