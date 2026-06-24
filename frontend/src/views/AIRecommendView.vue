<script setup>
import { RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useRecommendStore } from '@/stores/recommend'

const auth = useAuthStore()
// 추천 결과는 스토어에 보관 → 페이지 재진입 시 캐시를 그대로 보여주고,
// '추천 받기 / 다시 추천받기'를 눌렀을 때만 rec.fetch()로 새로 호출한다.
const rec = useRecommendStore()

const gradients = {
  economy: 'linear-gradient(135deg,#0f766e,#0891b2)',
  invest: 'linear-gradient(135deg,#1b2a59,#3b82f6)',
  saving: 'linear-gradient(135deg,#15803d,#65a30d)',
  finance: 'linear-gradient(135deg,#7c3aed,#2563eb)',
  society: 'linear-gradient(135deg,#b45309,#f59e0b)',
  etc: 'linear-gradient(135deg,#475569,#94a3b8)',
}
const icons = {
  economy: '📈', invest: '💹', saving: '🏦',
  finance: '💳', society: '🏙️', etc: '📰',
}
</script>

<template>
  <main class="ai">
    <div class="container">
      <!-- 헤더 -->
      <header class="hero">
        <span class="badge">🤖 AI 맞춤 추천</span>
        <h1>{{ auth.user?.nickname }}님을 위한 콘텐츠</h1>
        <p class="lead">
          EBTI 결과 · 관심사 · 커뮤니티 활동 · 퀴즈 학습 이력을 종합해
          AI가 맞춤 콘텐츠를 골랐어요.
        </p>
      </header>

      <!-- 분석에 사용된 신호 칩 (추천을 한 번 받은 뒤에만 표시) -->
      <template v-if="rec.signalsMeta">
        <div class="signals">
          <span class="chip" :class="{ off: !rec.signalsMeta.has_ebti }">
            {{ rec.signalsMeta.has_ebti ? '✅' : '⬜' }} EBTI 결과
          </span>
          <span class="chip" :class="{ off: !rec.signalsMeta.has_liked_contents }">
            {{ rec.signalsMeta.has_liked_contents ? '✅' : '⬜' }} 관심 콘텐츠
          </span>
          <span class="chip" :class="{ off: !rec.signalsMeta.has_community }">
            {{ rec.signalsMeta.has_community ? '✅' : '⬜' }} 커뮤니티 활동
          </span>
          <span class="chip" :class="{ off: !rec.signalsMeta.has_trending }">
            {{ rec.signalsMeta.has_trending ? '✅' : '⬜' }} 최근 인기 주제
          </span>
          <span class="chip" :class="{ off: !rec.signalsMeta.has_quiz_weak }">
            {{ rec.signalsMeta.has_quiz_weak ? '✅' : '⬜' }} 퀴즈 약점
          </span>
          <span class="chip" :class="{ off: !rec.signalsMeta.has_streak }">
            {{ rec.signalsMeta.has_streak ? '✅' : '⬜' }} 학습 스트릭
          </span>
        </div>

        <p v-if="!rec.signalsMeta.has_ebti" class="ebti-hint">
          💡 <RouterLink to="/ebti">EBTI 테스트</RouterLink>를 먼저 하면 더 정확한 추천을 받을 수 있어요.
        </p>
      </template>

      <!-- 1) 최초 진입: 아직 추천을 받지 않은 상태 -->
      <div v-if="!rec.loaded && !rec.loading && !rec.error" class="intro">
        <span class="intro-ico">🤖</span>
        <h2>AI 맞춤 추천을 받아보세요</h2>
        <p>버튼을 누르면 관심사 · 학습 이력 · EBTI 결과를 분석해 콘텐츠를 골라드려요.</p>
        <button class="btn btn-navy" @click="rec.fetch()">✨ 추천 받기</button>
      </div>

      <!-- 2) 로딩: 스켈레톤 UI -->
      <div
        v-else-if="rec.loading"
        class="skeleton"
        aria-busy="true"
        aria-label="AI가 맞춤 콘텐츠를 고르는 중입니다"
      >
        <p class="sk-note">✨ AI가 회원님께 맞는 콘텐츠를 고르고 있어요...</p>
        <div class="sk sk-summary"></div>
        <section v-for="n in 2" :key="n" class="sk-bundle">
          <div class="sk-bundle-head">
            <span class="sk sk-no"></span>
            <span class="sk sk-title"></span>
          </div>
          <span class="sk sk-story"></span>
          <div class="sk-list">
            <div v-for="m in 3" :key="m" class="sk-card">
              <span class="sk sk-thumb"></span>
              <div class="sk-card-body">
                <span class="sk sk-cat"></span>
                <span class="sk sk-line"></span>
                <span class="sk sk-line short"></span>
              </div>
            </div>
          </div>
        </section>
      </div>

      <!-- 3) 에러 -->
      <div v-else-if="rec.error" class="intro">
        <span class="intro-ico">😢</span>
        <p class="error">{{ rec.error }}</p>
        <button class="btn btn-navy" @click="rec.fetch()">다시 시도</button>
      </div>

      <!-- 4) 추천 결과 -->
      <template v-else>
        <!-- AI 요약 -->
        <div class="summary">
          <span class="ico">✨</span>
          <p>{{ rec.summary }}</p>
          <span class="src">{{ rec.source === 'ai' ? 'AI 분석' : '추천 엔진' }}</span>
        </div>

        <!-- 번들(묶음) 추천 -->
        <section
          v-for="(bundle, bi) in rec.bundles"
          :key="bi"
          class="bundle"
        >
          <header class="bundle-head">
            <div class="bundle-title">
              <span class="bundle-no">묶음 {{ bi + 1 }}</span>
              <h2>{{ bundle.title }}</h2>
            </div>
            <p class="storyline">
              <span class="ai-tag">AI</span> {{ bundle.storyline }}
            </p>
          </header>

          <div class="rec-list">
            <RouterLink
              v-for="it in bundle.items"
              :key="it.content.id"
              :to="`/contents/${it.content.id}`"
              class="rec-card"
            >
              <span
                class="thumb"
                :style="{ background: gradients[it.content.category] || gradients.etc }"
              >{{ icons[it.content.category] || '📰' }}</span>
              <div class="body">
                <span class="cat">{{ it.content.category_display }}</span>
                <h3>{{ it.content.title }}</h3>
                <p class="reason">{{ it.content.summary }}</p>
              </div>
              <span class="go">›</span>
            </RouterLink>
          </div>
        </section>

        <div class="actions">
          <button class="btn btn-outline" @click="rec.fetch()">🔄 다시 추천받기</button>
          <RouterLink to="/contents" class="btn btn-navy">전체 콘텐츠 보기 →</RouterLink>
        </div>
      </template>
    </div>
  </main>
