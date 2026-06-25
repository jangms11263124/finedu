<script setup>
import { onMounted, ref, watch, computed } from 'vue'
import { RouterLink } from 'vue-router'
import api from '@/api'
import { useAuthStore } from '@/stores/auth'
import CommunityTabs from '@/components/community/CommunityTabs.vue'

const auth = useAuthStore()

const boards = [
  { key: '', label: '전체' },
  { key: 'free', label: '자유게시판' },
  { key: 'review', label: '후기게시판' },
  { key: 'info', label: '정보게시판' },
  { key: 'qna', label: '질문게시판' },
  { key: 'study', label: '스터디 모집' },
]

const posts = ref([])
const loading = ref(true)
const board = ref('')
const keyword = ref('')
const sortBy = ref('created_at') // 정렬 기준 ('created_at' | 'views' | 'comment_count' | 'seq')
const sortOrder = ref('desc') // 정렬 순서 ('asc' | 'desc')

// 페이지네이션 관련 상태값
const currentPage = ref(1)
const postsPerPage = 10

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

// 필터, 키워드, 정렬방식 변경 시 첫 페이지로 리셋
watch([board, keyword, sortBy, sortOrder], () => {
  currentPage.value = 1
})

watch(board, load)

// 게시글 데이터 전처리 (정렬 및 순번 할당)
const processedPosts = computed(() => {
  const notices = posts.value.filter(p => p.board === 'notice').map(p => ({
    ...p,
    isNotice: true,
    seqNo: '공지'
  }))
  
  const normals = posts.value.filter(p => p.board !== 'notice')
  
  // 가입 순번(오름차순) 맵핑을 위해 등록일 순 정렬 및 번호 매기기
  const chronologicalNormals = [...normals].sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
  const idMap = new Map()
  chronologicalNormals.forEach((p, idx) => {
    idMap.set(p.id, idx + 1)
  })
  
  // 정렬 옵션에 따라 일반 게시글 정렬
  let sortedNormals = [...normals]
  if (sortBy.value === 'views') {
    sortedNormals.sort((a, b) => sortOrder.value === 'asc' ? a.views - b.views : b.views - a.views)
  } else if (sortBy.value === 'comment_count') {
    sortedNormals.sort((a, b) => sortOrder.value === 'asc' ? a.comment_count - b.comment_count : b.comment_count - a.comment_count)
  } else if (sortBy.value === 'seq') {
    sortedNormals.sort((a, b) => {
      const seqA = idMap.get(a.id)
      const seqB = idMap.get(b.id)
      return sortOrder.value === 'asc' ? seqA - seqB : seqB - seqA
    })
  } else {
    // 기본값: 최신 작성순
    sortedNormals.sort((a, b) => {
      const dateA = new Date(a.created_at)
      const dateB = new Date(b.created_at)
      return sortOrder.value === 'asc' ? dateA - dateB : dateB - dateA
    })
  }
  
  const processedNormals = sortedNormals.map(p => ({
    ...p,
    isNotice: false,
    seqNo: idMap.get(p.id)
  }))
  
  // 공지는 항상 리스트 최상단에 고정
  return [...notices, ...processedNormals]
})

// 현재 페이지에 렌더링할 게시글
const displayedPosts = computed(() => {
  const start = (currentPage.value - 1) * postsPerPage
  const end = start + postsPerPage
  return processedPosts.value.slice(start, end)
})

// 총 페이지 수 계산
const totalPages = computed(() => {
  return Math.ceil(processedPosts.value.length / postsPerPage) || 1
})

// 5개 단위로 페이지 번호 그룹핑 (1~5, 6~10 등)
const pageNumbers = computed(() => {
  const total = totalPages.value
  const blockIndex = Math.floor((currentPage.value - 1) / 5)
  const start = blockIndex * 5 + 1
  const end = Math.min(total, start + 4)
  const arr = []
  for (let i = start; i <= end; i++) arr.push(i)
  return arr
})

function changePage(page) {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

function fmt(dt) {
  return new Date(dt).toLocaleDateString('ko-KR', {
    month: '2-digit',
    day: '2-digit',
  })
}

function toggleSort(field) {
  if (sortBy.value === field) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortBy.value = field
    sortOrder.value = field === 'seq' ? 'asc' : 'desc'
  }
}

