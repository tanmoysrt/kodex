import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/:info',
    name: 'Exam',
    component: () => import('@/views/pages/Exam.vue')
  }
]

let router = createRouter({
  history: createWebHistory('/frontend'),
  routes
})

export default router
