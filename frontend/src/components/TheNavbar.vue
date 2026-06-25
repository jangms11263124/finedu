<script setup>
import { RouterLink, useRouter, useRoute } from 'vue-router'
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const isHome = computed(() => route.path === '/')

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

      <div class="nav-right" :class="{ 'hide-on-desktop-home': isHome }">
        <!-- 로그인 상태: 프로필 칩 → 마이페이지 -->
        <template v-if="auth.isLoggedIn">
          <RouterLink to="/mypage" class="profile-chip" title="마이페이지">
            {{ auth.user?.nickname }}
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
  padding-right: 0;
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
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 8px 14px;
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  background: #fff;
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--navy);
  white-space: nowrap;
  transition: border-color 0.12s, box-shadow 0.12s;
}
.profile-chip:hover {
  border-color: var(--navy);
  box-shadow: var(--shadow);
}
.btn-logout {
  background: transparent;
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  padding: 8px 14px;
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--text-sub);
  white-space: nowrap;
  transition: background 0.12s, color 0.12s, border-color 0.12s;
}
.btn-logout:hover {
  background: rgba(220, 38, 38, 0.05);
  border-color: #ef4444;
  color: #ef4444;
}
@media (min-width: 1300px) {
  .hide-on-desktop-home {
    display: none !important;
  }
}
@media (max-width: 980px) {
  .menu {
    display: none;
  }
  .nav-right {
    gap: 8px;
  }
}
@media (max-width: 480px) {
  .nav-inner {
    gap: 10px;
  }
  .logo {
    font-size: 1.2rem;
    letter-spacing: -0.5px;
  }
  .profile-chip {
    padding: 6px 10px;
  }
  .btn-logout {
    padding: 6px 10px;
    font-size: 0.75rem;
  }
}
</style>
