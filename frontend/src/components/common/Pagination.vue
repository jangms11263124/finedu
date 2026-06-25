<script setup>
import { computed } from 'vue'

const props = defineProps({
  page: { type: Number, required: true },
  totalPages: { type: Number, required: true },
})
const emit = defineEmits(['change'])

// 5개 단위로 페이지 번호 그룹핑 (1~5, 6~10 등)
const pages = computed(() => {
  const total = props.totalPages
  const blockIndex = Math.floor((props.page - 1) / 5)
  const start = blockIndex * 5 + 1
  const end = Math.min(total, start + 4)
  const arr = []
  for (let i = start; i <= end; i++) arr.push(i)
  return arr
})

function go(p) {
  if (p >= 1 && p <= props.totalPages && p !== props.page) emit('change', p)
}
</script>

<template>
  <nav v-if="totalPages > 1" class="pagination">
    <button class="arrow" :disabled="page === 1" @click="go(Math.max(1, page - 5))">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" class="arrow-icon">
        <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5" />
      </svg>
    </button>
    <button
      v-for="p in pages"
      :key="p"
      class="num"
      :class="{ on: p === page }"
      @click="go(p)"
    >
      {{ p }}
    </button>
    <button class="arrow" :disabled="page === totalPages" @click="go(Math.min(totalPages, page + 5))">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" class="arrow-icon">
        <path stroke-linecap="round" stroke-linejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
      </svg>
    </button>
  </nav>
</template>

<style scoped>
.pagination {
  display: flex;
  justify-content: center;
  gap: 6px;
  margin: 30px 0 10px;
}
.num,
.arrow {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 34px;
  height: 34px;
  border-radius: 9px;
  border: 1px solid var(--line);
  background: #fff;
  font-size: 0.86rem;
  font-weight: 600;
  color: var(--text-sub);
  cursor: pointer;
  transition: all 0.15s ease;
}
.arrow-icon {
  width: 14px;
  height: 14px;
}
.num:hover,
.arrow:hover:not(:disabled) {
  border-color: var(--navy);
  color: var(--navy);
}
.num.on {
  background: var(--navy);
  color: #fff;
  border-color: var(--navy);
}
.arrow:disabled {
  opacity: 0.4;
  cursor: default;
}
</style>
