<script setup>
import { RouterLink } from 'vue-router'

const columns = [
  {
    title: '서비스',
    items: [
      { label: '이용약관', to: '#' },
      { label: '개인정보처리방침', to: '#' },
      { label: '고객센터', to: '#' },
    ]
  },
  {
    title: '금융 교육 & 진단',
    items: [
      { label: '경제 EBTI 진단', to: '/ebti' },
      { label: 'AI 맞춤 콘텐츠 추천', to: '/ai-recommend' },
      { label: '금융 교육 콘텐츠', to: '/contents' },
    ]
  },
  {
    title: '경제 정보',
    items: [
      { label: '경제 용어 사전', to: '/glossary' },
      { label: '교육 및 행사 안내', to: '/events' },
    ]
  },
  {
    title: '커뮤니티',
    items: [
      { label: '금융 정보 공유', to: '/community' },
      { label: '공부 스터디 모집', to: '/community' },
    ]
  }
]
</script>

<template>
  <footer class="footer">
    <div class="container foot-inner">
      <div class="brand">
        <RouterLink to="/" class="logo">im fine <span>edu</span></RouterLink>
        <p>
          im fine edu는 누구나 쉽게 경제·금융을 배우는<br />
          금융 교육 플랫폼입니다. 똑똑한 경제 습관을 함께 만들어요.
        </p>
        <div class="social">
          <a href="#" aria-label="Facebook"><svg xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24" class="social-icon"><path d="M22 12c0-5.52-4.48-10-10-10S2 6.48 2 12c0 4.84 3.44 8.87 8 9.8V15H8v-3h2V9.5C10 7.57 11.57 6 13.5 6H16v3h-2c-.55 0-1 .45-1 1V12h3v3h-3v6.8c4.56-.93 8-4.96 8-9.8z"/></svg></a>
          <a href="#" aria-label="LinkedIn"><svg xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24" class="social-icon"><path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/></svg></a>
          <a href="#" aria-label="YouTube"><svg xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24" class="social-icon"><path d="M23.498 6.163a3.003 3.003 0 0 0-2.11-2.11C19.518 3.545 12 3.545 12 3.545s-7.519 0-9.388.508a3.003 3.003 0 0 0-2.11 2.11C0 8.033 0 12 0 12s0 3.967.502 5.837a3.003 3.003 0 0 0 2.11 2.11c1.87.508 9.388.508 9.388.508s7.519 0 9.388-.508a3.003 3.003 0 0 0 2.11-2.11C24 15.967 24 12 24 12s0-3.967-.502-5.837zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg></a>
        </div>
      </div>

      <div class="cols">
        <div v-for="c in columns" :key="c.title" class="col">
          <h4>{{ c.title }}</h4>
          <template v-for="i in c.items" :key="i.label">
            <RouterLink v-if="i.to !== '#'" :to="i.to">{{ i.label }}</RouterLink>
            <a v-else href="#">{{ i.label }}</a>
          </template>
        </div>
      </div>
    </div>
    <div class="container copy">
      © 2025 im fine edu. All rights reserved.
    </div>
  </footer>
</template>

<style scoped>
.footer {
  margin-top: 60px;
  background: #dfe4f3;
  padding: 44px 0 28px;
  color: var(--text-sub);
}
.foot-inner {
  display: flex;
  justify-content: space-between;
  gap: 40px;
  flex-wrap: wrap;
}
.logo {
  display: inline-block;
  font-size: 1.4rem;
  font-weight: 800;
  color: var(--navy);
  margin-bottom: 12px;
  letter-spacing: -1px;
}
.logo span {
  color: var(--teal);
}
.brand p {
  font-size: 0.82rem;
  line-height: 1.6;
}
.social {
  display: flex;
  gap: 10px;
  margin-top: 16px;
}
.social a {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--navy);
  color: #fff;
  display: grid;
  place-items: center;
  transition: background 0.12s ease, transform 0.12s ease;
}
.social a:hover {
  background: var(--teal);
  transform: translateY(-2px);
}
.social-icon {
  width: 16px;
  height: 16px;
}
.cols {
  display: flex;
  gap: 56px;
}
.col {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.col h4 {
  font-size: 0.9rem;
  color: var(--text);
  margin-bottom: 6px;
  white-space: nowrap;
}
.col a {
  font-size: 0.82rem;
  color: var(--text-sub);
  white-space: nowrap;
}
.col a:hover {
  color: var(--navy);
}
.copy {
  margin-top: 30px;
  padding-top: 18px;
  border-top: 1px solid #cfd6ea;
  font-size: 0.78rem;
  color: var(--text-mute);
}
@media (max-width: 720px) {
  .cols {
    gap: 28px;
  }
}
</style>
