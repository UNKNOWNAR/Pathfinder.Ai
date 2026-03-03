import { createRouter, createWebHashHistory } from 'vue-router';
import LoginView from '../views/LoginView.vue';

import HomeView from '../views/HomeView.vue';

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView
  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import('../views/ProfileView.vue')
  },
  {
    path: '/jobs',
    alias: '/student',
    name: 'jobs',
    component: () => import('../views/JobsView.vue')
  },
  {
    path: '/leetcode',
    name: 'leetcode',
    component: () => import('../views/LeetCodeView.vue')
  },
  {
    path: '/interview',
    name: 'interview',
    component: () => import('../views/InterviewView.vue')
  },
  {
    path: '/admin',
    name: 'admin',
    component: () => import('../views/AdminDashboardView.vue'),
    meta: { requiresAdmin: true }
  },
  {
    path: '/admin/jobs',
    name: 'admin-jobs',
    component: () => import('../views/AdminJobsView.vue'),
    meta: { requiresAdmin: true }
  },
  {
    path: '/admin/harvesters',
    name: 'admin-harvesters',
    component: () => import('../views/AdminHarvestersView.vue'),
    meta: { requiresAdmin: true }
  },
  {
    path: '/admin/companies',
    name: 'admin-companies',
    component: () => import('../views/AdminCompaniesView.vue'),
    meta: { requiresAdmin: true }
  },
  {
    path: '/company',
    name: 'company',
    component: () => import('../views/CompanyDashboardView.vue'),
    meta: { requiresCompany: true }
  }
];

const router = createRouter({
  history: createWebHashHistory(),
  routes
});

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token');
  const role = localStorage.getItem('role');

  if (to.path === '/' || to.path === '/login') {
    if (token) {
      if (role === 'admin') return next('/admin');
      if (role === 'student') return next('/jobs');
      if (role === 'company') return next('/company');
    }
    return next();
  }

  if (!token) {
    return next('/login');
  }

  if (to.meta.requiresAdmin && role !== 'admin') {
    return next(`/${role}`);
  }

  if (to.meta.requiresCompany && role !== 'company') {
    return next(`/${role}`);
  }

  // Prevent admins from accidentally landing on student/company pages
  if (role === 'admin' && !to.path.startsWith('/admin')) {
    return next('/admin');
  }

  // Prevent companies from accidentally landing on student/admin pages
  if (role === 'company' && !to.path.startsWith('/company')) {
    return next('/company');
  }

  // Prevent students from landing on admin wrapper implicitly
  if (role === 'student' && (to.path.startsWith('/admin') || to.path.startsWith('/company'))) {
    return next('/jobs');
  }

  next();
});

export default router;