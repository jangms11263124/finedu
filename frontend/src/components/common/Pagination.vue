<script setup>
import { computed } from 'vue'

const props = defineProps({
  page: { type: Number, required: true },
  totalPages: { type: Number, required: true },
})
const emit = defineEmits(['change'])

// 현재 페이지 주변 최대 5개 번호
const pages = computed(() => {
  const total = props.totalPages
  let start = Math.max(1, props.page - 2)
  let end = Math.min(total, start + 4)
  start = Math.max(1, end - 4)
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
    <button class="arrow" :disabled="page === 1" @click="go(page - 1)">‹</button>
    <button
      v-for="p in pages"
      :key="p"
      class="num"
      :class="{ on: p === page }"
      @click="go(p)"
    >
      {{ p }}
    </button>
    <button class="arrow" :disabled="page === totalPages" @click="go(page + 1)">›</button>
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
  min-width: 34px;
  height: 34px;
  border-radius: 9px;
  border: 1px solid var(--line);
  background: #fff;
  font-size: 0.86rem;
  font-weight: 600;
  color: var(--text-sub);
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
