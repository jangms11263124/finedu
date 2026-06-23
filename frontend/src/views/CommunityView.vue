<script setup>
import { onMounted, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import api from '@/api'
import { useAuthStore } from '@/stores/auth'
import CommunityTabs from '@/components/community/CommunityTabs.vue'

const auth = useAuthStore()

const boards = [
  { key: '', label: '전체' },
  { key: 'free', label: '자유게시판' },
  { key: 'info', label: '정보공유' },
  { key: 'qna', label: '질문답변' },
]

const posts = ref([])
const loading = ref(true)
const board = ref('')
const keyword = ref('')

async function load() {
  loading.value = true
  try {
    const params = {}
    if (board.value) params.board = board.value
    if (keyword.value.trim()) params.q = keyword.value.trim()
    const { data } = await api.get('/posts/', { params })
    posts.value = data
  } finally {
    loading.value = false
  }
}

watch(board, load)

function fmt(dt) {
  return new Date(dt).toLocaleDateString('ko-KR', {
    month: '2-digit',
    day: '2-digit',
  })
}

onMounted(load)
</script>

<template>
  <main class="community">
    <div class="container">
      <CommunityTabs />

      <!-- 게시판 필터 + 검색 + 글쓰기 -->
      <div class="toolbar">
        <div class="filters">
          <button
            v-for="b in boards"
            :key="b.key"
            class="chip"
            :class="{ on: board === b.key }"
            @click="board = b.key"
          >
            {{ b.label }}
          </button>
        </div>
        <form class="search" @submit.prevent="load">
          <input v-model="keyword" placeholder="제목 검색" />
          <button type="submit">🔍</button>
        </form>
        <RouterLink to="/community/write" class="btn btn-navy write">
          ✏️ 글쓰기
        </RouterLink>
      </div>

      <p v-if="loading" class="empty">불러오는 중...</p>
      <p v-else-if="!posts.length" class="empty">
        아직 게시글이 없어요. 첫 글을 작성해보세요!
      </p>

      <ul v-else class="post-list">
        <li class="head-row">
          <span class="c-board">게시판</span>
          <span class="c-title">제목</span>
          <span class="c-author">작성자</span>
          <span class="c-meta">조회</span>
          <span class="c-date">날짜</span>
        </li>
        <RouterLink
          v-for="p in posts"
          :key="p.id"
          :to="`/community/${p.id}`"
          class="row"
        >
          <span class="c-board"><em>{{ p.board_display }}</em></span>
          <span class="c-title">
            {{ p.title }}
            <span v-if="p.comment_count" class="cc">[{{ p.comment_count }}]</span>
          </span>
          <span class="c-author">{{ p.author }}</span>
          <span class="c-meta">{{ p.views.toLocaleString() }}</span>
          <span class="c-date">{{ fmt(p.created_at) }}</span>
        </RouterLink>
      </ul>
    </div>
  </main>
</template>

<style scoped>
.community {
  padding: 36px 0 20px;
  min-height: 70vh;
}
.toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}
.filters {
  display: flex;
  gap: 6px;
}
.chip {
  background: #fff;
  border: 1px solid var(--line);
  border-radius: 999px;
  padding: 8px 14px;
  font-size: 0.84rem;
  font-weight: 600;
  color: var(--text-sub);
}
.chip.on {
  background: var(--navy);
  color: #fff;
  border-color: var(--navy);
}
.search {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 6px;
  background: #fff;
  border: 1px solid var(--line);
  border-radius: 999px;
  padding: 7px 14px;
}
.search input {
  border: none;
  outline: none;
  font-size: 0.84rem;
  width: 140px;
}
.search button {
  background: transparent;
  padding: 0;
}
.write {
  padding: 9px 16px;
  font-size: 0.86rem;
  white-space: nowrap;
}
.empty {
  color: var(--text-mute);
  padding: 50px 0;
  text-align: center;
}
.post-list {
  list-style: none;
  margin: 0;
  padding: 0;
  background: #fff;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  overflow: hidden;
}
.row,
.head-row {
  display: grid;
  grid-template-columns: 90px 1fr 90px 60px 60px;
  align-items: center;
  gap: 10px;
  padding: 13px 18px;
  border-bottom: 1px solid var(--line);
  font-size: 0.88rem;
}
.head-row {
  background: var(--bg);
  color: var(--text-mute);
  font-size: 0.78rem;
  font-weight: 600;
}
.row:last-child {
  border-bottom: none;
}
.row:hover {
  background: var(--bg);
}
.c-board em {
  font-style: normal;
  font-size: 0.74rem;
  color: var(--teal);
  font-weight: 700;
  background: #e6f4f1;
  padding: 3px 8px;
  border-radius: 6px;
}
.c-title {
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.cc {
  color: var(--green);
  font-weight: 700;
  font-size: 0.8rem;
}
.c-author,
.c-meta,
.c-date {
  color: var(--text-mute);
  font-size: 0.8rem;
  text-align: center;
}
@media (max-width: 620px) {
  .row,
  .head-row {
    grid-template-columns: 70px 1fr 56px;
  }
  .c-author,
  .head-row .c-meta {
    display: none;
  }
  .c-meta {
    display: none;
  }
}
</style>
