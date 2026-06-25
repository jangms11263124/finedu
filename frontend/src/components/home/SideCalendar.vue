<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import api from '@/api'

const cursor = ref(new Date())
const today = new Date()
const events = ref([])
const loading = ref(false)
const selectedDate = ref(null)

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

// 날짜 포맷팅 함수들
function formatDate(date) {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

function formatDateYMD(y, m, d) {
  return `${y}-${String(m + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`
}

async function fetchEvents() {
  loading.value = true
  try {
    const { data } = await api.get('/events/')
    events.value = Array.isArray(data) ? data : (data.results || [])
  } catch (e) {
    console.error('교육 행사 API 조회 실패:', e)
  } finally {
    loading.value = false
  }
}

function isToday(d) {
  return (
    d === today.getDate() &&
    cursor.value.getMonth() === today.getMonth() &&
    cursor.value.getFullYear() === today.getFullYear()
  )
}

function hasEventStart(d) {
  if (!d) return false
  const dateStr = formatDateYMD(cursor.value.getFullYear(), cursor.value.getMonth(), d)
  return events.value.some((e) => e.start_date === dateStr)
}

function hasEventEnd(d) {
  if (!d) return false
  const dateStr = formatDateYMD(cursor.value.getFullYear(), cursor.value.getMonth(), d)
  return events.value.some((e) => e.end_date === dateStr)
}

// 오늘이 속한 주(일~토) 범위
const weekRange = computed(() => {
  const start = new Date(today)
  start.setDate(today.getDate() - today.getDay())
  const end = new Date(start)
  end.setDate(start.getDate() + 6)
  return { start, end }
})

// 이번 주에 해당하는 교육 행사 (접수 기간 기준)
const weekEvents = computed(() => {
  const { start, end } = weekRange.value
  const startStr = formatDate(start)
  const endStr = formatDate(end)

  return events.value
    .filter((e) => {
      if (!e.start_date || !e.end_date) return false
      return e.start_date <= endStr && e.end_date >= startStr
    })
    .sort((a, b) => {
      if (a.end_date !== b.end_date) {
        return a.end_date.localeCompare(b.end_date)
      }
      return a.start_date.localeCompare(b.start_date)
    })
})

// 특정 날짜 선택 로직
function selectDate(d) {
  if (!d) return
  const target = new Date(cursor.value.getFullYear(), cursor.value.getMonth(), d)
  if (selectedDate.value && formatDate(selectedDate.value) === formatDate(target)) {
    selectedDate.value = null
  } else {
    selectedDate.value = target
  }
}

// 선택된 날짜 여부
function isSelected(d) {
  if (!d || !selectedDate.value) return false
  return (
    d === selectedDate.value.getDate() &&
    cursor.value.getMonth() === selectedDate.value.getMonth() &&
    cursor.value.getFullYear() === selectedDate.value.getFullYear()
  )
}

// 선택된 날짜에 진행 중인 교육 행사
const selectedDateEvents = computed(() => {
  if (!selectedDate.value) return []
  const dateStr = formatDate(selectedDate.value)
  return events.value.filter((e) => {
    if (!e.start_date || !e.end_date) return false
    return e.start_date <= dateStr && e.end_date >= dateStr
  })
})

// 하단 리스트에 뿌릴 최종 행사 리스트
const displayEvents = computed(() => {
  return selectedDate.value ? selectedDateEvents.value : weekEvents.value
})

// 리스트 타이틀
const listTitle = computed(() => {
  if (selectedDate.value) {
    const m = selectedDate.value.getMonth() + 1
    const d = selectedDate.value.getDate()
    return `${m}월 ${d}일 프로그램`
  }
  return `이번 주 행사 프로그램`
})

function resetSelection() {
  selectedDate.value = null
}

function getEventStatus(e) {
  const d = new Date()
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const todayStr = `${year}-${month}-${day}`

  if (e.start_date && e.start_date > todayStr) {
    return 'upcoming'
  }
  if (e.d_day === null || e.status === 'closed' || e.status === 'ended') {
    return 'closed'
  }
  return 'ongoing'
}

function ddayLabel(e) {
  const status = getEventStatus(e)
  if (status === 'upcoming') return '예정'
  if (status === 'closed') return '마감'
  return e.d_day === 0 ? 'D-DAY' : `D-${e.d_day}`
}

function move(step) {
  const c = new Date(cursor.value)
  c.setMonth(c.getMonth() + step)
  cursor.value = c
}

onMounted(() => {
  fetchEvents()
})
</script>

<template>
  <div class="widget">
    <!-- 달력 헤더 -->
    <div class="cal-head">
      <button @click="move(-1)">‹</button>
      <strong>{{ label }}</strong>
      <button @click="move(1)">›</button>
    </div>

    <!-- 범례(Legend) -->
    <div class="cal-legend">
      <span class="legend-item"><span class="dot-start-sample"></span>접수시작</span>
      <span class="legend-item"><span class="dot-end-sample"></span>접수마감</span>
    </div>

    <!-- 요일 그리드 -->
    <div class="grid week">
      <span v-for="w in ['일','월','화','수','목','금','토']" :key="w">{{ w }}</span>
    </div>

    <!-- 날짜 그리드 -->
    <div class="grid">
      <span
        v-for="(d, i) in days"
        :key="i"
        class="day"
        :class="{
          disabled: !d,
          today: d && isToday(d),
          selected: d && isSelected(d),
        }"
        @click="selectDate(d)"
      >
        {{ d || '' }}
        <!-- 세련된 시작일/마감일 도트 표시 -->
        <div v-if="d && (hasEventStart(d) || hasEventEnd(d))" class="dots">
          <span v-if="hasEventStart(d)" class="dot-start"></span>
          <span v-if="hasEventEnd(d)" class="dot-end"></span>
        </div>
      </span>
    </div>

    <!-- 하단 일정 목록 -->
    <div class="schedule">
      <div class="sc-head-wrap">
        <span class="sc-head">
          <svg class="sc-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
            <line x1="16" y1="2" x2="16" y2="6"></line>
            <line x1="8" y1="2" x2="8" y2="6"></line>
            <line x1="3" y1="10" x2="21" y2="10"></line>
          </svg>
          {{ listTitle }}
        </span>
        <button
          v-if="selectedDate"
          class="sc-reset-btn"
          @click="resetSelection"
        >
          이번 주 보기
        </button>
      </div>

      <div v-if="loading" class="sc-empty">행사 정보를 불러오는 중...</div>
      
      <ul v-else-if="displayEvents.length">
        <li v-for="s in displayEvents.slice(0, 5)" :key="s.id">
          <RouterLink :to="`/events/${s.id}`" class="sc-link">
            <span class="sc-badge" :class="getEventStatus(s)">
              {{ ddayLabel(s) }}
            </span>
            <span class="sc-title" :title="s.title">{{ s.title }}</span>
          </RouterLink>
        </li>
      </ul>
      <p v-else class="sc-empty">등록된 행사 일정이 없어요.</p>
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
.cal-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}
.cal-head strong {
  font-size: 1rem;
  font-weight: 800;
  color: var(--navy);
  letter-spacing: -0.3px;
}
.cal-head button {
  background: transparent;
  font-size: 1.25rem;
  color: var(--text-sub);
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background 0.15s, color 0.15s;
}
.cal-head button:hover {
  background: var(--bg);
  color: var(--navy);
}
.cal-legend {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-bottom: 10px;
  padding-right: 4px;
}
.legend-item {
  font-size: 0.68rem;
  color: var(--text-sub);
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-weight: 600;
}
.dot-start-sample {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--teal);
}
.dot-end-sample {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #ef4444;
}
.grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  text-align: center;
  row-gap: 4px;
}
.week span {
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--text-mute);
  padding: 6px 0;
}
.week span:first-child {
  color: #ef4444; /* 일요일 빨간색 */
}
.week span:last-child {
  color: #3b82f6; /* 토요일 파란색 */
}
.day {
  font-size: 0.78rem;
  font-weight: 500;
  aspect-ratio: 1 / 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  color: var(--text);
  border-radius: 50%;
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
  user-select: none;
}
.day.disabled {
  cursor: default;
  pointer-events: none;
}
.day:hover:not(.disabled):not(.today):not(.selected) {
  background: var(--bg);
}
.day.today {
  background: var(--navy);
  color: #fff;
  font-weight: 800;
}
.day.selected {
  background: rgba(27, 42, 89, 0.08);
  border: 1px solid var(--navy);
  color: var(--navy);
  font-weight: 700;
}