function onDropdownChange() {
  sortOrder.value = sortBy.value === 'seq' ? 'asc' : 'desc'
}

onMounted(load)
</script>

<template>
  <main class="community">
    <div class="container">
      <CommunityTabs />

      <!-- 게시판 필터 (첫 번째 줄) -->
      <div class="filter-row">
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
      </div>

      <!-- 검색 + 정렬 + 글쓰기 (두 번째 줄) -->
      <div class="toolbar">
        <select v-model="sortBy" @change="onDropdownChange" class="sort-select">
          <option value="created_at">최신순</option>
          <option value="views">조회순</option>
          <option value="comment_count">댓글순</option>
          <option value="seq">번호순</option>
        </select>

        <form class="search" @submit.prevent="load">
          <input v-model="keyword" placeholder="제목 검색" />
          <button type="submit" aria-label="검색">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="search-icon">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.637 10.637Z" />
            </svg>
          </button>
        </form>

        <RouterLink to="/community/write" class="btn btn-navy write">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="write-icon">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L6.83 20.04a4.5 4.5 0 0 1-1.897 1.13l-2.685.8.8-2.685a4.5 4.5 0 0 1 1.13-1.897L16.863 4.487Zm0 0L19.5 7.125" />
          </svg>
          글쓰기
        </RouterLink>
      </div>

      <p v-if="loading" class="empty">불러오는 중...</p>
      <p v-else-if="!processedPosts.length" class="empty">
        아직 게시글이 없어요. 첫 글을 작성해보세요!
      </p>

      <div v-else>
        <!-- 게시글 목록 -->
        <ul class="post-list">
          <li class="head-row">
            <span class="c-no sortable" @click="toggleSort('seq')">
              No <span class="arrow" v-if="sortBy === 'seq'">{{ sortOrder === 'asc' ? '▲' : '▼' }}</span>
            </span>
            <span class="c-board">게시판</span>
            <span class="c-title">제목</span>
            <span class="c-author">작성자</span>
            <span class="c-comments sortable" @click="toggleSort('comment_count')">
              댓글 <span class="arrow" v-if="sortBy === 'comment_count'">{{ sortOrder === 'asc' ? '▲' : '▼' }}</span>
            </span>
            <span class="c-meta sortable" @click="toggleSort('views')">
              조회 <span class="arrow" v-if="sortBy === 'views'">{{ sortOrder === 'asc' ? '▲' : '▼' }}</span>
            </span>
            <span class="c-date sortable" @click="toggleSort('created_at')">
              날짜 <span class="arrow" v-if="sortBy === 'created_at'">{{ sortOrder === 'asc' ? '▲' : '▼' }}</span>
            </span>
          </li>
          <RouterLink
            v-for="p in displayedPosts"
            :key="p.id"
            :to="`/community/${p.id}`"
            class="row"
          >
            <!-- No -->
            <span class="c-no" :class="{ 'text-notice': p.isNotice }">
              {{ p.seqNo }}
            </span>
            
            <!-- 게시판 -->
            <span class="c-board">
              <em :class="{ 'badge-notice': p.isNotice }">{{ p.board_display }}</em>
            </span>
            
            <!-- 제목 -->
            <span class="c-title" :class="{ 'title-notice': p.isNotice }">
              {{ p.title }}
            </span>
            
            <span class="c-author">{{ p.author }}</span>
            <span class="c-comments">{{ p.comment_count }}</span>
            <span class="c-meta">{{ p.views.toLocaleString() }}</span>
            <span class="c-date">{{ fmt(p.created_at) }}</span>
          </RouterLink>
        </ul>

        <!-- 페이지네이션 -->
        <div v-if="totalPages > 1" class="pagination">
          <button 
            class="page-btn" 
            :disabled="currentPage === 1" 
            @click="changePage(Math.max(1, currentPage - 5))"
          >
            &lt;
          </button>
          <button
            v-for="num in pageNumbers"
            :key="num"
            class="page-num"
            :class="{ active: currentPage === num }"
            @click="changePage(num)"
          >
            {{ num }}
          </button>
          <button 
            class="page-btn" 
            :disabled="currentPage === totalPages" 
            @click="changePage(Math.min(totalPages, currentPage + 5))"
          >
            &gt;
          </button>
        </div>
      </div>
    </div>
  </main>
