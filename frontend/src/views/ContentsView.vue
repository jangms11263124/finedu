<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import api from '@/api'
import { useAuthStore } from '@/stores/auth'
import Pagination from '@/components/common/Pagination.vue'

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
  if (!auth.isLoggedIn) return alert('로그인이 필요합니다.')
  const { data } = await api.post(`/contents/${c.id}/like/`)
  c.is_liked = data.liked
  c.like_count = data.like_count
}

onMounted(load)
</script>

<template>
  <main class="contents">
    <div class="container">
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
            :style="{ background: gradients[c.category] || gradients.etc }"
          >
            <span class="emoji">{{ icons[c.category] || '📰' }}</span>
            <span class="play">▶</span>
            <button
              class="heart"
              :class="{ on: c.is_liked }"
              @click.prevent="toggleLike(c)"
            >
              {{ c.is_liked ? '❤️' : '🤍' }}
            </button>
          </div>
          <div class="body">
            <span class="badge">{{ c.category_display }}</span>
            <h3>{{ c.title }}</h3>
            <div class="meta">
              <span>👁 {{ c.views.toLocaleString() }}</span>
              <span>❤️ {{ c.like_count }}</span>
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
  padding: 8px 12px;
  font-size: 0.84rem;
  background: #fff;
  outline: none;
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
  aspect-ratio: 4 / 3;
  display: grid;
  place-items: center;
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
  font-size: 0.9rem;
  display: grid;
  place-items: center;
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
  gap: 12px;
  font-size: 0.76rem;
  color: var(--text-mute);
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
}
</style>
