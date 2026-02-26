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
  }

];

const router = createRouter({
  history: createWebHashHistory(),
  routes
});

export default router;