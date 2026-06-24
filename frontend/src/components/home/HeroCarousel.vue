<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

// 배너 슬라이드 정의 (각자 그라데이션 · 카피 · CTA · 장식 이모지)
const slides = computed(() => [
  {
    kicker: '금융 교육 플랫폼',
    title: ['똑똑한 경제 습관,', 'finedu와 함께'],
    desc: '경제 용어부터 금융 상품까지, 누구나 쉽게 배우는 금융 교육',
    cta: '지금 시작하기 →',
    to: auth.isLoggedIn ? '/ebti' : '/login',
    gradient: 'linear-gradient(120deg, #0b4f49 0%, #0f766e 55%, #15803d 120%)',
    art: ['💰', '📈', '🪙'],
  },
  {
    kicker: 'AI 맞춤 추천',
    title: ['AI가 골라주는', '나만의 금융 콘텐츠'],
    desc: '관심사와 학습 이력을 분석해 딱 맞는 콘텐츠를 추천해드려요.',
    cta: 'AI 추천 콘텐츠 보러가기 →',
    to: auth.isLoggedIn ? '/ai-recommend' : '/login',
    gradient: 'linear-gradient(120deg, #1b2a59 0%, #2b3f7a 55%, #4f46e5 120%)',
    art: ['🤖', '✨', '🎯'],
  },
  {
    kicker: '금융 성향 테스트',
    title: ['나의 금융 성향은?', 'EBTI로 알아보기'],
    desc: '5분 테스트로 나의 소비·투자 유형을 진단하고 맞춤 가이드를 받아보세요.',
    cta: '테스트 시작하기 →',
    to: auth.isLoggedIn ? '/ebti' : '/login',
    gradient: 'linear-gradient(120deg, #7c2d12 0%, #c2410c 55%, #f59e0b 120%)',
    art: ['🧭', '🧠', '📊'],
  },
  {
    kicker: '경제 용어 사전',
    title: ['매일 하나씩,', '경제 용어 마스터'],
    desc: '어려운 시사·경제 용어를 쉬운 설명과 함께 차곡차곡 쌓아가세요.',
    cta: '용어 사전 둘러보기 →',
    to: '/glossary',
    gradient: 'linear-gradient(120deg, #581c87 0%, #7e22ce 55%, #db2777 120%)',
    art: ['📚', '🔖', '💡'],
  },
])

const current = ref(0)
const INTERVAL = 5000
let timer = null

function go(i) {
  current.value = (i + slides.value.length) % slides.value.length
}
function next() {
  go(current.value + 1)
}

function start() {
  stop()
  timer = setInterval(next, INTERVAL)
}
function stop() {
  if (timer) clearInterval(timer)
  timer = null
}

onMounted(start)
onBeforeUnmount(stop)
</script>

<template>
  <div class="hero-carousel" @mouseenter="stop" @mouseleave="start">
    <transition-group name="fade" tag="div" class="track">
      <section
        v-for="(s, i) in slides"
        v-show="i === current"
        :key="i"
        class="hero"
        :style="{ background: s.gradient }"
      >
        <div class="hero-text">
          <span class="kicker">{{ s.kicker }}</span>
          <h1>
            <template v-for="(line, li) in s.title" :key="li">
              {{ line }}<br v-if="li < s.title.length - 1" />
            </template>
          </h1>
          <p>{{ s.desc }}</p>
          <RouterLink :to="s.to" class="btn btn-green">{{ s.cta }}</RouterLink>
        </div>
        <div class="hero-art">
          <span class="coin c1">{{ s.art[0] }}</span>
          <span class="coin c2">{{ s.art[1] }}</span>
          <span class="coin c3">{{ s.art[2] }}</span>
        </div>
      </section>
    </transition-group>

    <!-- 우측 하단 점 네비게이션 -->
    <div class="dots">
      <button
        v-for="(s, i) in slides"
        :key="i"
        class="dot"
        :class="{ on: i === current }"
        :aria-label="`${i + 1}번 배너로 이동`"
        @click="go(i)"
      ></button>
    </div>
  </div>
</template>

<style scoped>
.hero-carousel {
  position: relative;
  border-radius: 18px;
  overflow: hidden;
  min-height: 230px;
}
.track {
  display: grid;
}
/* 모든 슬라이드를 같은 칸에 겹쳐 쌓아 전환 */
.track > .hero {
  grid-area: 1 / 1;
}
.hero {
  position: relative;
  overflow: hidden;
  border-radius: 18px;
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
.hero-text {
  position: relative;
  z-index: 2;
  max-width: 70%;
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

/* 점 네비게이션 */
.dots {
  position: absolute;
  right: 22px;
  bottom: 18px;
  z-index: 5;
  display: flex;
  gap: 8px;
}
.dot {
  width: 9px;
  height: 9px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.45);
  transition: width 0.2s, background 0.2s;
  padding: 0;
}
.dot:hover {
  background: rgba(255, 255, 255, 0.75);
}
.dot.on {
  width: 24px;
  background: #fff;
}

/* 페이드 전환 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.6s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 560px) {
  .hero {
    padding: 34px 26px;
  }
  .hero-text {
    max-width: 100%;
  }
  .hero-text h1 {
    font-size: 1.6rem;
  }
  .hero-art {
    opacity: 0.35;
  }
}
</style>
