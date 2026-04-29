import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'unlock',
      component: () => import('@/views/Unlock.vue'),
    },
    {
      path: '/app',
      name: 'app',
      component: () => import('@/views/AppView.vue'),
    },
  ],
})

export default router
