import { createRouter, createWebHashHistory } from 'vue-router';

const routes = [
  { path: '/', redirect: '/login' },

  // ── Auth ──
  {
    path: '/login',
    name: 'login',
    meta: { guest: true },
    component: () => import('../views/LoginView.vue')
  },

  // ── Student ──
  {
    path: '/dashboard',
    name: 'student-dashboard',
    meta: { requiresAuth: true, role: 'student' },
    component: () => import('../views/students/StudentDashboard.vue')
  },
  {
    path: '/placement-drives',
    name: 'placement-drives',
    meta: { requiresAuth: true, role: 'student' },
    component: () => import('../views/students/StudentPlacementView.vue')
  },
  {
    path: '/my-applications',
    name: 'my-applications',
    meta: { requiresAuth: true, role: 'student' },
    component: () => import('../views/students/MyApplications.vue')
  },
  {
    path: '/student/profile',
    name: 'student-profile',
    meta: { requiresAuth: true, role: 'student' },
    component: () => import('../views/students/StudentProfile.vue')
  },

  // ── Admin ──
  {
    path: '/admin/dashboard',
    name: 'admin-dashboard',
    meta: { requiresAuth: true, role: 'admin' },
    component: () => import('../views/admin/AdminDashboard.vue')
  },
  {
    path: '/admin/placement-drives',
    name: 'admin-placement-drives',
    meta: { requiresAuth: true, role: 'admin' },
    component: () => import('../views/admin/AdminPlacementDrive.vue')
  },
  {
    path: '/admin/companies',
    name: 'admin-companies',
    meta: { requiresAuth: true, role: 'admin' },
    component: () => import('../views/admin/AdminCompaniesView.vue')
  },
  {
    path: '/admin/students',
    name: 'admin-students',
    meta: { requiresAuth: true, role: 'admin' },
    component: () => import('../views/admin/AdminStudents.vue')
  },

  // ── Company ──
  {
    path: '/company/dashboard',
    name: 'company-dashboard',
    meta: { requiresAuth: true, role: 'company' },
    component: () => import('../views/company/CompanyDashboard.vue')
  },
  {
    path: '/company/create-drive',
    name: 'company-create-drive',
    meta: { requiresAuth: true, role: 'company' },
    component: () => import('../views/company/CompanyCreateDrive.vue')
  },
  {
    path: '/company/drive/:id/applicants',
    name: 'company-applicants',
    meta: { requiresAuth: true, role: 'company' },
    component: () => import('../views/company/CompanyApplicants.vue')
  },
  {
    path: '/company/applicants',
    name: 'company-all-applicants',
    meta: { requiresAuth: true, role: 'company' },
    component: () => import('../views/company/CompanyAllApplicants.vue')
  },
  {
    path: '/company/drives',
    name: 'company-drives',
    meta: { requiresAuth: true, role: 'company' },
    component: () => import('../views/company/CompanyDrivesView.vue')
  },
  {
    path: '/company/profile',
    name: 'company-profile',
    meta: { requiresAuth: true, role: 'company' },
    component: () => import('../views/company/CompanyProfile.vue')
  },
];

const router = createRouter({
  history: createWebHashHistory(),
  routes
});

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token');
  const role = localStorage.getItem('role');

  if (to.meta.requiresAuth && !token) {
    return next({ name: 'login' });
  }

  if (to.meta.role && to.meta.role !== role) {
    return next({ name: 'login' });
  }

  if (to.meta.guest && token) {
    // Redirect logged-in users away from login page
    if (role === 'admin') return next({ name: 'admin-dashboard' });
    if (role === 'company') return next({ name: 'company-dashboard' });
    return next({ name: 'student-dashboard' });
  }

  next();
});

export default router;