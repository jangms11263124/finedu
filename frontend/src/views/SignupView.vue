<script setup>
import { ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

const form = ref({
  username: '',
  email: '',
  nickname: '',
  password: '',
  password2: '',
})
const errors = ref({})
const loading = ref(false)

async function submit() {
  errors.value = {}
  loading.value = true
  try {
    await auth.signup(form.value)
    router.push('/')
  } catch (e) {
    errors.value = e.response?.data || { detail: '회원가입에 실패했습니다.' }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="auth-card">
      <RouterLink to="/" class="logo">fin<span>edu</span></RouterLink>
      <p class="lead">finedu와 함께 금융 공부를 시작해보세요</p>

      <form @submit.prevent="submit">
        <label>아이디</label>
        <input v-model="form.username" placeholder="아이디를 입력해주세요" />
        <small v-if="errors.username" class="err">{{ errors.username[0] }}</small>

        <label>이메일</label>
        <input v-model="form.email" type="email" placeholder="이메일을 입력해주세요" />
        <small v-if="errors.email" class="err">{{ errors.email[0] }}</small>

        <label>닉네임</label>
        <input v-model="form.nickname" placeholder="닉네임을 입력해주세요" />

        <label>비밀번호</label>
        <input v-model="form.password" type="password" placeholder="비밀번호를 입력해주세요" />
        <small v-if="errors.password" class="err">{{ errors.password[0] }}</small>

        <label>비밀번호 확인</label>
        <input v-model="form.password2" type="password" placeholder="비밀번호를 다시 입력해주세요" />
        <small v-if="errors.password2" class="err">{{ errors.password2[0] }}</small>

        <small v-if="errors.detail" class="err">{{ errors.detail }}</small>

        <button class="btn btn-navy btn-block" type="submit" :disabled="loading">
          {{ loading ? '가입 중...' : '회원가입' }}
        </button>
      </form>

      <div class="divider"><span>SNS 계정으로 간편 가입</span></div>
      <button class="btn social naver">N&nbsp; 네이버로 시작하기</button>
      <button class="btn social kakao">💬&nbsp; 카카오로 시작하기</button>

      <p class="to-login">
        이미 계정이 있으신가요? <RouterLink to="/login">로그인</RouterLink>
      </p>
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
  max-width: 420px;
  background: #fff;
  border: 1px solid var(--line);
  border-radius: 18px;
  padding: 38px 34px;
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
  font-size: 0.86rem;
  margin: 8px 0 24px;
}
form {
  display: flex;
  flex-direction: column;
  text-align: left;
}
label {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-sub);
  margin: 12px 0 5px;
}
input {
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  padding: 12px 14px;
  font-size: 0.9rem;
  outline: none;
}
input:focus {
  border-color: var(--navy);
}
.err {
  color: #dc2626;
  font-size: 0.75rem;
  margin-top: 4px;
}
form .btn {
  margin-top: 22px;
}
.divider {
  position: relative;
  margin: 22px 0 14px;
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
.to-login {
  margin-top: 20px;
  font-size: 0.82rem;
  color: var(--text-sub);
}
.to-login a {
  color: var(--navy);
  font-weight: 700;
}
</style>
