<script setup>
import { ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function submit() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(username.value, password.value)
    router.push(route.query.redirect || '/')
  } catch {
    error.value = '아이디 또는 비밀번호가 올바르지 않습니다.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="auth-card">
      <RouterLink to="/" class="logo">fin<span>edu</span></RouterLink>
      <p class="lead">다시 만나서 반가워요</p>

      <form @submit.prevent="submit">
        <input v-model="username" placeholder="아이디를 입력해주세요" autocomplete="username" />
        <input
          v-model="password"
          type="password"
          placeholder="비밀번호를 입력해주세요"
          autocomplete="current-password"
        />

        <label class="keep">
          <input type="checkbox" /> 로그인 상태 유지
        </label>

        <p v-if="error" class="err">{{ error }}</p>

        <button class="btn btn-navy btn-block" type="submit" :disabled="loading">
          {{ loading ? '로그인 중...' : '로그인' }}
        </button>
      </form>

      <div class="links">
        <RouterLink to="/signup">회원가입</RouterLink>
        <span>·</span>
        <a href="#">아이디 찾기</a>
        <span>·</span>
        <a href="#">비밀번호 찾기</a>
      </div>

      <div class="divider"><span>SNS 계정으로 간편 로그인</span></div>

      <button class="btn social naver">N&nbsp; 네이버 로그인</button>
      <button class="btn social kakao">💬&nbsp; 카카오 로그인</button>
    </div>
  </div>
</template>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  background: var(--bg);
  padding: 40px 16px;
}
.auth-card {
  width: 100%;
  max-width: 380px;
  background: #fff;
  border: 1px solid var(--line);
  border-radius: 18px;
  padding: 40px 34px;
  box-shadow: var(--shadow);
  text-align: center;
}
.logo {
  font-size: 1.9rem;
  font-weight: 800;
  color: var(--navy);
  letter-spacing: -1px;
}
.logo span {
  color: var(--teal);
}
.lead {
  color: var(--text-sub);
  font-size: 0.88rem;
  margin: 8px 0 26px;
}
form {
  display: flex;
  flex-direction: column;
  gap: 10px;
  text-align: left;
}
input[type='text'],
input:not([type]),
input[type='password'] {
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  padding: 13px 14px;
  font-size: 0.9rem;
  outline: none;
}
input:focus {
  border-color: var(--navy);
}
.keep {
  font-size: 0.8rem;
  color: var(--text-sub);
  display: flex;
  align-items: center;
  gap: 6px;
}
.keep input {
  width: auto;
}
.err {
  color: #dc2626;
  font-size: 0.8rem;
}
form .btn {
  margin-top: 6px;
}
.links {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin: 18px 0;
  font-size: 0.8rem;
  color: var(--text-mute);
}
.links a:hover {
  color: var(--navy);
}
.divider {
  position: relative;
  margin: 16px 0;
  font-size: 0.76rem;
  color: var(--text-mute);
}
.divider::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background: var(--line);
}
.divider span {
  position: relative;
  background: #fff;
  padding: 0 12px;
}
.social {
  width: 100%;
  margin-top: 8px;
  font-weight: 700;
}
.social.naver {
  background: var(--naver);
  color: #fff;
}
.social.kakao {
  background: var(--kakao);
  color: #3c1e1e;
}
</style>
