import { createApp } from 'vue'
import { createPinia } from 'pinia'
import './style.css'
import App from './App.vue'
import router from './router'
import { useAuthStore } from '@/stores/auth'

const app = createApp(App)

app.use(createPinia())
app.use(router)

// 새로고침 시 저장된 토큰으로 사용자 정보 복원
useAuthStore().fetchMe()

app.mount('#app')
