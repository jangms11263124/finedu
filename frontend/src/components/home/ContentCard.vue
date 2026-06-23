<script setup>
import { RouterLink } from 'vue-router'

const props = defineProps({
  content: { type: Object, required: true },
})

// 썸네일이 없을 때 카테고리별 그라데이션 플레이스홀더
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
</script>

<template>
  <RouterLink :to="`/contents/${content.id}`" class="card">
    <div
      class="thumb"
      :style="content.thumbnail
        ? { backgroundImage: `url(${content.thumbnail})` }
        : { background: gradients[content.category] || gradients.etc }"
    >
      <span v-if="!content.thumbnail" class="emoji">
        {{ icons[content.category] || '📰' }}
      </span>
      <span class="play">▶</span>
      <span class="tag">{{ content.category_display }}</span>
    </div>
    <div class="body">
      <h3>{{ content.title }}</h3>
      <p class="summary">{{ content.summary }}</p>
      <div class="meta">
        <span>👁 {{ content.views.toLocaleString() }}</span>
      </div>
    </div>
  </RouterLink>
</template>

<style scoped>
.card {
  display: block;
  background: #fff;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  overflow: hidden;
  transition: transform 0.14s, box-shadow 0.14s;
  cursor: pointer;
}
.card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-hover);
}
.thumb {
  position: relative;
  aspect-ratio: 16 / 10;
  background-size: cover;
  background-position: center;
  display: grid;
  place-items: center;
}
.emoji {
  font-size: 2rem;
  filter: drop-shadow(0 2px 6px rgba(0, 0, 0, 0.25));
}
.play {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 40px;
  height: 40px;
  border-radius: 999px;
  background: rgba(0, 0, 0, 0.45);
  color: #fff;
  display: grid;
  place-items: center;
  font-size: 0.9rem;
  padding-left: 3px;
  opacity: 0;
  transition: opacity 0.15s;
}
.card:hover .play {
  opacity: 1;
}
.tag {
  position: absolute;
  top: 8px;
  left: 8px;
  background: rgba(255, 255, 255, 0.92);
  color: var(--navy);
  font-size: 0.7rem;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: 999px;
}
.body {
  padding: 13px 14px 16px;
}
h3 {
  font-size: 0.95rem;
  font-weight: 700;
  line-height: 1.35;
  margin-bottom: 6px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.summary {
  font-size: 0.8rem;
  color: var(--text-sub);
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.meta {
  margin-top: 10px;
  font-size: 0.74rem;
  color: var(--text-mute);
}
</style>