/* 닷(도트) 마크 표시 */
.dots {
  position: absolute;
  bottom: 4px;
  display: flex;
  gap: 3px;
  justify-content: center;
}
.dot-start, .dot-end {
  width: 4px;
  height: 4px;
  border-radius: 50%;
}
.dot-start {
  background: var(--teal);
}
.dot-end {
  background: #ef4444;
}

/* 활성화 날짜(오늘, 선택일)일 때는 가시성을 위해 도트 색 조정 */
.day.today .dot-start {
  background: #5eead4;
}
.day.today .dot-end {
  background: #ef4444;
}

/* 이번 주 일정 */
.schedule {
  margin-top: 16px;
  padding-top: 14px;
  border-top: 1px solid var(--line);
}
.sc-head-wrap {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
  min-height: 24px;
}
.sc-head {
  font-size: 0.84rem;
  font-weight: 800;
  color: var(--text);
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.sc-icon {
  width: 14px;
  height: 14px;
  color: var(--navy);
  flex-shrink: 0;
}
.sc-reset-btn {
  font-size: 0.72rem;
  color: var(--navy);
  background: none;
  font-weight: 700;
  cursor: pointer;
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid var(--navy);
  transition: background 0.15s, color 0.15s;
}
.sc-reset-btn:hover {
  background: var(--navy);
  color: #fff;
}
.schedule ul {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.sc-link {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  border-radius: var(--radius-sm);
  transition: background 0.15s;
}
.sc-link:hover {
  background: var(--bg);
}
.sc-badge {
  font-size: 0.64rem;
  font-weight: 800;
  padding: 2px 6px;
  border-radius: 5px;
  white-space: nowrap;
}
.sc-badge.upcoming {
  background: #e0f2fe;
  color: #0369a1;
}
.sc-badge.ongoing {
  background: #fee2e2;
  color: #b91c1c;
}
.sc-badge.closed {
  background: #f3f4f6;
  color: #4b5563;
}
.sc-title {
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.sc-empty {
  font-size: 0.78rem;
  color: var(--text-mute);
  text-align: center;
  padding: 16px 0;
}
</style>
