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
  }

  return { access, user, isLoggedIn, login, signup, fetchMe, updateProfile, logout }
})
