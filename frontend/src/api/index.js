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

// 만료/무효 토큰(401)이면 토큰을 비워 공개 콘텐츠는 계속 볼 수 있게 한다
api.interceptors.response.use(
  (res) => res,
  (error) => {
    if (error.response?.status === 401 && localStorage.getItem('access')) {
      localStorage.removeItem('access')
      localStorage.removeItem('refresh')
    }
    return Promise.reject(error)
  }
)

export default api
