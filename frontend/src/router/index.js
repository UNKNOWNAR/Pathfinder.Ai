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
    path: '/student',
    name: 'student',
    component: () => import('../views/DashboardView.vue')
  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import('../views/ProfileView.vue')
  },
  {
    path: '/jobs',
    name: 'jobs',
    component: () => import('../views/JobsView.vue')
  },
  {
    path: '/leetcode',
    name: 'leetcode',
    component: () => import('../views/LeetCodeView.vue')
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
      if (role === 'student') return next('/student');
      if (role === 'company') return next('/company');
    }
    return next();
  }

  if (!token) {
    return next('/login');
  }

  if (to.meta.requiresAdmin && role !== 'admin') {
    return next('/student');
  }

  // Prevent admins from accidentally landing on student pages
  if (role === 'admin' && !to.path.startsWith('/admin')) {
    return next('/admin');
  }

  // Prevent students/companies from landing on admin wrapper implicitly
  if (role !== 'admin' && to.path.startsWith('/admin')) {
    return next(`/${role}`);
  }

  next();
});

export default router;