<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const keyword = ref('')

// 청년들이 실제 많이 검색하는 실용 키워드 (사전 데이터 연동 확인 완료)
const suggestions = ['연말정산', 'CMA', '국민주택', 'ETF', '기준금리', '레버리지 효과', '손익분기점']

// 검색 버튼/엔터 → 경제 용어 사전으로 이동하며 검색어 전달
function go() {
  const q = keyword.value.trim()
  if (!q) return
  router.push({ name: 'glossary', query: { term: q } })
}

// 키워드 칩 클릭 시 검색창 입력 및 즉시 검색 실행
function searchImmediately(term) {
  keyword.value = term
  go()
}
</script>

<template>
  <div class="widget">
    <div class="head">
      <!-- 깔끔한 책 오픈 SVG 아이콘 -->
      <svg class="head-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path>
        <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path>
      </svg>
      <strong>경제 용어 사전</strong>
    </div>
    <p class="desc">어려운 경제 용어, 검색해서 바로 찾아보세요.</p>
    <form class="search" @submit.prevent="go">
      <input v-model="keyword" placeholder="용어를 검색해보세요" />
      <button type="submit" aria-label="검색">
        <!-- 깔끔한 돋보기 SVG 아이콘 -->
        <svg class="search-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>
      </button>
    </form>
    <div class="chips">
      <button
        v-for="s in suggestions"
        :key="s"
        class="chip"
        @click="searchImmediately(s)"
      >
        #{{ s }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.widget {
  background: #fff;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 18px;
  box-shadow: var(--shadow);
}
.head {
  display: flex;
  align-items: center;
  gap: 7px;
  margin-bottom: 8px;
}
.head-icon {
  width: 15px;
  height: 15px;
  color: var(--navy);
  flex-shrink: 0;
}
.head strong {
  font-size: 0.95rem;
}
.desc {
  font-size: 0.8rem;
  color: var(--text-sub);
  line-height: 1.45;
  margin-bottom: 12px;
}
.search {
  display: flex;
  align-items: center;
  gap: 6px;
  background: var(--bg);
  border: 1px solid var(--line);
  border-radius: 999px;
  padding: 8px 14px;
  transition: border-color 0.15s, box-shadow 0.15s;
}
.search:focus-within {
  border-color: var(--navy);
  background: #ffffff;
  box-shadow: 0 0 0 2px rgba(27, 42, 89, 0.05);
}
.search input {
  flex: 1;
  border: none;
  background: transparent;
  outline: none;
  font-size: 0.84rem;
}
.search button {
  background: transparent;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}
.search-icon {
  width: 14px;
  height: 14px;
  color: var(--text-sub);
  transition: color 0.15s;
}
.search button:hover .search-icon {
  color: var(--navy);
}
.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 12px;
}
.chip {
  font-size: 0.76rem;
  font-weight: 600;
  color: var(--teal);
  background: #e6f4f1;
  border-radius: 999px;
  padding: 5px 10px;
  transition: background 0.15s, color 0.15s;
}
.chip:hover {
  background: #d3ebe6;
}
</style>
