<script setup>
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import { getEventTheme } from '@/utils/eventTheme'

const props = defineProps({
  event: { type: Object, required: true },
})

const theme = computed(() => getEventTheme(props.event))

const statusClass = { open: 'open', closed: 'closed', ended: 'ended' }
</script>

<template>
  <RouterLink :to="`/events/${event.id}`" class="ev-card">
    <div class="thumb" :style="theme.image ? {} : { background: theme.gradient }">
      <img v-if="theme.image" :src="theme.image" :alt="event.title" class="thumb-img" />
      <template v-else>
        <span class="icon main">{{ theme.icons[0] }}</span>
        <span class="icon sub1">{{ theme.icons[1] }}</span>
        <span class="icon sub2">{{ theme.icons[2] }}</span>
      </template>
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
  </RouterLink>
</template>

<style scoped>
.ev-card {
  display: block;
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
  display: grid;
  place-items: center;
  overflow: hidden;
}
.thumb-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.icon {
  position: absolute;
  filter: drop-shadow(0 3px 8px rgba(0, 0, 0, 0.35));
  user-select: none;
  pointer-events: none;
}
.icon.main {
  font-size: 3.2rem;
  right: 22px;
  top: 50%;
  transform: translateY(-60%);
}
.icon.sub1 {
  font-size: 1.8rem;
  right: 72px;
  top: 14px;
  opacity: 0.85;
}
.icon.sub2 {
  font-size: 1.6rem;
  right: 16px;
  bottom: 14px;
  opacity: 0.75;
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
.badge.open   { background: var(--green); }
.badge.closed { background: #d97706; }
.badge.ended  { background: #6b7280; }
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
  min-height: calc(1.4em * 2);
}
.period {
  font-size: 0.78rem;
  color: var(--text-sub);
}
</style>
