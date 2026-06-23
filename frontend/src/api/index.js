import axios from 'axios'

// Django REST API 기본 주소
const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api',
})

// 저장된 JWT access 토큰을 모든 요청에 자동 첨부
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default api
