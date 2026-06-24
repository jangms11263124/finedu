import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import api from '@/api'

export const useAuthStore = defineStore('auth', () => {
  const access = ref(localStorage.getItem('access') || '')
  const user = ref(null)

  const isLoggedIn = computed(() => !!access.value)

  function setToken(token) {
    access.value = token
    localStorage.setItem('access', token)
  }

  async function login(username, password) {
    // 이전 세션의 EBTI 캐시가 새 계정으로 새지 않도록 먼저 비운다.
    localStorage.removeItem('ebtiResult')
    const { data } = await api.post('/accounts/login/', { username, password })
    setToken(data.access)
    localStorage.setItem('refresh', data.refresh)
    await fetchMe()
  }

  async function signup(payload) {
    await api.post('/accounts/register/', payload)
    // 가입 직후 자동 로그인
    await login(payload.username, payload.password)
  }

  async function fetchMe() {
    if (!access.value) return
    try {
      const { data } = await api.get('/accounts/me/')
      user.value = data
    } catch {
      logout()
    }
  }

  async function updateProfile(payload) {
    // payload가 FormData면 프로필 이미지 업로드(멀티파트), 아니면 일반 JSON
    const { data } = await api.patch('/accounts/me/', payload)
    user.value = data
    return data
  }

  function logout() {
    access.value = ''
    user.value = null
    localStorage.removeItem('access')
    localStorage.removeItem('refresh')
    // EBTI 결과는 계정별 데이터이므로 로그아웃 시 함께 비워 다음 계정으로 새지 않게 한다.
    localStorage.removeItem('ebtiResult')
    // AI 추천 캐시도 비운다 (순환 import 방지를 위해 동적 import).
    import('@/stores/recommend').then((m) => m.useRecommendStore().reset())
  }

  return { access, user, isLoggedIn, login, signup, fetchMe, updateProfile, logout }
})
