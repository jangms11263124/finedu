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
</script>

<template>
  <main class="ai">
    <div class="container">
      <!-- 헤더 -->
      <header class="hero">
        <span class="badge">AI 맞춤 추천</span>
        <h1>{{ auth.user?.nickname }}님을 위한 콘텐츠</h1>
        <p class="lead">EBTI 결과 · 관심사 · 커뮤니티 활동 · 퀴즈 학습 이력을 종합해 AI가 맞춤 콘텐츠를 골랐어요.</p>
      </header>

      <!-- 분석에 사용된 신호 칩 (추천을 한 번 받은 뒤에만 표시) -->
      <template v-if="rec.signalsMeta">
        <div class="signals">
          <span class="chip" :class="{ off: !rec.signalsMeta.has_ebti }">
            <svg v-if="rec.signalsMeta.has_ebti" class="sig-icon checked" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
            <span v-else class="sig-dot-off"></span>
            EBTI 결과
          </span>
          <span class="chip" :class="{ off: !rec.signalsMeta.has_liked_contents }">
            <svg v-if="rec.signalsMeta.has_liked_contents" class="sig-icon checked" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
            <span v-else class="sig-dot-off"></span>
            관심 콘텐츠
          </span>
          <span class="chip" :class="{ off: !rec.signalsMeta.has_community }">
            <svg v-if="rec.signalsMeta.has_community" class="sig-icon checked" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
            <span v-else class="sig-dot-off"></span>
            커뮤니티 활동
          </span>
          <span class="chip" :class="{ off: !rec.signalsMeta.has_trending }">
            <svg v-if="rec.signalsMeta.has_trending" class="sig-icon checked" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
            <span v-else class="sig-dot-off"></span>
            최근 인기 주제
          </span>
          <span class="chip" :class="{ off: !rec.signalsMeta.has_quiz_weak }">
            <svg v-if="rec.signalsMeta.has_quiz_weak" class="sig-icon checked" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
            <span v-else class="sig-dot-off"></span>
            퀴즈 약점
          </span>
          <span class="chip" :class="{ off: !rec.signalsMeta.has_streak }">
            <svg v-if="rec.signalsMeta.has_streak" class="sig-icon checked" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
            <span v-else class="sig-dot-off"></span>
            학습 스트릭
          </span>
        </div>

        <div v-if="!rec.signalsMeta.has_ebti" class="ebti-hint-box">
          <svg class="hint-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
          <p class="ebti-hint"><RouterLink to="/ebti">EBTI 테스트</RouterLink>를 먼저 진행하시면 한층 더 정밀한 AI 맞춤 추천 서비스를 이용하실 수 있습니다.</p>
        </div>
      </template>

      <!-- 1) 최초 진입: 아직 추천을 받지 않은 상태 -->
      <div v-if="!rec.loaded && !rec.loading && !rec.error" class="intro-card">
        <h2>AI 맞춤 추천을 받아보세요</h2>
        <p>간단한 클릭 한 번으로 내 경제 성향(EBTI), 관심 금융 카테고리, 퀴즈 취약점 정보를 종합적으로 분석해 가장 가치 있는 교육 콘텐츠들을 추천해 드립니다.</p>
        <button class="btn btn-navy btn-premium" @click="rec.fetch()">
          추천 받기
        </button>
      </div>

      <!-- 2) 로딩: 스켈레톤 UI -->
      <div
        v-else-if="rec.loading"
        class="skeleton"
        aria-busy="true"
        aria-label="AI가 맞춤 콘텐츠를 고르는 중입니다"
      >
        <div class="sk-note-wrap">
          <svg class="sk-spark" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275Z"></path></svg>
          <p class="sk-note">AI가 회원님께 꼭 맞는 금융 교육 콘텐츠를 구성하고 있어요...</p>
        </div>
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
      <div v-else-if="rec.error" class="intro-card error-card">
        <div class="intro-visual">
          <svg class="alert-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
        </div>
        <h2>추천 결과를 가져오지 못했습니다</h2>
        <p class="error">{{ rec.error }}</p>
        <button class="btn btn-navy btn-premium" @click="rec.fetch()">다시 시도</button>
      </div>

      <!-- 4) 추천 결과 -->
      <template v-else>
        <!-- AI 요약 리포트 카드 -->
        <div class="summary-card">
          <div class="sum-header">
            <svg class="sum-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
              <path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275Z"></path>
            </svg>
            <h3>AI 종합 분석 코멘트</h3>
            <span class="src">{{ rec.source === 'ai' ? 'AI 분석 리포트' : '기본 분석' }}</span>
          </div>
          <p class="sum-body">{{ rec.summary }}</p>
        </div>

        <!-- 번들(묶음) 추천 -->
        <section
          v-for="(bundle, bi) in rec.bundles"
          :key="bi"
          class="bundle"
        >
          <header class="bundle-head">
            <div class="bundle-title">
              <span class="bundle-no">테마 {{ bi + 1 }}</span>
              <h2>{{ bundle.title }}</h2>
            </div>
            <p class="storyline"><span class="ai-tag">AI 분석</span> {{ bundle.storyline }}</p>
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
              >
                <span class="card-text-badge">{{ it.content.category_display.slice(0, 2) }}</span>
              </span>
              <div class="body">
                <span class="cat">{{ it.content.category_display }}</span>
                <h3>{{ it.content.title }}</h3>
                <p class="reason">{{ it.content.summary }}</p>
              </div>
              <span class="go">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>
              </span>
            </RouterLink>
          </div>
        </section>

        <!-- 하단 버튼 영역 -->
        <div class="actions">
          <button class="btn btn-outline btn-refresh" @click="rec.fetch()">
            <svg class="refresh-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"></path>
            </svg>
            다시 추천받기
          </button>
          <RouterLink to="/contents" class="btn btn-navy">
            전체 콘텐츠 보기
            <svg class="arrow-right-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>
          </RouterLink>
        </div>
      </template>
    </div>
  </main>
