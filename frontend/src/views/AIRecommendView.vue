<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import api from '@/api'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

const loading = ref(true)
const summary = ref('')
const items = ref([])
const source = ref('') // 'ai' | 'rule'
const error = ref('')

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

function getEbti() {
  try {
    return JSON.parse(localStorage.getItem('ebtiResult') || 'null')
  } catch {
    return null
  }
}

const hasEbti = ref(!!getEbti())

async function fetchRecommend() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.post('/contents/ai-recommend/', {
      ebti: getEbti(),
      region: auth.user?.region || '',
    })
    summary.value = data.summary
    items.value = data.items
    source.value = data.source
  } catch {
    error.value = '추천을 불러오지 못했어요. 잠시 후 다시 시도해주세요.'
  } finally {
    loading.value = false
  }
}

onMounted(fetchRecommend)
</script>

<template>
  <main class="ai">
    <div class="container">
      <!-- 헤더 -->
      <header class="hero">
        <span class="badge">🤖 AI 맞춤 추천</span>
        <h1>{{ auth.user?.nickname }}님을 위한 콘텐츠</h1>
        <p class="lead">
          EBTI 결과 · 관심사 · 학습 이력 · 커뮤니티 활동 · 지역을 종합해
          AI가 맞춤 콘텐츠를 골랐어요.
        </p>
      </header>

      <!-- 분석에 사용된 신호 칩 -->
      <div class="signals">
        <span class="chip" :class="{ off: !hasEbti }">
          {{ hasEbti ? '✅' : '⬜' }} EBTI 결과
        </span>
        <span class="chip">✅ 관심 콘텐츠</span>
        <span class="chip">✅ 커뮤니티 활동</span>
        <span class="chip">✅ 최근 인기 주제</span>
        <span class="chip" :class="{ off: !auth.user?.region }">
          {{ auth.user?.region ? '✅' : '⬜' }} 지역
        </span>
      </div>

      <p v-if="!hasEbti" class="ebti-hint">
        💡 <RouterLink to="/ebti">EBTI 테스트</RouterLink>를 먼저 하면 더 정확한 추천을 받을 수 있어요.
      </p>

      <!-- 로딩 -->
      <div v-if="loading" class="loading">
        <span class="spinner"></span>
        <p>AI가 회원님께 맞는 콘텐츠를 고르고 있어요...</p>
      </div>

      <p v-else-if="error" class="error">{{ error }}</p>

      <template v-else>
        <!-- AI 요약 -->
        <div class="summary">
          <span class="ico">✨</span>
          <p>{{ summary }}</p>
          <span class="src">{{ source === 'ai' ? 'AI 분석' : '추천 엔진' }}</span>
        </div>

        <!-- 추천 카드 -->
        <div class="rec-list">
          <RouterLink
            v-for="(it, i) in items"
            :key="it.content.id"
            :to="`/contents/${it.content.id}`"
            class="rec-card"
          >
            <span class="rank">{{ i + 1 }}</span>
            <span
              class="thumb"
              :style="{ background: gradients[it.content.category] || gradients.etc }"
            >{{ icons[it.content.category] || '📰' }}</span>
            <div class="body">
              <span class="cat">{{ it.content.category_display }}</span>
              <h3>{{ it.content.title }}</h3>
              <p class="reason">
                <span class="ai-tag">AI</span> {{ it.reason }}
              </p>
            </div>
            <span class="go">›</span>
          </RouterLink>
        </div>

        <div class="actions">
          <button class="btn btn-outline" @click="fetchRecommend">🔄 다시 추천받기</button>
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
.loading {
  text-align: center;
  padding: 60px 0;
  color: var(--text-sub);
}
.spinner {
  display: inline-block;
  width: 38px;
  height: 38px;
  border: 4px solid var(--line);
  border-top-color: var(--navy);
  border-radius: 999px;
  animation: spin 0.8s linear infinite;
  margin-bottom: 16px;
}
@keyframes spin {
  to { transform: rotate(360deg); }
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
.rank {
  width: 26px;
  text-align: center;
  font-weight: 800;
  font-size: 1.1rem;
  color: var(--navy);
  flex-shrink: 0;
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
