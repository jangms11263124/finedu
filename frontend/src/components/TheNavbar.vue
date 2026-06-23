<script setup>
import { RouterLink } from 'vue-router'

const menus = [
  { label: '콘텐츠 보기', to: '/contents' },
  { label: '교육 행사 프로그램', to: '/events' },
  { label: '경제 용어 사전', to: '/glossary' },
  { label: '커뮤니티', to: '/community' },
]
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
        <div class="search">
          <span class="ico">🔍</span>
          <input type="text" placeholder="검색어를 입력하세요" />
        </div>
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
.search {
  width: 280px;
  display: flex;
  align-items: center;
  gap: 6px;
  background: var(--bg);
  border: 1px solid var(--line);
  border-radius: 999px;
  padding: 9px 16px;
}
.search .ico {
  font-size: 0.85rem;
}
.search input {
  flex: 1;
  border: none;
  background: transparent;
  outline: none;
  font-size: 0.85rem;
  width: 100%;
}
.btn.sm {
  padding: 8px 14px;
  font-size: 0.85rem;
}
@media (max-width: 980px) {
  .menu,
  .search {
    display: none;
  }
}
</style>