</template>

<style scoped>
.ai {
  padding: 34px 0 40px;
  min-height: 74vh;
}
.hero {
  text-align: center;
  margin-bottom: 24px;
}
.badge {
  display: inline-block;
  font-size: 0.8rem;
  font-weight: 800;
  color: var(--navy);
  background: rgba(27, 42, 89, 0.08);
  border: 1px solid rgba(27, 42, 89, 0.12);
  padding: 5px 14px;
  border-radius: 999px;
  letter-spacing: -0.2px;
}
.hero h1 {
  font-size: 1.8rem;
  font-weight: 800;
  letter-spacing: -0.6px;
  margin: 16px 0 10px;
  color: var(--navy);
  word-break: keep-all;
}
.lead {
  color: var(--text-sub);
  font-size: 0.95rem;
  line-height: 1.6;
  max-width: 800px;
  margin: 0 auto;
  word-break: keep-all;
  letter-spacing: -0.3px;
}

/* 신호 칩 목록 */
.signals {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 8px;
  margin: 22px 0 12px;
}
.chip {
  font-size: 0.78rem;
  font-weight: 700;
  color: var(--teal);
  background: #f0fdfa;
  border: 1px solid #b2f5ea;
  border-radius: 999px;
  padding: 6px 14px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: all 0.15s ease;
  white-space: nowrap;
}
.chip.off {
  color: var(--text-mute);
  background: var(--bg);
  border-color: var(--line);
}
.sig-icon {
  width: 10px;
  height: 10px;
  color: var(--teal);
  flex-shrink: 0;
}
.sig-dot-off {
  width: 6px;
  height: 6px;
  background: var(--text-mute);
  border-radius: 50%;
  flex-shrink: 0;
  opacity: 0.5;
}

/* EBTI 조언 힌트 */
.ebti-hint-box {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin: 12px auto;
  max-width: 720px;
  background: #fffbeb;
  border: 1px solid #fef3c7;
  padding: 10px 20px;
  border-radius: 12px;
}
.hint-icon {
  width: 14px;
  height: 14px;
  color: #d97706;
  flex-shrink: 0;
}
.ebti-hint {
  font-size: 0.85rem;
  color: #b45309;
  font-weight: 500;
  margin: 0;
  word-break: keep-all;
  line-height: 1.5;
  letter-spacing: -0.2px;
}
.ebti-hint a {
  color: var(--navy);
  font-weight: 700;
  text-decoration: underline;
}

/* 웰컴 인트로 카드 */
.intro-card {
  text-align: center;
  background: #fff;
  border: 1px solid var(--line);
  border-radius: 20px;
  padding: 56px 32px;
  margin-top: 24px;
  box-shadow: var(--shadow);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.intro-visual {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: rgba(79, 70, 229, 0.08);
  color: #4f46e5;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
}
.sparkle-huge {
  width: 36px;
  height: 36px;
}
.intro-card h2 {
  font-size: 1.35rem;
  font-weight: 800;
  color: var(--navy);
  letter-spacing: -0.4px;
  margin: 0 0 10px;
  word-break: keep-all;
}
.intro-card p {
  color: var(--text-sub);
  font-size: 0.92rem;
  line-height: 1.7;
  max-width: 500px;
  margin: 0 0 28px;
  word-break: keep-all;
  letter-spacing: -0.3px;
}
.btn-premium {
  padding: 13px 26px;
  border-radius: 12px;
  font-size: 0.95rem;
  box-shadow: 0 4px 14px rgba(27, 42, 89, 0.25);
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.btn-premium:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(27, 42, 89, 0.35);
}
.btn-spark-icon {
  width: 16px;
  height: 16px;
  color: #fff;
  flex-shrink: 0;
}

/* 에러 알림 카드 */
.error-card .intro-visual {
  background: rgba(220, 38, 38, 0.08);
  color: #dc2626;
}
.alert-icon {
  width: 32px;
  height: 32px;
}
.error-card .error {
  color: #dc2626;
  font-weight: 600;
  margin-bottom: 24px;
}

/* 스켈레톤 로딩 */
.skeleton {
  margin-top: 24px;
}
.sk-note-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-bottom: 20px;
}
.sk-spark {
  width: 16px;
  height: 16px;
  color: #4f46e5;
  animation: sk-pulse 1.5s infinite;
}
@keyframes sk-pulse {
  50% { transform: scale(1.2); opacity: 0.6; }
}
.sk-note {
  font-size: 0.9rem;
  font-weight: 700;
  color: #4f46e5;
  margin: 0;
  word-break: keep-all;
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
  height: 64px;
  border-radius: 16px;
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

/* AI 요약 리포트 카드 */
.summary-card {
  background: linear-gradient(135deg, rgba(238, 242, 255, 0.6), rgba(245, 243, 255, 0.7));
  backdrop-filter: blur(8px);
  border: 1px solid rgba(196, 181, 253, 0.4);
  box-shadow: 0 8px 30px rgba(79, 70, 229, 0.04);
  border-radius: 18px;
  padding: 22px 24px;
  margin: 24px 0 28px;
}
.sum-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}
.sum-icon {
  width: 16px;
  height: 16px;
  color: #6366f1;
  flex-shrink: 0;
}
.sum-header h3 {
  font-size: 0.92rem;
  font-weight: 800;
  color: #3730a3;
  margin: 0;
  white-space: nowrap;
}
.sum-header .src {
  margin-left: auto;
  font-size: 0.68rem;
  font-weight: 700;
  color: #6d28d9;
  background: #ede9fe;
  padding: 3px 9px;
  border-radius: 999px;
  white-space: nowrap;
}
.sum-body {
  font-size: 0.95rem;
  font-weight: 500;
  line-height: 1.7;
  color: #1e1b4b;
  margin: 0;
  white-space: pre-line;
  word-break: keep-all;
  letter-spacing: -0.3px;
}

