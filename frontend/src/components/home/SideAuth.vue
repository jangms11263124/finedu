<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

const username = ref('')
const password = ref('')
const error = ref('')

async function submit() {
  error.value = ''
  try {
    await auth.login(username.value, password.value)
  } catch {
    error.value = '아이디 또는 비밀번호를 확인해주세요.'
  }
}
</script>

<template>
  <!-- 로그인 상태: 프로필 카드 -->
  <div v-if="auth.isLoggedIn" class="widget profile">
    <div class="avatar">{{ (auth.user?.nickname || 'U').charAt(0) }}</div>
    <div class="who">
      <strong>{{ auth.user?.nickname }}</strong>
      <span class="lv">Lv.{{ auth.user?.level }} · {{ auth.user?.points }}P</span>
    </div>
    <div class="prof-menu">
      <a href="#">📚 내 학습</a>
      <a href="#">🔖 스크랩</a>
      <a href="#">⚙️ 설정</a>
    </div>
    <button class="logout" @click="auth.logout()">로그아웃</button>
  </div>

  <!-- 비로그인: 로그인 폼 -->
  <div v-else class="widget login">
    <form @submit.prevent="submit">
      <input v-model="username" placeholder="아이디" autocomplete="username" />
      <input
        v-model="password"
        type="password"
        placeholder="비밀번호"
        autocomplete="current-password"
      />
      <p v-if="error" class="err">{{ error }}</p>
      <button class="btn btn-navy btn-block" type="submit">로그인</button>
    </form>
    <div class="links">
      <RouterLink to="/signup">회원가입</RouterLink>
      <span>·</span>
      <a href="#">아이디 찾기</a>
      <span>·</span>
      <a href="#">비밀번호 찾기</a>
    </div>
  </div>
</template>

<style scoped>
.widget {
  background: #fff;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 18px;
  box-shadow: var(--shadow);
}
.login form {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.login input {
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  padding: 11px 12px;
  font-size: 0.88rem;
  outline: none;
}
.login input:focus {
  border-color: var(--navy);
}
.err {
  color: #dc2626;
  font-size: 0.76rem;
}
.login .btn {
  margin-top: 4px;
}
.links {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-top: 12px;
  font-size: 0.76rem;
  color: var(--text-mute);
}
.links a:hover {
  color: var(--navy);
}

/* 프로필 */
.profile {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 12px;
  align-items: center;
}
.avatar {
  width: 46px;
  height: 46px;
  border-radius: 999px;
  background: linear-gradient(135deg, var(--teal), var(--navy));
  color: #fff;
  font-weight: 800;
  display: grid;
  place-items: center;
  font-size: 1.1rem;
}
.who {
  display: flex;
  flex-direction: column;
}
.who strong {
  font-size: 0.98rem;
}
.lv {
  font-size: 0.76rem;
  color: var(--teal);
  font-weight: 600;
}
.prof-menu {
  grid-column: 1 / -1;
  display: flex;
  justify-content: space-between;
  border-top: 1px solid var(--line);
  padding-top: 12px;
  margin-top: 4px;
}
.prof-menu a {
  font-size: 0.78rem;
  color: var(--text-sub);
}
.prof-menu a:hover {
  color: var(--navy);
}
.logout {
  grid-column: 1 / -1;
  width: 100%;
  margin-top: 12px;
  padding: 10px;
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  background: var(--bg);
  font-size: 0.84rem;
  font-weight: 600;
  color: var(--text-sub);
  transition: background 0.12s, color 0.12s;
}
.logout:hover {
  background: #fee2e2;
  border-color: #fca5a5;
  color: #dc2626;
}
</style>
