<script setup>
import { ref } from 'vue'

const keyword = ref('')
// 추천 검색어 (데모)
const suggestions = ['금리', '인플레이션', 'ETF', '복리', '환율']

function search(term) {
  keyword.value = term || keyword.value
  // 실제 서비스에서는 용어 사전 검색 페이지로 이동
}
</script>

<template>
  <div class="widget">
    <div class="head">
      <span class="ico">📖</span>
      <strong>경제 용어 사전</strong>
    </div>
    <p class="desc">어려운 경제 용어, 검색해서 바로 찾아보세요.</p>
    <form class="search" @submit.prevent="search()">
      <input v-model="keyword" placeholder="용어를 검색해보세요" />
      <button type="submit" aria-label="검색">🔍</button>
    </form>
    <div class="chips">
      <button
        v-for="s in suggestions"
        :key="s"
        class="chip"
        @click="search(s)"
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
  font-size: 0.85rem;
  padding: 0;
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
}
.chip:hover {
  background: #d3ebe6;
}
</style>
