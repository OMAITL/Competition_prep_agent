import { createRouter, createWebHistory } from 'vue-router'
import AppLayout from '@/layouts/AppLayout.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: AppLayout,
      children: [
        { path: '', name: 'dashboard', component: () => import('@/views/DashboardView.vue') },
        { path: 'competitions', name: 'competitions', component: () => import('@/views/CompetitionsView.vue') },
        { path: 'intake', name: 'intake', component: () => import('@/views/IntakeView.vue') },
        { path: 'generate', name: 'generate', component: () => import('@/views/GenerateView.vue') },
        { path: 'result', name: 'result', component: () => import('@/views/ResultView.vue') },
      ],
    },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
  scrollBehavior: () => ({ top: 0 }),
})

export default router
