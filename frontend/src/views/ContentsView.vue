<script setup>
import { onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import api from '@/api'
import { useAuthStore } from '@/stores/auth'
import Pagination from '@/components/common/Pagination.vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const categories = [
  { key: '', label: '전체' },
  { key: 'economy', label: '경제' },
  { key: 'invest', label: '투자' },
  { key: 'saving', label: '저축' },
  { key: 'finance', label: '금융상품' },
  { key: 'society', label: '사회' },
]
const orderings = [
  { key: '', label: '최신순' },
  { key: 'views', label: '조회순' },
  { key: 'oldest', label: '오래된순' },
]

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

const items = ref([])
const count = ref(0)
const page = ref(1)
const totalPages = ref(1)
const loading = ref(true)

const category = ref('')
const ordering = ref('')
const keyword = ref('')

async function load() {
  loading.value = true
  try {
    const params = { page: page.value }
    if (category.value) params.category = category.value
    if (ordering.value) params.ordering = ordering.value
    if (keyword.value.trim()) params.q = keyword.value.trim()
    const { data } = await api.get('/contents/', { params })
    items.value = data.results
    count.value = data.count
    totalPages.value = data.total_pages
  } finally {
    loading.value = false
  }
}

function search() {
  page.value = 1
  load()
}
function reset() {
  category.value = ''
  ordering.value = ''
  keyword.value = ''
  page.value = 1
  load()
}
function changePage(p) {
  page.value = p
  load()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

async function toggleLike(c) {
  if (!auth.isLoggedIn) {
    if (confirm('로그인이 필요합니다. 로그인 페이지로 이동하시겠습니까?')) {
      router.push({ name: 'login', query: { redirect: route.fullPath } })
    }
    return
  }
  const { data } = await api.post(`/contents/${c.id}/like/`)
  c.is_liked = data.liked
  c.like_count = data.like_count
}

function applyQuery() {
  if (route.query.q) keyword.value = String(route.query.q)
  if (route.query.category) category.value = String(route.query.category)
}

watch(() => route.query, () => {
  applyQuery()
  page.value = 1
  load()
})

onMounted(() => {
  applyQuery()
  load()
})
</script>

<template>
  <main class="contents">
    <div class="container">
      <header class="head">
        <h1>콘텐츠 보기</h1>
        <p>유튜브 영상으로 쉽고 재미있게 금융/경제 지식을 배워보세요.</p>
      </header>

      <!-- AI 맞춤 추천 배너 -->
      <RouterLink to="/ai-recommend" class="ai-banner">
        <span class="ai-banner-glow"></span>
        <div class="ai-banner-text">
          <span class="ai-banner-badge">AI 맞춤 추천</span>
          <h2>나에게 딱 맞는 콘텐츠가 궁금하다면?</h2>
          <p>관심사 · 학습 이력 · EBTI 결과를 분석해 AI가 콘텐츠를 골라드려요.</p>
        </div>
        <span class="ai-banner-cta">맞춤 추천 받기 →</span>
      </RouterLink>

      <!-- 검색바 -->
      <div class="search-bar">
        <select v-model="category" @change="search">
          <option v-for="c in categories" :key="c.key" :value="c.key">{{ c.label }}</option>
        </select>
        <input
          v-model="keyword"
          placeholder="시리즈명·콘텐츠명·태그·서두 내용 키워드를 입력하세요."
          @keyup.enter="search"
        />
        <button class="btn btn-navy" @click="search">조회</button>
        <button class="btn btn-outline" @click="reset">↻ 초기화</button>
      </div>

      <!-- 카운트 + 정렬 -->
      <div class="result-head">
        <span class="count">📄 총 <strong>{{ count.toLocaleString() }}</strong>건</span>
        <select v-model="ordering" class="sort" @change="search">
          <option v-for="o in orderings" :key="o.key" :value="o.key">{{ o.label }}</option>
        </select>
      </div>

      <p v-if="loading" class="empty">불러오는 중...</p>
      <p v-else-if="!items.length" class="empty">검색 결과가 없습니다.</p>

      <!-- 카드 그리드 -->
      <div v-else class="grid">
        <RouterLink
          v-for="c in items"
          :key="c.id"
          :to="`/contents/${c.id}`"
          class="card"
        >
          <div
            class="thumb"
            :style="c.youtube_id ? {} : { background: gradients[c.category] || gradients.etc }"
          >
            <img
              v-if="c.youtube_id"
              :src="`https://img.youtube.com/vi/${c.youtube_id}/mqdefault.jpg`"
              :alt="c.title"
              class="thumb-img"
            />
            <span v-else class="emoji">{{ icons[c.category] || '📰' }}</span>
            <span class="play">▶</span>
            <button
              class="heart"
              :class="{ on: c.is_liked }"
              @click.prevent="toggleLike(c)"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke-width="2.5"
                stroke="currentColor"
                class="heart-icon"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12Z"
                />
              </svg>
            </button>
          </div>
          <div class="body">
            <span class="badge">{{ c.category_display }}</span>
            <h3>{{ c.title }}</h3>
            <div class="meta">
              <span>
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="meta-icon"><path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z" /><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" /></svg>
                {{ c.views.toLocaleString() }}
              </span>
              <span>
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="meta-icon heart-small"><path stroke-linecap="round" stroke-linejoin="round" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12Z" /></svg>
                {{ c.like_count }}
              </span>
              <span>
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="meta-icon"><path stroke-linecap="round" stroke-linejoin="round" d="M12 20.25c4.97 0 9-3.694 9-8.25s-4.03-8.25-9-8.25S3 7.444 3 12c0 2.104.859 4.023 2.273 5.48.432.447.74 1.04.586 1.641a4.483 4.483 0 0 1-1.923 2.07c-.464.248.035.75.502.578a11.97 11.97 0 0 0 3.42-1.48c.53-.18 1.09-.208 1.644-.208Z" /></svg>
                {{ c.comment_count }}
              </span>
            </div>
          </div>
        </RouterLink>
      </div>

      <Pagination :page="page" :total-pages="totalPages" @change="changePage" />
    </div>
  </main>
</template>

<style scoped>
.contents {
  padding: 30px 0 20px;
  min-height: 72vh;
}
.head {
  margin-bottom: 22px;
}
.head h1 {
  font-size: 1.7rem;
  font-weight: 800;
  letter-spacing: -0.6px;
}
.head p {
  margin-top: 8px;
  color: var(--text-sub);
  font-size: 0.92rem;
}
/* AI 맞춤 추천 배너 */
.ai-banner {
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  background: linear-gradient(120deg, #1b2a59, #4f46e5 60%, #7c3aed);
  border-radius: 16px;
  padding: 22px 26px;
  margin-bottom: 22px;
  color: #fff;
  box-shadow: var(--shadow);
  transition: transform 0.16s ease, box-shadow 0.16s ease;
}
.ai-banner:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-hover);
}
.ai-banner-glow {
  position: absolute;
  top: -40%;
  right: -5%;
  width: 220px;
  height: 220px;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.22), transparent 70%);
  pointer-events: none;
}
.ai-banner-text {
  position: relative;
  z-index: 1;
}
.ai-banner-badge {
  display: inline-block;
  font-size: 0.74rem;
  font-weight: 700;
  background: rgba(255, 255, 255, 0.18);
  padding: 4px 11px;
  border-radius: 999px;
}
.ai-banner-text h2 {
  font-size: 1.2rem;
  font-weight: 800;
  letter-spacing: -0.4px;
  margin: 10px 0 6px;
}
.ai-banner-text p {
  font-size: 0.86rem;
  color: rgba(255, 255, 255, 0.82);
  line-height: 1.5;
}
.ai-banner-cta {
  position: relative;
  z-index: 1;
  flex-shrink: 0;
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--navy);
  background: #fff;
  padding: 11px 18px;
  border-radius: 10px;
  white-space: nowrap;
  transition: transform 0.16s ease;
}
.ai-banner:hover .ai-banner-cta {
  transform: scale(1.04);
}
.search-bar {
  display: flex;
  gap: 8px;
  background: #fff;
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 14px;
  box-shadow: var(--shadow);
}
.search-bar select,
.search-bar input {
  border: 1px solid var(--line);
  border-radius: 9px;
  padding: 11px 13px;
  font-size: 0.88rem;
  outline: none;
}
.search-bar select {
  flex-shrink: 0;
  appearance: none;
  -webkit-appearance: none;
  background-image: url("data:image/svg+xml;charset=utf-8,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3E%3Cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='m6 8 4 4 4-4'/%3E%3C/svg%3E");
  background-position: right 10px center;
  background-repeat: no-repeat;
  background-size: 18px;
  padding-right: 32px !important;
  cursor: pointer;
  background-color: #fff;
  transition: border-color 0.15s ease;
}
.search-bar select:focus,
.search-bar select:hover {
  border-color: var(--navy);
}
.search-bar input {
  flex: 1;
}
.search-bar input:focus {
  border-color: var(--navy);
}
.result-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 22px 0 14px;
}
.count {
  font-size: 0.92rem;
  color: var(--text-sub);
}
.count strong {
  color: var(--navy);
}
.sort {
  border: 1px solid var(--line);
  border-radius: 9px;
  padding: 8px 30px 8px 12px;
  font-size: 0.84rem;
  background: #fff;
  outline: none;
  appearance: none;
  -webkit-appearance: none;
  background-image: url("data:image/svg+xml;charset=utf-8,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3E%3Cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='m6 8 4 4 4-4'/%3E%3C/svg%3E");
  background-position: right 8px center;
  background-repeat: no-repeat;
  background-size: 16px;
  cursor: pointer;
  transition: border-color 0.15s ease;
}
.sort:focus,
.sort:hover {
  border-color: var(--navy);
}
.empty {
  text-align: center;
  color: var(--text-mute);
  padding: 60px 0;
}
.grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 18px;
}
.card {
  background: #fff;
  border: 1px solid var(--line);
  border-radius: 14px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.14s, box-shadow 0.14s;
}
.card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-hover);
}
.thumb {
  position: relative;
  aspect-ratio: 16 / 9;
  display: grid;
  place-items: center;
  overflow: hidden;
  background: #111;
}
.thumb-img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.emoji {
  font-size: 2.4rem;
  filter: drop-shadow(0 3px 8px rgba(0, 0, 0, 0.3));
}
.play {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 46px;
  height: 46px;
  border-radius: 999px;
  background: rgba(0, 0, 0, 0.45);
  color: #fff;
  display: grid;
  place-items: center;
  font-size: 1rem;
  padding-left: 3px;
  opacity: 0;
  transition: opacity 0.15s;
}
.card:hover .play {
  opacity: 1;
}
.heart {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 30px;
  height: 30px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(0, 0, 0, 0.05);
  display: grid;
  place-items: center;
  cursor: pointer;
  box-shadow: 0 2px 5px rgba(0,0,0,0.08);
  transition: all 0.2s ease;
}
.heart:hover {
  transform: scale(1.08);
  background: #fff;
  border-color: rgba(252, 165, 165, 0.5);
}
.heart .heart-icon {
  width: 15px;
  height: 15px;
  transition: transform 0.2s ease, fill 0.2s ease, stroke 0.2s ease;
  fill: transparent;
  stroke: var(--text-sub);
}
.heart:hover .heart-icon {
  stroke: #dc2626;
}
.heart.on {
  background: #fee2e2;
  border-color: #fca5a5;
}
.heart.on .heart-icon {
  fill: #dc2626;
  stroke: #dc2626;
  animation: heart-bounce 0.4s ease;
}
@keyframes heart-bounce {
  0% { transform: scale(1); }
  50% { transform: scale(1.35); }
  100% { transform: scale(1); }
}
.body {
  padding: 14px;
}
.badge {
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--teal);
  background: #e6f4f1;
  padding: 3px 8px;
  border-radius: 6px;
}
h3 {
  font-size: 0.95rem;
  font-weight: 700;
  line-height: 1.4;
  margin: 10px 0 12px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 2.6em;
}
.meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 0.76rem;
  color: var(--text-mute);
}
.meta span {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
.meta-icon {
  width: 14px;
  height: 14px;
  stroke: var(--text-mute);
}
.meta-icon.heart-small {
  fill: #fee2e2;
  stroke: #ef4444;
}
@media (max-width: 900px) {
  .grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
@media (max-width: 560px) {
  .grid {
    grid-template-columns: 1fr;
  }
  .search-bar {
    flex-wrap: wrap;
  }
  .ai-banner {
    flex-direction: column;
    align-items: flex-start;
    gap: 14px;
  }
  .ai-banner-cta {
    align-self: stretch;
    text-align: center;
  }
}
</style>
