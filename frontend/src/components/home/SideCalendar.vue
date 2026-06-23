<script setup>
import { computed, ref } from 'vue'

const cursor = ref(new Date())
const today = new Date()

const label = computed(
  () => `${cursor.value.getFullYear()}.${String(cursor.value.getMonth() + 1).padStart(2, '0')}`
)

const days = computed(() => {
  const y = cursor.value.getFullYear()
  const m = cursor.value.getMonth()
  const first = new Date(y, m, 1).getDay()
  const total = new Date(y, m + 1, 0).getDate()
  const cells = []
  for (let i = 0; i < first; i++) cells.push(null)
  for (let d = 1; d <= total; d++) cells.push(d)
  return cells
})

function isToday(d) {
  return (
    d === today.getDate() &&
    cursor.value.getMonth() === today.getMonth() &&
    cursor.value.getFullYear() === today.getFullYear()
  )
}

// 데모용 일정 (이번 달 기준 day-of-month). 실제 서비스에서는 API 연동.
const schedules = [
  { day: 7, title: '출석 체크 이벤트', type: 'event' },
  { day: 15, title: '청소년 경제 캠프 신청 마감', type: 'deadline' },
  { day: 23, title: '오늘의 퀴즈 풀기', type: 'quiz' },
  { day: 25, title: '자산관리 클래스 시작', type: 'event' },
]

const typeColor = {
  event: 'var(--green)',
  deadline: '#dc2626',
  quiz: 'var(--teal)',
}

// 달력 점 표시용 날짜
const marked = computed(() => schedules.map((s) => s.day))

// 오늘이 속한 주(일~토) 범위
const weekRange = computed(() => {
  const start = new Date(today)
  start.setDate(today.getDate() - today.getDay())
  const end = new Date(start)
  end.setDate(start.getDate() + 6)
  return { start, end }
})

// 이번 주에 해당하는 일정 (현재 달 기준)
const weekSchedules = computed(() => {
  const { start, end } = weekRange.value
  return schedules
    .filter((s) => {
      const date = new Date(today.getFullYear(), today.getMonth(), s.day)
      return date >= new Date(start.toDateString()) &&
        date <= new Date(end.toDateString())
    })
    .sort((a, b) => a.day - b.day)
})

const monthLabel = computed(() => today.getMonth() + 1)

function dayLabel(day) {
  const date = new Date(today.getFullYear(), today.getMonth(), day)
  const w = ['일', '월', '화', '수', '목', '금', '토'][date.getDay()]
  return `${monthLabel.value}/${day}(${w})`
}

function move(step) {
  const c = new Date(cursor.value)
  c.setMonth(c.getMonth() + step)
  cursor.value = c
}
</script>

<template>
  <div class="widget">
    <div class="cal-head">
      <button @click="move(-1)">‹</button>
      <strong>{{ label }}</strong>
      <button @click="move(1)">›</button>
    </div>
    <div class="grid week">
      <span v-for="w in ['일','월','화','수','목','금','토']" :key="w">{{ w }}</span>
    </div>
    <div class="grid">
      <span
        v-for="(d, i) in days"
        :key="i"
        class="day"
        :class="{ today: d && isToday(d), mark: d && marked.includes(d) }"
      >
        {{ d || '' }}
      </span>
    </div>

    <!-- 이번 주 일정 -->
    <div class="schedule">
      <div class="sc-head">📌 이번 주 일정</div>
      <ul v-if="weekSchedules.length">
        <li v-for="s in weekSchedules" :key="s.day">
          <span class="dot" :style="{ background: typeColor[s.type] }"></span>
          <span class="sc-date">{{ dayLabel(s.day) }}</span>
          <span class="sc-title">{{ s.title }}</span>
        </li>
      </ul>
      <p v-else class="sc-empty">이번 주 등록된 일정이 없어요.</p>
    </div>
  </div>
</template>

<style scoped>
.widget {
  background: #fff;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 16px;
  box-shadow: var(--shadow);
}
.cal-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}
.cal-head strong {
  font-size: 0.95rem;
}
.cal-head button {
  background: transparent;
  font-size: 1.1rem;
  color: var(--text-sub);
  padding: 0 6px;
}
.grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  text-align: center;
}
.week span {
  font-size: 0.72rem;
  color: var(--text-mute);
  padding: 4px 0;
}
.day {
  font-size: 0.78rem;
  padding: 6px 0;
  position: relative;
  color: var(--text);
}
.day.today {
  background: var(--navy);
  color: #fff;
  border-radius: 999px;
}
.day.mark::after {
  content: '';
  position: absolute;
  bottom: 2px;
  left: 50%;
  transform: translateX(-50%);
  width: 4px;
  height: 4px;
  border-radius: 999px;
  background: var(--green);
}

/* 이번 주 일정 */
.schedule {
  margin-top: 14px;
  padding-top: 14px;
  border-top: 1px solid var(--line);
}
.sc-head {
  font-size: 0.84rem;
  font-weight: 700;
  margin-bottom: 10px;
}
.schedule ul {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 9px;
}
.schedule li {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 0.78rem;
}
.dot {
  width: 6px;
  height: 6px;
  border-radius: 999px;
  flex-shrink: 0;
}
.sc-date {
  color: var(--text-mute);
  font-weight: 600;
  white-space: nowrap;
}
.sc-title {
  color: var(--text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.sc-empty {
  font-size: 0.78rem;
  color: var(--text-mute);
  padding: 4px 0;
}
</style>
