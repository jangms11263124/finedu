<script setup>
defineProps({
  event: { type: Object, required: true },
})

const statusClass = {
  open: 'open',
  closed: 'closed',
  ended: 'ended',
}
</script>

<template>
  <article class="ev-card">
    <div class="thumb">
      <span class="emoji">🎓</span>
      <span class="badge" :class="statusClass[event.status]">
        {{ event.status_display }}
      </span>
    </div>
    <div class="body">
      <span class="host">{{ event.host }}</span>
      <h3>{{ event.title }}</h3>
      <p class="period" v-if="event.start_date">
        🗓 {{ event.start_date }} ~ {{ event.end_date }}
      </p>
    </div>
  </article>
</template>

<style scoped>
.ev-card {
  background: #fff;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  overflow: hidden;
  transition: transform 0.14s, box-shadow 0.14s;
  cursor: pointer;
}
.ev-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-hover);
}
.thumb {
  position: relative;
  aspect-ratio: 16 / 9;
  background: linear-gradient(135deg, #0b4f49, #0f766e 55%, #15803d);
  display: grid;
  place-items: center;
}
.emoji {
  font-size: 2.4rem;
  filter: drop-shadow(0 2px 6px rgba(0, 0, 0, 0.3));
}
.badge {
  position: absolute;
  top: 10px;
  left: 10px;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 999px;
  color: #fff;
}
.badge.open {
  background: var(--green);
}
.badge.closed {
  background: #d97706;
}
.badge.ended {
  background: #6b7280;
}
.body {
  padding: 14px 16px 18px;
}
.host {
  font-size: 0.75rem;
  color: var(--teal);
  font-weight: 700;
}
h3 {
  font-size: 1rem;
  font-weight: 700;
  line-height: 1.4;
  margin: 6px 0 10px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  /* 제목이 1줄이든 2줄이든 항상 2줄 높이를 확보해 카드 높이를 통일 */
  min-height: calc(1.4em * 2);
}
.period {
  font-size: 0.78rem;
  color: var(--text-sub);
}
</style>
