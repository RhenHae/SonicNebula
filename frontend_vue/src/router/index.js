import { createRouter, createWebHistory } from 'vue-router'

const routes =[
  { path: '/', redirect: '/intro' },
  { path: '/intro', name: 'Intro', component: () => import('../views/Intro.vue'), meta: { transition: 'fade' } },
  { path: '/explorer', name: 'Explorer', component: () => import('../views/Explorer.vue') },
  { path: '/analysis', name: 'Analysis', component: () => import('../views/Analysis.vue') },
  { path: '/studio', name: 'Studio', component: () => import('../views/AiStudio.vue') } // ✅ 新增
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router