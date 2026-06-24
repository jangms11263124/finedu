<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import api from '@/api'
import Pagination from '@/components/common/Pagination.vue'

const regions = [
  '지역 선택',
  '서울',
  '부산',
  '대구',
  '인천',
  '광주',
  '대전',
  '울산',
  '세종',
  '경기도',
  '강원도',
  '충청북도',
  '충청남도',
  '전라북도',
  '전라남도',
  '경상북도',
  '경상남도',
  '제주도',
  '온라인'
]
const onlines = [
  { key: '', label: '온/오프라인 선택' },
  { key: 'offline', label: '오프라인' },
  { key: 'online', label: '온라인' },
  { key: 'both', label: '온·오프라인' },
]

const items = ref([])
const count = ref(0)
const page = ref(1)
const totalPages = ref(1)
const loading = ref(true)

const appStatus = ref('')
const region = ref('지역 선택')
const online = ref('')

async function load() {
  loading.value = true
  try {
    const params = { page: page.value }
    if (appStatus.value) params.app_status = appStatus.value
    if (region.value && region.value !== '지역 선택') params.region = region.value
    if (online.value) params.online_type = online.value
    const { data } = await api.get('/events/', { params })
    items.value = data.results
    count.value = data.count
    totalPages.value = data.total_pages
  } finally {
    loading.value = false
  }
}

function search() {
  page.value = 1
  load()
}
function changePage(p) {
  page.value = p
  load()
  window.scrollTo({ top: 0, behavior: 'smooth' })
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

onMounted(load)
</script>

<template>
  <main class="events">
    <div class="container">
      <header class="head">
        <div>
          <h1>교육 행사 프로그램</h1>
          <p>다양한 금융·경제 교육 프로그램과 온·오프라인 행사 일정을 확인해 보세요.</p>
        </div>
        <div class="filters">
          <select v-model="appStatus" @change="search">
            <option value="">신청 상태</option>
            <option value="upcoming">신청 예정</option>
            <option value="ongoing">신청 중</option>
            <option value="closed">신청 마감</option>
          </select>
          <select v-model="region" @change="search">
            <option v-for="r in regions" :key="r" :value="r">{{ r }}</option>
          </select>
          <select v-model="online" @change="search">
            <option v-for="o in onlines" :key="o.key" :value="o.key">{{ o.label }}</option>
          </select>
          <button class="btn btn-navy" @click="search">조회</button>
        </div>
      </header>

      <p v-if="loading" class="empty">불러오는 중...</p>
      <p v-else-if="!items.length" class="empty">조건에 맞는 행사가 없습니다.</p>

      <div v-else class="grid">
        <RouterLink
          v-for="e in items"
          :key="e.id"
          :to="`/events/${e.id}`"
          class="card"
        >
          <div class="thumb">
            <span class="emoji">🎓</span>
            <div v-if="getEventStatus(e) === 'closed'" class="closed-overlay"></div>
            <span class="dday" :class="getEventStatus(e)">
              {{ ddayLabel(e) }}
            </span>
            <span class="tags">{{ e.region }} · {{ e.online_display }}</span>
          </div>
          <div class="body">
            <h3>{{ e.title }}</h3>
            <p class="period">
              접수기간 <span>{{ e.start_date }} ~ {{ e.end_date }}</span>
            </p>
          </div>
        </RouterLink>
      </div>

      <Pagination :page="page" :total-pages="totalPages" @change="changePage" />
    </div>
  </main>
</template>

<style scoped>
.events {
  padding: 34px 0 20px;
  min-height: 72vh;
}
.head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}
.head h1 {
  font-size: 1.7rem;
  font-weight: 800;
  letter-spacing: -0.6px;
}
.head p {
  margin-top: 8px;
  color: var(--text-sub);
  font-size: 0.92rem;
}
.filters {
  display: flex;
  gap: 8px;
}
.filters select {
  border: 1px solid var(--line);
  border-radius: 9px;
  padding: 10px 30px 10px 14px;
  font-size: 0.85rem;
  background: #fff;
  outline: none;
  appearance: none;
  -webkit-appearance: none;
  background-image: url("data:image/svg+xml;charset=utf-8,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3E%3Cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='m6 8 4 4 4-4'/%3E%3C/svg%3E");
  background-position: right 8px center;
  background-repeat: no-repeat;
  background-size: 16px;
  cursor: pointer;
  min-width: 110px;
  transition: border-color 0.15s ease;
}
.filters select:focus,
.filters select:hover {
  border-color: var(--navy);
}
.empty {
  text-align: center;
  color: var(--text-mute);
  padding: 60px 0;
}
.grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 18px;
}
.card {
  display: block;
  background: #fff;
  border: 1px solid var(--line);
  border-radius: 14px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.14s, box-shadow 0.14s;
}
.card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-hover);
}
.thumb {
  position: relative;
  aspect-ratio: 16 / 10;
  background: linear-gradient(135deg, #0b1f3a, #133a5e 60%, #0f766e);
  display: grid;
  place-items: center;
}
.emoji {
  font-size: 2.6rem;
  filter: drop-shadow(0 3px 8px rgba(0, 0, 0, 0.4));
  z-index: 2;
}
.dday {
  position: absolute;
  top: 10px;
  left: 10px;
  font-size: 0.74rem;
  font-weight: 800;
  color: #fff;
  padding: 4px 10px;
  border-radius: 7px;
  z-index: 2;
}
.dday.upcoming {
  background: #2563eb;
}
.dday.ongoing {
  background: #dc2626;
}
.dday.closed {
  background: #000;
}
.tags {
  position: absolute;
  bottom: 10px;
  left: 10px;
  font-size: 0.72rem;
  font-weight: 600;
  color: #fff;
  background: rgba(0, 0, 0, 0.4);
  padding: 3px 9px;
  border-radius: 999px;
  z-index: 2;
}
.closed-overlay {
  position: absolute;
  inset: 0;
  background: rgba(128, 128, 128, 0.35);
  z-index: 1;
  pointer-events: none;
}
.body {
  padding: 14px 16px 18px;
}
h3 {
  font-size: 0.98rem;
  font-weight: 700;
  line-height: 1.42;
  margin-bottom: 12px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 2.7em;
}
.period {
  font-size: 0.78rem;
  color: var(--text-mute);
}
.period span {
  color: var(--text-sub);
  font-weight: 600;
}
@media (max-width: 900px) {
  .grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
@media (max-width: 560px) {
  .grid {
    grid-template-columns: 1fr;
  }
}
</style>
