import { createRouter, createWebHistory } from 'vue-router'

const routes =[
  { path: '/', redirect: '/intro' }, // 默认进入简介页
  { 
    path: '/intro', 
    name: 'Intro', 
    component: () => import('../views/Intro.vue'),
    meta: { transition: 'fade' }
  },
  { 
    path: '/explorer', 
    name: 'Explorer', 
    component: () => import('../views/Explorer.vue') 
  },
  { 
    path: '/analysis', 
    name: 'Analysis', 
    component: () => import('../views/Analysis.vue') 
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router