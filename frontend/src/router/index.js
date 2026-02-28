import { createRouter, createWebHashHistory } from 'vue-router';
import LoginView from '../views/LoginView.vue';

const routes = [
  { path: '/', redirect: '/dashboard' },
  {
    path: '/login',
    name: 'login',
    component: LoginView
  },
  {
    path: '/dashboard',
    name: 'dashboard',
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
  }
];

const router = createRouter({
  history: createWebHashHistory(),
  routes
});

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token');
  const role = localStorage.getItem('role');

  if (to.path !== '/login' && !token) {
    return next('/login');
  }

  if (to.meta.requiresAdmin && role !== 'admin') {
    return next('/dashboard');
  }

  next();
});

export default router;