</template>

<style scoped>
.community {
  padding: 36px 0 20px;
  min-height: 70vh;
}
.filter-row {
  margin-bottom: 12px;
}
.filters {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}
.chip {
  background: #fff;
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
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
.toolbar {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}
.search {
  display: flex;
  align-items: center;
  gap: 6px;
  background: #fff;
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  padding: 0 14px;
  width: 240px;
  height: 38px;
  box-sizing: border-box;
}
.search input {
  border: none;
  outline: none;
  font-size: 0.84rem;
  width: 100%;
}
.search button {
  background: transparent;
  padding: 0;
  display: flex;
  align-items: center;
}
.search-icon {
  width: 16px;
  height: 16px;
  stroke: var(--text-mute);
  stroke-width: 2.5;
  display: block;
}
.sort-select {
  background: #fff;
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  padding: 0 30px 0 14px;
  font-size: 0.84rem;
  font-weight: 600;
  color: var(--text-sub);
  outline: none;
  cursor: pointer;
  margin-right: 8px;
  height: 38px;
  min-width: 96px;
  box-sizing: border-box;
  appearance: none;
  -webkit-appearance: none;
  background-image: url("data:image/svg+xml;charset=utf-8,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3E%3Cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='m6 8 4 4 4-4'/%3E%3C/svg%3E");
  background-position: right 10px center;
  background-repeat: no-repeat;
  background-size: 16px;
  transition: border-color 0.15s ease;
}
.sort-select:focus,
.sort-select:hover {
  border-color: var(--navy);
}
.write {
  margin-left: auto;
  padding: 0 16px;
  font-size: 0.86rem;
  white-space: nowrap;
  height: 38px;
  box-sizing: border-box;
}
.write-icon {
  width: 14px;
  height: 14px;
  stroke: currentColor;
  flex-shrink: 0;
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
  grid-template-columns: 60px 100px 1fr 100px 60px 60px 80px;
  align-items: center;
  gap: 10px;
  padding: 13px 18px;
  border-bottom: 1px solid var(--line);
  font-size: 0.88rem;
}
.head-row {
  background: #f1f3f9;
  color: var(--text);
  font-size: 0.8rem;
  font-weight: 700;
  border-bottom: 2px solid var(--line);
}
.head-row span {
  color: var(--text);
  font-weight: 700;
  text-align: center;
}
.head-row span.sortable {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  cursor: pointer;
  user-select: none;
  transition: color 0.12s ease;
}
.head-row span.sortable:hover {
  color: var(--navy);
}
.head-row span.sortable .arrow {
  font-size: 0.65rem;
}
.head-row .c-title {
  text-align: left;
}
.row:last-child {
  border-bottom: none;
}
.row:hover {
  background: var(--bg);
}
.c-no {
  font-size: 0.8rem;
  color: var(--text-mute);
  text-align: center;
}
.c-no.text-notice {
  font-weight: 700;
  color: var(--navy);
}
.c-board {
  display: flex;
  justify-content: center;
}
.c-board em {
  font-style: normal;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-sub);
}
.c-board em.badge-notice {
  font-weight: 700;
  color: var(--navy);
}
.c-title {
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.c-title.title-notice {
  font-weight: 700;
}
.c-comments {
  color: var(--text-mute);
  font-size: 0.8rem;
  text-align: center;
}
.c-author,
.c-meta,
.c-date {
  color: var(--text-mute);
  font-size: 0.8rem;
  text-align: center;
}
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  margin-top: 24px;
}
.page-btn,
.page-num {
  background: #fff;
  border: 1px solid var(--line);
  color: var(--text-sub);
  width: 32px;
  height: 32px;
  border-radius: 6px;
  display: grid;
  place-items: center;
  font-size: 0.86rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.12s;
}
.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.page-btn:not(:disabled):hover,
.page-num:hover {
  border-color: var(--navy);
  color: var(--navy);
}
.page-num.active {
  background: var(--navy);
  border-color: var(--navy);
  color: #fff;
}
@media (max-width: 620px) {
  .row,
  .head-row {
    grid-template-columns: 70px 1fr 56px;
  }
  .c-no,
  .c-author,
  .c-comments,
  .c-meta,
  .c-date {
    display: none;
  }
}
</style>
