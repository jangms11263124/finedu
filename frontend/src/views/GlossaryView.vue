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
const alphabets = '0-9ABCDEFGHIJKLMNOPQRSTUVWXYZ'.match(/0-9|[A-Z]/g)

const items = ref([])
const count = ref(0)
const page = ref(1)
const totalPages = ref(1)
const loading = ref(true)

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

      <!-- 검색 박스 -->
      <div class="finder">
        <div class="row">
          <span class="label">🔍 검색어로 찾기</span>
          <select v-model="subject" @change="search">
            <option v-for="s in subjects" :key="s.key" :value="s.key">{{ s.label }}</option>
          </select>
          <input v-model="keyword" placeholder="검색어를 입력하세요" @keyup.enter="search" />
          <button class="btn btn-navy" @click="search">검색</button>
        </div>
        <div class="row initials">
          <span class="label">🔠 두문자로 찾기</span>
          <div class="chips">
            <button :class="{ on: initial === '' }" @click="pickInitial('')">전체</button>
            <button
              v-for="c in consonants"
              :key="c"
              :class="{ on: initial === c }"
              @click="pickInitial(c)"
            >{{ c }}</button>
          </div>
        </div>
        <div class="row initials alpha">
          <span class="label"></span>
          <div class="chips">
            <button
              v-for="a in alphabets"
              :key="a"
              :class="{ on: initial === a }"
              @click="pickInitial(a)"
            >{{ a }}</button>
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
            <em :class="subjectClass[t.subject_display]">{{ t.subject_display }}</em>
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
        <em class="m-sub" :class="subjectClass[selected.subject_display]">
          {{ selected.subject_display }}
        </em>
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
  border-radius: 12px;
  box-shadow: var(--shadow);
  overflow: hidden;
}
.row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 18px;
  border-bottom: 1px solid var(--line);
}
.row:last-child {
  border-bottom: none;
}
.label {
  flex-shrink: 0;
  width: 120px;
  font-size: 0.86rem;
  font-weight: 700;
  color: var(--text);
}
.row select {
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 9px 12px;
  font-size: 0.85rem;
  background: var(--bg);
  outline: none;
}
.row input {
  flex: 1;
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 9px 12px;
  font-size: 0.85rem;
  outline: none;
}
.row input:focus {
  border-color: var(--navy);
}
.initials.alpha {
  padding-top: 0;
}
.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}
.chips button {
  min-width: 30px;
  height: 30px;
  border-radius: 7px;
  border: 1px solid transparent;
  background: transparent;
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--text-sub);
}
.chips button:hover {
  background: var(--bg);
}
.chips button.on {
  background: var(--navy);
  color: #fff;
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
  border-radius: 12px;
  overflow: hidden;
}
.thead,
.trow {
  display: grid;
  grid-template-columns: 50px 80px 180px 1fr;
  align-items: center;
  gap: 14px;
  padding: 14px 20px;
}
.thead {
  background: #2b3654;
  color: #fff;
  font-size: 0.84rem;
  font-weight: 700;
}
.trow {
  border-top: 1px solid var(--line);
  font-size: 0.86rem;
  cursor: pointer;
}
.trow:hover {
  background: var(--bg);
}
.t-no {
  color: var(--text-mute);
  text-align: center;
}
.t-sub em {
  font-style: normal;
  font-size: 0.74rem;
  font-weight: 700;
  padding: 3px 9px;
  border-radius: 999px;
  background: var(--bg);
  color: var(--text-sub);
}
.t-sub em.economy { background: #e0f2fe; color: #0369a1; }
.t-sub em.management { background: #ede9fe; color: #6d28d9; }
.t-sub em.finance { background: #dcfce7; color: #15803d; }
.t-sub em.society { background: #fef3c7; color: #b45309; }
.t-sub em.science { background: #fee2e2; color: #b91c1c; }
.t-term {
  font-weight: 700;
}
.t-desc {
  color: var(--text-sub);
  line-height: 1.5;
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
  font-style: normal;
  font-size: 0.76rem;
  font-weight: 700;
  padding: 4px 11px;
  border-radius: 999px;
  background: var(--bg);
  color: var(--text-sub);
}
.m-sub.economy { background: #e0f2fe; color: #0369a1; }
.m-sub.management { background: #ede9fe; color: #6d28d9; }
.m-sub.finance { background: #dcfce7; color: #15803d; }
.m-sub.society { background: #fef3c7; color: #b45309; }
.m-sub.science { background: #fee2e2; color: #b91c1c; }
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
  .label {
    width: 100%;
    margin-bottom: 6px;
  }
  .row {
    flex-wrap: wrap;
  }
  .thead,
  .trow {
    grid-template-columns: 36px 64px 1fr;
  }
  .t-desc {
    display: none;
  }
}
</style>