</template>

<style scoped>
.ai {
  padding: 32px 0 30px;
  min-height: 74vh;
}
.hero {
  text-align: center;
  margin-bottom: 20px;
}
.badge {
  display: inline-block;
  font-size: 0.82rem;
  font-weight: 700;
  color: #fff;
  background: linear-gradient(120deg, #1b2a59, #4f46e5);
  padding: 6px 14px;
  border-radius: 999px;
}
.hero h1 {
  font-size: 1.8rem;
  font-weight: 800;
  letter-spacing: -0.6px;
  margin: 16px 0 10px;
}
.lead {
  color: var(--text-sub);
  font-size: 0.94rem;
  line-height: 1.6;
  max-width: 560px;
  margin: 0 auto;
}
.signals {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 8px;
  margin: 22px 0 6px;
}
.chip {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--teal);
  background: #e6f4f1;
  border: 1px solid #cfe9e3;
  border-radius: 999px;
  padding: 6px 12px;
}
.chip.off {
  color: var(--text-mute);
  background: var(--bg);
  border-color: var(--line);
}
.ebti-hint {
  text-align: center;
  font-size: 0.85rem;
  color: var(--text-sub);
  margin: 10px 0;
}
.ebti-hint a {
  color: var(--navy);
  font-weight: 700;
}
/* 최초 진입 / 에러 안내 */
.intro {
  text-align: center;
  background: #fff;
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 48px 24px;
  margin-top: 22px;
  box-shadow: var(--shadow);
}
.intro-ico {
  font-size: 2.6rem;
}
.intro h2 {
  font-size: 1.25rem;
  font-weight: 800;
  letter-spacing: -0.4px;
  margin: 14px 0 8px;
}
.intro p {
  color: var(--text-sub);
  font-size: 0.92rem;
  line-height: 1.6;
  max-width: 440px;
  margin: 0 auto 20px;
}
.intro .error {
  color: #dc2626;
  font-weight: 600;
  padding: 0;
}

