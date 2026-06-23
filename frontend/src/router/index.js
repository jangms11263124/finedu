import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
    },
    {
      path: '/signup',
      name: 'signup',
      component: () => import('@/views/SignupView.vue'),
    },
    {
      path: '/contents',
      name: 'contents',
      component: () => import('@/views/ContentsView.vue'),
    },
    {
      path: '/contents/:id',
      name: 'content-detail',
      component: () => import('@/views/ContentDetailView.vue'),
    },
    {
      path: '/events',
      name: 'events',
      component: () => import('@/views/EventsView.vue'),
    },
    {
      path: '/glossary',
      name: 'glossary',
      component: () => import('@/views/GlossaryView.vue'),
    },
    {
      path: '/community',
      name: 'community',
      component: () => import('@/views/CommunityView.vue'),
    },
    {
      path: '/community/ranking',
      name: 'community-ranking',
      component: () => import('@/views/CommunityRankingView.vue'),
    },
    {
      path: '/community/write',
      name: 'post-create',
      component: () => import('@/views/PostFormView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/community/:id',
      name: 'post-detail',
      component: () => import('@/views/PostDetailView.vue'),
    },
    {
      path: '/community/:id/edit',
      name: 'post-edit',
      component: () => import('@/views/PostFormView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/ebti',
      name: 'ebti',
      component: () => import('@/views/EbtiView.vue'),
      meta: { requiresAuth: true },
    },
  ],
  scrollBehavior() {
    return { top: 0 }
  },
})

// 로그인이 필요한 페이지 보호 (예: EBTI 테스트)
router.beforeEach((to) => {
  if (to.meta.requiresAuth && !useAuthStore().isLoggedIn) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
})

export default router
