import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  { path: '/', name: 'home', component: () => import('@/views/HomeView.vue') },
  {
    path: '/lobby/:id',
    name: 'lobby',
    component: () => import('@/views/LobbyView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/game/:id',
    name: 'game',
    component: () => import('@/views/GameView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/result/:id',
    name: 'result',
    component: () => import('@/views/ResultView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/admin',
    name: 'admin',
    component: () => import('@/views/admin/AdminDashboard.vue'),
    meta: { requiresAuth: true, requiresWriter: true },
  },
  {
    path: '/admin/genres',
    name: 'admin-genres',
    component: () => import('@/views/admin/GenreManager.vue'),
    meta: { requiresAuth: true, requiresWriter: true },
  },
  {
    path: '/admin/scenario/:id',
    name: 'admin-scenario',
    component: () => import('@/views/admin/ScenarioEditor.vue'),
    meta: { requiresAuth: true, requiresWriter: true },
  },
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.isAuthenticated) return { name: 'home' }
  if (to.meta.requiresWriter && !auth.isWriter) return { name: 'home' }
  return true
})
