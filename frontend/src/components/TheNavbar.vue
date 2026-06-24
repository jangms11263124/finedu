<script setup>
import { RouterLink, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

const menus = [
  { label: '콘텐츠 보기', to: '/contents' },
  { label: '교육 행사 프로그램', to: '/events' },
  { label: '경제 용어 사전', to: '/glossary' },
  { label: '커뮤니티', to: '/community' },
]

function logout() {
  auth.logout()
  router.push('/')
}
</script>

<template>
  <header class="nav">
    <div class="container nav-inner">
      <RouterLink to="/" class="logo">fin<span>edu</span></RouterLink>

      <nav class="menu">
        <template v-for="m in menus" :key="m.label">
          <RouterLink
            v-if="m.to !== '#'"
            :to="m.to"
            :class="{ active: $route.path === m.to }"
          >{{ m.label }}</RouterLink>
          <a v-else href="#">{{ m.label }}</a>
        </template>
      </nav>

      <div class="nav-right">
        <!-- 로그인 상태: 프로필 칩 → 마이페이지 -->
        <template v-if="auth.isLoggedIn">
          <RouterLink to="/mypage" class="profile-chip" title="마이페이지">
            <img
              v-if="auth.user?.profile_image"
              :src="auth.user.profile_image"
              class="chip-img"
              alt=""
            />
            <span v-else class="chip-avatar">
              {{ (auth.user?.nickname || 'U').charAt(0) }}
            </span>
            <span class="chip-name">{{ auth.user?.nickname }}</span>
          </RouterLink>
          <button class="btn-logout" @click="logout">로그아웃</button>
        </template>

        <!-- 비로그인: 로그인 버튼 -->
        <RouterLink v-else to="/login" class="btn btn-navy sm">로그인</RouterLink>
      </div>
    </div>
  </header>
</template>

<style scoped>
.nav {
  background: #fff;
  border-bottom: 1px solid var(--line);
  position: sticky;
  top: 0;
  z-index: 50;
}
.nav-inner {
  display: flex;
  align-items: center;
  height: 64px;
  gap: 28px;
}
.logo {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--navy);
  letter-spacing: -1px;
}
.logo span {
  color: var(--teal);
}
.menu {
  display: flex;
  gap: 24px;
}
.menu a {
  font-size: 0.92rem;
  font-weight: 500;
  color: var(--text-sub);
  white-space: nowrap;
}
.menu a:hover {
  color: var(--navy);
}
.menu a.active {
  color: var(--navy);
  font-weight: 700;
}
.nav-right {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 10px;
}
.btn.sm {
  padding: 8px 14px;
  font-size: 0.85rem;
}
.profile-chip {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 5px 12px 5px 6px;
  border: 1px solid var(--line);
  border-radius: 999px;
  background: #fff;
  transition: border-color 0.12s, box-shadow 0.12s;
}
.profile-chip:hover {
  border-color: var(--navy);
  box-shadow: var(--shadow);
}
.chip-avatar,
.chip-img {
  width: 30px;
  height: 30px;
  border-radius: 999px;
  flex-shrink: 0;
}
.chip-avatar {
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, var(--teal), var(--navy));
  color: #fff;
  font-weight: 800;
  font-size: 0.85rem;
}
.chip-img {
  object-fit: cover;
}
.chip-name {
  font-size: 0.86rem;
  font-weight: 600;
  color: var(--navy);
  white-space: nowrap;
}
.btn-logout {
  background: transparent;
  border: 1px solid var(--line);
  border-radius: 999px;
  padding: 8px 14px;
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--text-sub);
  white-space: nowrap;
  transition: background 0.12s, color 0.12s, border-color 0.12s;
}
.btn-logout:hover {
  background: #fee2e2;
  border-color: #fca5a5;
  color: #dc2626;
}
@media (max-width: 980px) {
  .menu {
    display: none;
  }
}
</style>
