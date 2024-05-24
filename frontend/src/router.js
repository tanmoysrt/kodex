import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/dummy'
  },
  {
    path: '/:info',
    name: 'Exam',
    component: () => import('@/views/pages/Exam.vue')
  },
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
    path: '/invalid',
    name: 'Exam Invalid',
    component: () => import('@/views/pages/ExamInvalid.vue')
  },
]

let router = createRouter({
  history: createWebHistory('/kodex'),
  routes
})

export default router
