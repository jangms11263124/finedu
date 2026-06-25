<script setup>
import { nextTick, onMounted, ref, watch } from 'vue'

const props = defineProps({
  items: { type: Array, default: () => [] },
  itemKey: { type: String, default: 'id' },
})

const track = ref(null)
const atStart = ref(true)
const atEnd = ref(false)

function update() {
  const el = track.value
  if (!el) return
  atStart.value = el.scrollLeft <= 2
  atEnd.value = el.scrollLeft + el.clientWidth >= el.scrollWidth - 2
}

function scrollBy(dir) {
  const el = track.value
  if (!el) return
  // 보이는 너비의 약 90%만큼 이동
  el.scrollBy({ left: dir * el.clientWidth * 0.9, behavior: 'smooth' })
}

watch(() => props.items, () => nextTick(update))
onMounted(() => nextTick(update))
</script>

<template>
  <div class="carousel">
    <button
      class="nav prev"
      :class="{ hidden: atStart }"
      aria-label="이전"
      @click="scrollBy(-1)"
    >
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
        <polyline points="15 18 9 12 15 6"></polyline>
      </svg>
    </button>

    <div ref="track" class="track" @scroll="update">
      <div v-for="item in items" :key="item[itemKey]" class="slide">
        <slot :item="item" />
      </div>
    </div>

    <button
      class="nav next"
      :class="{ hidden: atEnd }"
      aria-label="다음"
      @click="scrollBy(1)"
    >
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
        <polyline points="9 18 15 12 9 6"></polyline>
      </svg>
    </button>
  </div>
</template>

<style scoped>
.carousel {
  position: relative;
}
.track {
  display: flex;
  gap: 16px;
  overflow-x: auto;
  scroll-behavior: smooth;
  scrollbar-width: none;
  padding: 4px 2px;
}
.track::-webkit-scrollbar {
  display: none;
}
.slide {
  flex: 0 0 calc((100% - 48px) / 4);
}
.nav {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  z-index: 5;
  width: 40px;
  height: 40px;
  border-radius: 999px;
  background: #fff;
  border: 1px solid var(--line);
  box-shadow: 0 4px 14px rgba(27, 42, 89, 0.16);
  color: var(--navy);
  display: grid;
  place-items: center;
  transition: opacity 0.15s, transform 0.12s, background-color 0.15s, color 0.15s;
}
.nav svg {
  width: 16px;
  height: 16px;
  transition: transform 0.12s ease;
}
.nav:hover {
  background: var(--navy);
  color: #fff;
}
.nav:hover svg {
  transform: scale(1.15);
}
.nav:active {
  transform: translateY(-50%) scale(0.9);
}
.nav.prev {
  left: -12px;
}
.nav.next {
  right: -12px;
}
.nav.hidden {
  opacity: 0;
  pointer-events: none;
}
@media (max-width: 900px) {
  .slide {
    flex: 0 0 calc((100% - 16px) / 2);
  }
}
@media (max-width: 560px) {
  .slide {
    flex: 0 0 85%;
  }
}
</style>