/* 스켈레톤 UI */
.skeleton {
  margin-top: 22px;
}
.sk-note {
  text-align: center;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-sub);
  margin-bottom: 18px;
}
.sk {
  position: relative;
  overflow: hidden;
  background: #e9ebf3;
  border-radius: 8px;
}
.sk::after {
  content: '';
  position: absolute;
  inset: 0;
  transform: translateX(-100%);
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.65),
    transparent
  );
  animation: shimmer 1.3s infinite;
}
@keyframes shimmer {
  100% { transform: translateX(100%); }
}
.sk-summary {
  height: 60px;
  border-radius: 14px;
  margin: 0 0 24px;
}
.sk-bundle {
  margin: 0 0 26px;
}
.sk-bundle-head {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}
.sk-no {
  width: 54px;
  height: 20px;
  border-radius: 999px;
}
.sk-title {
  width: 180px;
  height: 20px;
}
.sk-story {
  display: block;
  width: 70%;
  height: 14px;
  margin-bottom: 14px;
}
.sk-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.sk-card {
  display: flex;
  align-items: center;
  gap: 14px;
  background: #fff;
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 16px;
}
.sk-thumb {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  flex-shrink: 0;
}
.sk-card-body {
  flex: 1;
  min-width: 0;
}
.sk-cat {
  display: block;
  width: 48px;
  height: 14px;
  border-radius: 6px;
  margin-bottom: 9px;
}
.sk-line {
  display: block;
  width: 80%;
  height: 13px;
  margin-bottom: 7px;
}
.sk-line.short {
  width: 55%;
  margin-bottom: 0;
}
.error {
  text-align: center;
  color: #dc2626;
  padding: 50px 0;
}
.summary {
  display: flex;
  align-items: center;
  gap: 12px;
  background: linear-gradient(120deg, #eef2ff, #f5f3ff);
  border: 1px solid #ddd6fe;
  border-radius: 14px;
  padding: 18px 20px;
  margin: 22px 0 20px;
}
.summary .ico {
  font-size: 1.4rem;
}
.summary p {
  flex: 1;
  font-size: 0.95rem;
  font-weight: 600;
  color: #3730a3;
}
.summary .src {
  font-size: 0.72rem;
  font-weight: 700;
  color: #6d28d9;
  background: #ede9fe;
  padding: 4px 10px;
  border-radius: 999px;
  white-space: nowrap;
}
.bundle {
  margin: 0 0 26px;
}
.bundle-head {
  margin: 0 0 12px;
}
.bundle-title {
  display: flex;
  align-items: center;
  gap: 10px;
}
.bundle-no {
  font-size: 0.72rem;
  font-weight: 800;
  color: #fff;
  background: linear-gradient(120deg, #1b2a59, #4f46e5);
  padding: 3px 10px;
  border-radius: 999px;
  flex-shrink: 0;
}
.bundle-title h2 {
  font-size: 1.15rem;
  font-weight: 800;
  letter-spacing: -0.4px;
}
.storyline {
  margin: 8px 0 0;
  font-size: 0.88rem;
  line-height: 1.55;
  color: var(--text-sub);
}
.rec-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.rec-card {
  display: flex;
  align-items: center;
  gap: 14px;
  background: #fff;
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 16px;
  transition: transform 0.14s, box-shadow 0.14s;
}
.rec-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-hover);
}
.thumb {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  font-size: 1.5rem;
  flex-shrink: 0;
}
.body {
  flex: 1;
  min-width: 0;
}
.cat {
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--teal);
  background: #e6f4f1;
  padding: 2px 8px;
  border-radius: 6px;
}
.body h3 {
  font-size: 1rem;
  font-weight: 700;
  margin: 7px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.reason {
  font-size: 0.84rem;
  color: var(--text-sub);
  line-height: 1.45;
}
.ai-tag {
  font-size: 0.66rem;
  font-weight: 800;
  color: #fff;
  background: linear-gradient(120deg, #4f46e5, #7c3aed);
  padding: 2px 6px;
  border-radius: 5px;
  margin-right: 4px;
  vertical-align: middle;
}
.go {
  font-size: 1.5rem;
  color: var(--text-mute);
  flex-shrink: 0;
}
.actions {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 28px;
}
@media (max-width: 560px) {
  .reason {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
}
</style>
