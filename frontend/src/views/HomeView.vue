<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import api from '@/api'
import ContentCard from '@/components/home/ContentCard.vue'
import EventCard from '@/components/home/EventCard.vue'
import CardCarousel from '@/components/common/CardCarousel.vue'
import SideAuth from '@/components/home/SideAuth.vue'
import SideQuiz from '@/components/home/SideQuiz.vue'
import SideCalendar from '@/components/home/SideCalendar.vue'
import SideTerms from '@/components/home/SideTerms.vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

const recommended = ref([])
const popular = ref([])
const events = ref([])
const posts = ref([])

onMounted(async () => {
  try {
    const [rec, pop, ev, ps] = await Promise.all([
      api.get('/contents/', { params: { recommended: 1 } }),
      api.get('/contents/', { params: { popular: 1 } }),
      api.get('/events/'),
      api.get('/posts/', { params: { popular: 1 } }),
    ])
    recommended.value = rec.data
    popular.value = pop.data
    events.value = ev.data
    posts.value = ps.data.slice(0, 5)
  } catch (e) {
    console.error('홈 데이터 로딩 실패', e)
  }
})
</script>

<template>
  <main class="home">
    <div class="container layout">
      <!-- ===== 본문 ===== -->
      <div class="main-col">
        <!-- 히어로 배너 -->
        <section class="hero">
          <div class="hero-text">
            <span class="kicker">금융 교육 플랫폼</span>
            <h1>똑똑한 경제 습관,<br />finedu와 함께</h1>
            <p>경제 용어부터 금융 상품까지, 누구나 쉽게 배우는 금융 교육</p>
            <RouterLink
              :to="auth.isLoggedIn ? '/ebti' : '/login'"
              class="btn btn-green"
            >지금 시작하기 →</RouterLink>
          </div>
          <div class="hero-art">
            <span class="coin c1">💰</span>
            <span class="coin c2">📈</span>
            <span class="coin c3">🪙</span>
          </div>
        </section>

        <!-- 추천 콘텐츠 -->
        <section class="block">
          <div class="section-head">
            <h2>추천 콘텐츠<span class="sub">나에게 딱 맞는 콘텐츠를 추천해드려요</span></h2>
            <RouterLink to="/contents" class="more">더보기 ›</RouterLink>
          </div>
          <div class="rec-wrap">
            <div :class="{ blurred: !auth.isLoggedIn }">
              <CardCarousel :items="recommended" v-slot="{ item }">
                <ContentCard :content="item" />
              </CardCarousel>
            </div>
            <div v-if="!auth.isLoggedIn" class="rec-lock">
              <span class="lock-ico">🔒</span>
              <p class="lock-title">나만을 위한 맞춤 콘텐츠가 기다리고 있어요</p>
              <p class="lock-desc">로그인하면 관심사에 딱 맞는 콘텐츠를 추천해드려요.</p>
              <RouterLink to="/login" class="btn btn-navy">로그인하고 추천받기 →</RouterLink>
              <p class="lock-sub">
                아직 회원이 아니신가요?
                <RouterLink to="/signup">회원가입</RouterLink>
              </p>
            </div>
          </div>
        </section>

        <!-- 인기 콘텐츠 -->
        <section class="block">
          <div class="section-head">
            <h2>인기 콘텐츠<span class="sub">지금 가장 많이 본 콘텐츠</span></h2>
            <RouterLink to="/contents" class="more">더보기 ›</RouterLink>
          </div>
          <CardCarousel :items="popular" v-slot="{ item }">
            <ContentCard :content="item" />
          </CardCarousel>
        </section>

        <!-- 교육 행사 & 프로그램 -->
        <section class="block">
          <div class="section-head">
            <h2>교육 행사 &amp; 프로그램</h2>
            <RouterLink to="/events" class="more">더보기 ›</RouterLink>
          </div>
          <CardCarousel :items="events" v-slot="{ item }">
            <EventCard :event="item" />
          </CardCarousel>
        </section>

        <!-- 인기 게시글 -->
        <section class="block">
          <div class="section-head">
            <h2>인기 게시글</h2>
            <RouterLink to="/community" class="more">더보기 ›</RouterLink>
          </div>
          <ul class="post-list">
            <RouterLink
              v-for="(p, i) in posts"
              :key="p.id"
              :to="`/community/${p.id}`"
              custom
              v-slot="{ navigate }"
            >
              <li @click="navigate">
                <span class="rank">{{ i + 1 }}</span>
                <span class="board">{{ p.board_display }}</span>
                <span class="title">{{ p.title }}</span>
                <span class="info">
                  💬 {{ p.comment_count }} · 👁 {{ p.views.toLocaleString() }}
                </span>
              </li>
            </RouterLink>
          </ul>
        </section>
      </div>

      <!-- ===== 사이드바 ===== -->
      <aside class="side-col">
        <SideAuth />
        <SideQuiz />
        <SideCalendar />
        <SideTerms />
      </aside>
    </div>
  </main>
