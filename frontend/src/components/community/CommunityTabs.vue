<script setup>
import { RouterLink } from 'vue-router'
</script>

<template>
  <header class="c-head">
    <div>
      <h1>커뮤니티</h1>
      <p>finedu 회원들과 금융 이야기를 나누고 인기 랭킹을 확인하세요.</p>
    </div>
    <nav class="c-tabs">
      <RouterLink to="/community" exact-active-class="on">📝 게시판</RouterLink>
      <RouterLink to="/community/ranking" active-class="on">🏆 랭킹</RouterLink>
    </nav>
  </header>
</template>

<style scoped>
.c-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 22px;
  flex-wrap: wrap;
}
.c-head h1 {
  font-size: 1.7rem;
  font-weight: 800;
  letter-spacing: -0.6px;
}
.c-head p {
  margin-top: 8px;
  color: var(--text-sub);
  font-size: 0.92rem;
}
.c-tabs {
  display: flex;
  gap: 8px;
}
.c-tabs a {
  background: #fff;
  border: 1px solid var(--line);
  border-radius: 999px;
  padding: 9px 18px;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-sub);
}
.c-tabs a.on {
  background: var(--navy);
  color: #fff;
  border-color: var(--navy);
}
</style>
