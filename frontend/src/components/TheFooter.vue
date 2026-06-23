<script setup>
const columns = [
  { title: '서비스', items: ['이용약관', '개인정보처리방침', '고객센터'] },
  { title: '콘텐츠', items: ['경제 용어', '금융 콘텐츠', '금융 상품'] },
  { title: '커뮤니티', items: ['정보 게시판', '이벤트', '공지사항'] },
]
</script>

<template>
  <footer class="footer">
    <div class="container foot-inner">
      <div class="brand">
        <div class="logo">fin<span>edu</span></div>
        <p>
          finedu는 누구나 쉽게 경제·금융을 배우는<br />
          금융 교육 플랫폼입니다. 똑똑한 경제 습관을 함께 만들어요.
        </p>
        <div class="social">
          <span>f</span><span>in</span><span>▶</span>
        </div>
      </div>

      <div class="cols">
        <div v-for="c in columns" :key="c.title" class="col">
          <h4>{{ c.title }}</h4>
          <a v-for="i in c.items" :key="i" href="#">{{ i }}</a>
        </div>
      </div>
    </div>
    <div class="container copy">
      © 2025 finedu. All rights reserved.
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
  font-size: 1.4rem;
  font-weight: 800;
  color: var(--navy);
  margin-bottom: 12px;
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
  gap: 8px;
  margin-top: 16px;
}
.social span {
  width: 30px;
  height: 30px;
  border-radius: 999px;
  background: var(--navy);
  color: #fff;
  display: grid;
  place-items: center;
  font-size: 0.75rem;
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
}
.col a {
  font-size: 0.82rem;
  color: var(--text-sub);
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
