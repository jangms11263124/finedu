<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api'
import Pagination from '@/components/common/Pagination.vue'

const route = useRoute()

const subjects = [
  { key: '', label: '주제별 전체' },
  { key: 'economy', label: '경제' },
  { key: 'management', label: '경영' },
  { key: 'finance', label: '금융' },
  { key: 'society', label: '사회' },
  { key: 'science', label: '과학' },
]
const consonants = 'ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅊㅋㅌㅍㅎ'.split('')
const alphabets1 = '0-9ABCDEFGHIJKLMN'.match(/0-9|[A-Z]/g)
const alphabets2 = 'OPQRSTUVWXYZ'.match(/[A-Z]/g)

const items = ref([])
const count = ref(0)
const page = ref(1)
const totalPages = ref(1)
const loading = ref(true)
const usedInitials = ref([])

const subject = ref('')
const initial = ref('')
const keyword = ref('')

// 용어 뜻 팝업
const selected = ref(null)
function openTerm(t) {
  selected.value = t
}
function closeTerm() {
  selected.value = null
}


const subjectClass = {
  경제: 'economy', 경영: 'management', 금융: 'finance',
  사회: 'society', 과학: 'science', 기타: 'etc',
}

async function load() {
  loading.value = true
  try {
    const params = { page: page.value }
    if (subject.value) params.subject = subject.value
    if (initial.value) params.initial = initial.value
    if (keyword.value.trim()) params.q = keyword.value.trim()
    const { data } = await api.get('/terms/', { params })
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
function pickInitial(c) {
  initial.value = initial.value === c ? '' : c
  search()
}
function changePage(p) {
  page.value = p
  load()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// 사이드바 등에서 ?term= 으로 들어오면 목록을 필터한다.
// 결과가 1개뿐이면(딱 떨어지는 검색) 바로 뜻 팝업, 여러 개면 목록만 보여준다.
async function handleTermQuery(q) {
  if (!q) return
  keyword.value = q
  page.value = 1
  await load()
  const exact = items.value.find(
    (t) => t.term.toLowerCase() === q.trim().toLowerCase()
  )
  if (exact) {
    openTerm(exact)
  } else if (count.value === 1) {
    openTerm(items.value[0])
  }
}

watch(
  () => route.query.term,
  (q) => handleTermQuery(q)
)

onMounted(async () => {
  try {
    const res = await api.get('/terms/initials/')
    usedInitials.value = res.data
  } catch (err) {
    console.error('Failed to fetch initials:', err)
  }

  const q = route.query.term
  if (q) {
    await handleTermQuery(q)
  } else {
    await load()
  }
})
</script>

<template>
  <main class="glossary">
    <div class="container">
      <header class="head">
        <h1>경제 용어 사전</h1>
        <p>어려운 경제 용어도 쉽게 찾아보고 이해하세요.</p>
      </header>

      <div class="finder">
        <div class="row">
          <span class="label">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" class="label-icon"><path stroke-linecap="round" stroke-linejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.637 10.637Z" /></svg>
            검색어로 찾기
          </span>
          <select v-model="subject" class="subject-select" @change="search">
            <option v-for="s in subjects" :key="s.key" :value="s.key">{{ s.label }}</option>
          </select>
          <input v-model="keyword" placeholder="검색어를 입력하세요" @keyup.enter="search" />
          <button class="btn btn-navy search-btn" @click="search">검색</button>
        </div>
        <div class="row initials">
          <span class="label">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" class="label-icon"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6.042A8.967 8.967 0 0 0 6 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 0 1 6 18c2.305 0 4.408.867 6 2.292m0-16.25a8.966 8.966 0 0 1 6-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0 0 18 18a8.967 8.967 0 0 0-6 2.292m0-16.25v16.25" /></svg>
            두문자로 찾기
          </span>
          <div class="chips-group">
            <div class="chips">
              <button :class="{ on: initial === '', wide: true }" @click="pickInitial('')">전체</button>
              <button
                v-for="c in consonants"
                :key="c"
                :class="{ on: initial === c, disabled: !usedInitials.includes(c) }"
                :disabled="!usedInitials.includes(c)"
                @click="pickInitial(c)"
              >{{ c }}</button>
            </div>
            <div class="chips">
              <button
                v-for="a in alphabets1"
                :key="a"
                :class="{ on: initial === a, wide: a === '0-9', disabled: !usedInitials.includes(a) }"
                :disabled="!usedInitials.includes(a)"
                @click="pickInitial(a)"
              >{{ a }}</button>
            </div>
            <div class="chips">
              <button
                v-for="a in alphabets2"
                :key="a"
                :class="{ on: initial === a, disabled: !usedInitials.includes(a) }"
                :disabled="!usedInitials.includes(a)"
                @click="pickInitial(a)"
              >{{ a }}</button>
            </div>
          </div>
        </div>
      </div>

      <p class="count"><strong>{{ count }}</strong>개 용어</p>

      <!-- 표 -->
      <div class="table">
        <div class="thead">
          <span class="t-no">NO</span>
          <span class="t-sub">주제</span>
          <span class="t-term">용어</span>
          <span class="t-desc">설명</span>
        </div>
        <p v-if="loading" class="empty">불러오는 중...</p>
        <p v-else-if="!items.length" class="empty">검색 결과가 없습니다.</p>
        <div
          v-for="(t, i) in items"
          v-else
          :key="t.id"
          class="trow"
          @click="openTerm(t)"
        >
          <span class="t-no">{{ (page - 1) * 12 + i + 1 }}</span>
          <span class="t-sub">
            {{ t.subject_display }}
          </span>
          <span class="t-term">{{ t.term }}</span>
          <span class="t-desc">{{ t.description }}</span>
        </div>
      </div>

      <Pagination :page="page" :total-pages="totalPages" @change="changePage" />
    </div>

    <!-- 용어 뜻 팝업 -->
    <div v-if="selected" class="modal-backdrop" @click.self="closeTerm">
      <div class="modal">
        <button class="close" @click="closeTerm" aria-label="닫기">✕</button>
        <span class="m-sub">
          {{ selected.subject_display }}
        </span>
        <h2 class="m-term">{{ selected.term }}</h2>
        <p class="m-desc">{{ selected.description }}</p>
      </div>
    </div>
  </main>
</template>

<style scoped>
.glossary {
  padding: 34px 0 20px;
  min-height: 72vh;
}
.head {
  margin-bottom: 22px;
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
.finder {
  background: #fff;
  border: 1px solid var(--line);
  border-radius: 16px;
  box-shadow: var(--shadow);
  overflow: hidden;
  transition: box-shadow 0.3s ease;
}
.finder:hover {
  box-shadow: var(--shadow-hover);
}
.row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  border-bottom: 1px solid var(--line);
}
.row:last-child {
  border-bottom: none;
}
.label {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
  width: 160px;
  font-size: 0.86rem;
  font-weight: 700;
  color: var(--text);
}
.label-icon {
  width: 16px;
  height: 16px;
  stroke: var(--navy);
}
.row select {
  height: 40px;
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 0 30px 0 12px;
  font-size: 0.85rem;
  outline: none;
  background: #fff;
  appearance: none;
  -webkit-appearance: none;
  background-image: url("data:image/svg+xml;charset=utf-8,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3E%3Cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='m6 8 4 4 4-4'/%3E%3C/svg%3E");
  background-position: right 8px center;
  background-repeat: no-repeat;
  background-size: 16px;
  cursor: pointer;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}
.subject-select {
  width: 120px;
  flex-shrink: 0;
}
.row input {
  flex: 1;
  height: 40px;
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 0 12px;
  font-size: 0.85rem;
  outline: none;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}
.row select:hover,
.row input:hover {
  border-color: var(--navy-dark);
}
.row select:focus,
.row input:focus {
  border-color: var(--navy);
  box-shadow: 0 0 0 3px rgba(27, 42, 89, 0.1);
}
.row .btn {
  height: 40px;
  padding: 0 20px;
  font-size: 0.88rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}
.search-btn {
  width: 80px;
  padding: 0 !important;
  flex-shrink: 0;
}
.row .btn:hover {
  background: var(--navy-dark);
  box-shadow: 0 4px 12px rgba(27, 42, 89, 0.15);
}
.row.initials {
  align-items: flex-start;
  padding: 14px 20px;
}
.row.initials .label {
  margin-top: 6px;
}
.chips-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
}
.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  max-width: 800px;
}
.chips button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  padding: 0;
  border-radius: 8px;
  border: 1px solid var(--line);
  background: #fff;
  font-size: 0.86rem;
  font-weight: 600;
  color: var(--text-sub);
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}
.chips button.wide {
  width: auto;
  min-width: 48px;
  padding: 0 10px;
}
.chips button:hover {
  border-color: var(--navy);
  color: var(--navy);
  background: #f8fafc;
  transform: translateY(-1px);
}
.chips button.on {
  background: linear-gradient(135deg, var(--navy), #253366);
  border-color: var(--navy);
  color: #fff;
  transform: translateY(-1px);
  box-shadow: 0 4px 10px rgba(27, 42, 89, 0.2);
  font-weight: 700;
}
.chips button:disabled,
.chips button.disabled {
  background: #f8fafc;
  color: var(--text-mute);
  border-color: var(--line);
  cursor: not-allowed;
  opacity: 0.55;
  transform: none !important;
  box-shadow: none !important;
  pointer-events: none;
}
.count {
  margin: 18px 0 10px;
  font-size: 0.88rem;
  color: var(--text-sub);
}
.count strong {
  color: var(--navy);
}
.table {
  background: #fff;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  overflow: hidden;
}
.thead,
.trow {
  display: grid;
  grid-template-columns: 60px 100px 200px 1fr;
  align-items: center;
  gap: 10px;
  padding: 13px 18px;
}
.thead {
  background: #f1f3f9;
  color: var(--text);
  font-size: 0.8rem;
  font-weight: 700;
  border-bottom: 2px solid var(--line);
}
.thead span {
  color: var(--text);
  font-weight: 700;
  text-align: center;
}
.thead .t-term,
.thead .t-desc {
  text-align: left;
}
.trow {
  border-bottom: 1px solid var(--line);
  font-size: 0.88rem;
  cursor: pointer;
  transition: background 0.15s ease;
}
.trow:last-child {
  border-bottom: none;
}
.trow:hover {
  background: var(--bg);
}
.t-no {
  color: var(--text-mute);
  text-align: center;
  font-size: 0.8rem;
}
.t-sub {
  color: var(--text-sub);
  font-weight: 600;
  text-align: center;
  font-size: 0.8rem;
}
.t-term {
  font-weight: 700;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.t-desc {
  color: var(--text-sub);
  line-height: 1.5;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.empty {
  text-align: center;
  color: var(--text-mute);
  padding: 50px 0;
}

/* 용어 뜻 팝업 */
.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 100;
  background: rgba(20, 28, 50, 0.45);
  display: grid;
  place-items: center;
  padding: 20px;
  animation: fade 0.15s ease;
}
.modal {
  position: relative;
  width: 100%;
  max-width: 440px;
  background: #fff;
  border-radius: 18px;
  padding: 32px 30px 30px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.25);
  animation: pop 0.18s ease;
}
.close {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 30px;
  height: 30px;
  border-radius: 999px;
  background: var(--bg);
  color: var(--text-sub);
  font-size: 0.85rem;
}
.close:hover {
  background: #e5e7f0;
}
.m-sub {
  font-size: 0.84rem;
  color: var(--teal);
  font-weight: 700;
}
.m-term {
  font-size: 1.5rem;
  font-weight: 800;
  letter-spacing: -0.5px;
  margin: 14px 0 12px;
}
.m-desc {
  font-size: 0.95rem;
  line-height: 1.7;
  color: var(--text-sub);
}
@keyframes fade {
  from { opacity: 0; }
}
@keyframes pop {
  from { opacity: 0; transform: translateY(10px) scale(0.97); }
}

@media (max-width: 720px) {
  .thead,
  .trow {
    grid-template-columns: 36px 64px 1fr;
  }
  .t-desc {
    display: none;
  }
}

@media (max-width: 576px) {
  .label {
    width: 100%;
    margin-bottom: 8px;
  }
  .row {
    flex-wrap: wrap;
    gap: 8px;
  }
  .subject-select {
    width: 100%;
  }
  .row input {
    width: 100%;
    flex: none;
  }
  .search-btn {
    width: 100%;
  }
}
</style>