/* 번들 묶음 리스트 */
.bundle {
  margin: 0 0 32px;
}
.bundle-head {
  margin: 0 0 14px;
}
.bundle-title {
  display: flex;
  align-items: center;
  gap: 8px;
}
.bundle-no {
  font-size: 0.7rem;
  font-weight: 800;
  color: #fff;
  background: var(--navy);
  padding: 4px 10px;
  border-radius: 999px;
  flex-shrink: 0;
}
.bundle-title h2 {
  font-size: 1.25rem;
  font-weight: 800;
  letter-spacing: -0.5px;
  color: var(--text);
  line-height: 1.4;
}
.storyline {
  margin: 10px 0 0;
  font-size: 0.9rem;
  line-height: 1.65;
  color: var(--text-sub);
  word-break: keep-all;
  white-space: pre-line;
  letter-spacing: -0.2px;
}
.ai-tag {
  font-size: 0.64rem;
  font-weight: 800;
  color: #fff;
  background: linear-gradient(120deg, #4f46e5, #7c3aed);
  padding: 2px 7px;
  border-radius: 6px;
  margin-right: 4px;
  vertical-align: middle;
}

/* 추천 리스트 및 개별 카드 */
.rec-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.rec-card {
  display: flex;
  align-items: center;
  gap: 20px;
  background: #fff;
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 18px 24px;
  transition: transform 0.2s, box-shadow 0.2s, background-color 0.2s;
  text-decoration: none;
}
.rec-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-hover);
  background-color: #fafbfd;
}
.thumb {
  width: 58px;
  height: 58px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 4px 8px rgba(0,0,0,0.04);
}
.card-text-badge {
  font-size: 0.84rem;
  font-weight: 800;
  color: #fff;
  letter-spacing: -0.3px;
}
.body {
  flex: 1;
  min-width: 0;
}
.cat {
  font-size: 0.7rem;
  font-weight: 700;
  color: var(--teal);
  background: #e6f4f1;
  padding: 2px 8px;
  border-radius: 6px;
  display: inline-block;
  margin-bottom: 6px;
}
.body h3 {
  font-size: 0.98rem;
  font-weight: 700;
  margin: 0 0 6px;
  color: var(--text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  letter-spacing: -0.3px;
}
.reason {
  font-size: 0.85rem;
  color: var(--text-sub);
  line-height: 1.55;
  margin: 0;
  word-break: keep-all;
  letter-spacing: -0.2px;
}
.go {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--bg);
  color: var(--text-sub);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: background 0.15s, color 0.15s;
}
.go svg {
  width: 14px;
  height: 14px;
  stroke-width: 3;
}
.rec-card:hover .go {
  background: var(--navy);
  color: #fff;
}

/* 하단 액션 버튼 */
.actions {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-top: 34px;
}
.btn-refresh {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.refresh-icon {
  width: 14px;
  height: 14px;
  stroke: var(--navy);
  transition: transform 0.4s ease;
  flex-shrink: 0;
}
.btn-refresh:hover .refresh-icon {
  transform: rotate(-180deg);
}
.arrow-right-icon {
  width: 14px;
  height: 14px;
  stroke: #fff;
  transition: transform 0.15s ease;
  flex-shrink: 0;
}
.actions .btn-navy {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.actions .btn-navy:hover .arrow-right-icon {
  transform: translateX(3px);
}

@media (max-width: 560px) {
  .reason {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
  .actions {
    flex-direction: column;
    align-items: stretch;
  }
  .actions .btn {
    text-align: center;
    justify-content: center;
  }
}
</style>