</template>

<style scoped>
.home {
  padding: 26px 0 10px;
}
.layout {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 28px;
  align-items: start;
}
.main-col {
  display: flex;
  flex-direction: column;
  gap: 38px;
}
.side-col {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

/* 히어로 */
.hero {
  position: relative;
  overflow: hidden;
  border-radius: 18px;
  background: linear-gradient(120deg, #0b4f49 0%, #0f766e 55%, #15803d 120%);
  color: #fff;
  padding: 44px 40px;
  min-height: 230px;
  display: flex;
  align-items: center;
}
.kicker {
  display: inline-block;
  font-size: 0.78rem;
  font-weight: 600;
  background: rgba(255, 255, 255, 0.18);
  padding: 5px 12px;
  border-radius: 999px;
  margin-bottom: 16px;
}
.hero-text h1 {
  font-size: 2rem;
  font-weight: 800;
  line-height: 1.25;
  letter-spacing: -0.5px;
}
.hero-text p {
  margin: 14px 0 22px;
  font-size: 0.95rem;
  opacity: 0.9;
}
.hero-art {
  position: absolute;
  right: 30px;
  top: 0;
  bottom: 0;
  width: 240px;
  pointer-events: none;
}
.coin {
  position: absolute;
  font-size: 3rem;
  filter: drop-shadow(0 6px 14px rgba(0, 0, 0, 0.3));
}
.c1 { right: 30px; top: 40px; font-size: 4rem; }
.c2 { right: 120px; top: 110px; }
.c3 { right: 20px; bottom: 36px; }

/* 추천 콘텐츠 잠금 (비로그인) */
.rec-wrap {
  position: relative;
}
.grid-4.blurred {
  filter: blur(6px);
  pointer-events: none;
  user-select: none;
}
.rec-lock {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  gap: 6px;
  padding: 20px;
  background: rgba(238, 240, 248, 0.55);
  border-radius: var(--radius);
}
.lock-ico {
  font-size: 2rem;
}
.lock-title {
  font-size: 1.05rem;
  font-weight: 800;
  color: var(--navy);
}
.lock-desc {
  font-size: 0.86rem;
  color: var(--text-sub);
  margin-bottom: 8px;
}
.rec-lock .btn {
  padding: 12px 24px;
}
.lock-sub {
  margin-top: 10px;
  font-size: 0.8rem;
  color: var(--text-sub);
}
.lock-sub a {
  color: var(--navy);
  font-weight: 700;
}

/* 그리드 */
.grid-4 {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}
.grid-3 {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

/* 게시글 목록 */
.post-list {
  list-style: none;
  margin: 0;
  padding: 0;
  background: #fff;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  overflow: hidden;
}
.post-list li {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 18px;
  border-bottom: 1px solid var(--line);
  font-size: 0.88rem;
}
.post-list li:last-child {
  border-bottom: none;
}
.post-list li:hover {
  background: var(--bg);
}
.post-list li {
  cursor: pointer;
}
.rank {
  font-weight: 800;
  color: var(--navy);
  width: 18px;
  text-align: center;
}
.board {
  font-size: 0.72rem;
  color: var(--teal);
  font-weight: 700;
  background: #e6f4f1;
  padding: 3px 8px;
  border-radius: 6px;
  white-space: nowrap;
}
.post-list .title {
  flex: 1;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.post-list .info {
  font-size: 0.75rem;
  color: var(--text-mute);
  white-space: nowrap;
}

/* 반응형 */
@media (max-width: 980px) {
  .layout {
    grid-template-columns: 1fr;
  }
  .side-col {
    position: static;
  }
  .grid-4 {
    grid-template-columns: repeat(2, 1fr);
  }
}
@media (max-width: 560px) {
  .grid-4,
  .grid-3 {
    grid-template-columns: 1fr;
  }
  .post-list .info {
    display: none;
  }
}
</style>
