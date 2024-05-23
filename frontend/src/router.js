import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/completed',
    name: 'Exam Completed',
    component: () => import('@/views/pages/ExamCompleted.vue')
  },
  {
    path: '/malpractice',
    name: 'Exam Completed Due To Malpractice',
    component: () => import('@/views/pages/ExamCompletedMalpractice.vue')
  },
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
