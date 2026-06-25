<script setup>
import { nextTick, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import api from '@/api'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const route = useRoute()

/* ── 탭 ───────────────────────────────── */
const tabs = [
  { key: 'posts', label: '내가 쓴 글' },
  { key: 'liked-posts', label: '좋아요한 글' },
  { key: 'liked-contents', label: '좋아요한 콘텐츠' },
  { key: 'scrap', label: '스크랩' },
]
const activeTab = ref('posts')
const tabsEl = ref(null)

// 스크랩 탭 내부 토글 (콘텐츠 / 교육행사 분리)
const scrapKind = ref('contents')

// 활동 현황 카드 클릭 → 해당 탭으로 전환하고 목록 위치로 스크롤
function goTab(key) {
  activeTab.value = key
  loadTab(key)
  nextTick(() => tabsEl.value?.scrollIntoView({ behavior: 'smooth', block: 'start' }))
}

const myPosts = ref([])
const likedPosts = ref([])
const likedContents = ref([])
const scrapContents = ref([])
const scrapEvents = ref([])
const loading = ref(false)
const loaded = ref({})

async function loadTab(tab) {
  if (loaded.value[tab]) return
  loading.value = true
  try {
    if (tab === 'posts') {
      const { data } = await api.get('/posts/', { params: { author: 'me' } })
      myPosts.value = data
    } else if (tab === 'liked-posts') {
      const { data } = await api.get('/posts/', { params: { liked: 'me' } })
      likedPosts.value = data
    } else if (tab === 'liked-contents') {
      const { data } = await api.get('/contents/', { params: { liked: 'me' } })
      likedContents.value = data
    } else if (tab === 'scrap') {
      // 스크랩한 콘텐츠 · 교육행사를 함께 불러온다
      const [c, e] = await Promise.all([
        api.get('/contents/', { params: { scrapped: 'me' } }),
        api.get('/events/', { params: { scrapped: 'me' } }),
      ])
      scrapContents.value = c.data
      scrapEvents.value = e.data
    }
    loaded.value[tab] = true
  } finally {
    loading.value = false
  }
}

const ddayLabel = (e) =>
  e.d_day === null ? '접수마감' : e.d_day === 0 ? 'D-DAY' : `D-${e.d_day}`

watch(activeTab, (t) => loadTab(t), { immediate: false })

/* ── 프로필 수정 ───────────────────────── */
const editing = ref(false)
const form = ref({ nickname: '', email: '' })
const imageFile = ref(null)
const imagePreview = ref('')
const saving = ref(false)
const saveError = ref('')

function startEdit() {
  form.value = {
    nickname: auth.user?.nickname || '',
    email: auth.user?.email || '',
    password: '',
    password2: '',
  }
  imageFile.value = null
  imagePreview.value = ''
  saveError.value = ''
  editing.value = true
}

function onFile(e) {
  const file = e.target.files?.[0]
  if (!file) return
  imageFile.value = file
  imagePreview.value = URL.createObjectURL(file)
}

async function save() {
  saving.value = true
  saveError.value = ''

  // 비밀번호 입력 매칭 검사
  if (form.value.password || form.value.password2) {
    if (form.value.password !== form.value.password2) {
      saveError.value = '새 비밀번호가 일치하지 않습니다.'
      saving.value = false
      return
    }
  }

  try {
    let payload
    if (imageFile.value) {
      payload = new FormData()
      payload.append('nickname', form.value.nickname)
      payload.append('email', form.value.email)
      payload.append('profile_image', imageFile.value)
      if (form.value.password) {
        payload.append('password', form.value.password)
        payload.append('password2', form.value.password2)
      }
    } else {
      payload = { nickname: form.value.nickname, email: form.value.email }
      if (form.value.password) {
        payload.password = form.value.password
        payload.password2 = form.value.password2
      }
    }
    await auth.updateProfile(payload)
    editing.value = false
  } catch (err) {
    saveError.value =
      err.response?.data?.password?.[0] ||
      err.response?.data?.password2?.[0] ||
      err.response?.data?.nickname?.[0] ||
      err.response?.data?.email?.[0] ||
      '저장에 실패했어요. 다시 시도해주세요.'
  } finally {
    saving.value = false
  }
}

/* ── 표시용 계산값 ─────────────────────── */
const getDisplayScore = (score) => {
  if (score > 20) {
    return Math.round((score - 6) / 24 * 20)
  }
  return score
}

function fmt(dt) {
  return new Date(dt).toLocaleDateString('ko-KR', {
    year: '2-digit',
    month: '2-digit',
    day: '2-digit',
  })
}

onMounted(() => {
  // 통계 카드용 최신 카운트 확보 (직접 진입 등으로 비어 있을 수 있어 한 번 더 갱신)
  auth.fetchMe()
  // 홈 사이드바 "스크랩" 등에서 ?tab=... 으로 진입하면 해당 탭을 연다
  const initial = tabs.some((t) => t.key === route.query.tab)
    ? route.query.tab
    : 'posts'
  activeTab.value = initial
  loadTab(initial)
})

// URL 쿼리 변화 실시간 감지
watch(
  () => route.query.tab,
  (newTab) => {
    if (newTab && tabs.some(t => t.key === newTab)) {
      activeTab.value = newTab
      loadTab(newTab)
    }
  }
)

watch(
  () => route.query.edit,
  (newEdit) => {
    if (newEdit === 'true') {
      startEdit()
    } else {
      editing.value = false
    }
  }
)
</script>

<template>
  <main class="mypage">
    <div class="container">
      <!-- 프로필 헤더 -->
      <section class="profile-card">
        <div class="avatar-lg">
          <img v-if="auth.user?.profile_image" :src="auth.user.profile_image" alt="" />
          <span v-else>{{ (auth.user?.nickname || 'U').charAt(0) }}</span>
        </div>

        <div class="info">
          <div class="name-row">
            <h1>{{ auth.user?.nickname }}</h1>
            <span v-if="auth.user?.attendance_streak" class="streak-badge">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" class="inline-icon flame-icon"><path stroke-linecap="round" stroke-linejoin="round" d="M15.362 5.214A8.252 8.252 0 0 1 12 21 8.25 8.25 0 0 1 6.038 7.047 8.287 8.287 0 0 0 9 9.601a8.983 8.983 0 0 1 3.361-6.867 8.21 8.21 0 0 0 3 2.48Z" /><path stroke-linecap="round" stroke-linejoin="round" d="M12 18a3.75 3.75 0 0 0 .495-7.467 5.99 5.99 0 0 0-1.925 3.546 5.974 5.974 0 0 1-2.133-1A3.75 3.75 0 0 0 12 18Z" /></svg>
              연속 출석 {{ auth.user.attendance_streak }}일
            </span>
          </div>
          <p class="sub">@{{ auth.user?.username }}</p>
          <p class="sub email" v-if="auth.user?.email">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" class="inline-icon email-icon"><path stroke-linecap="round" stroke-linejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 0 1-2.25 2.25h-15a2.25 2.25 0 0 1-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0 0 19.5 4.5h-15a2.25 2.25 0 0 0-2.25 2.25m19.5 0v.243a2.25 2.25 0 0 1-1.07 1.916l-7.5 4.615a2.25 2.25 0 0 1-2.36 0L3.32 8.91a2.25 2.25 0 0 1-1.07-1.916V6.75" /></svg>
            {{ auth.user.email }}
          </p>
        </div>

        <button class="btn btn-outline edit-btn" @click="startEdit">프로필 수정</button>
      </section>

      <!-- 나의 활동 현황 -->
      <h2 class="section-title">나의 활동 현황</h2>
      <section class="stats">
        <button class="stat" @click="goTab('posts')">
          <span class="stat-ico ico-post">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" class="stat-svg post-color"><path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" /></svg>
          </span>
          <div class="stat-body">
            <strong>{{ auth.user?.post_count ?? 0 }}</strong>
            <span>작성 글</span>
          </div>
        </button>
        <button class="stat" @click="goTab('liked-posts')">
          <span class="stat-ico ico-like">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" class="stat-svg like-color"><path stroke-linecap="round" stroke-linejoin="round" d="M6.633 10.25c.806 0 1.533-.446 2.031-1.08a9.041 9.041 0 0 1 2.861-2.4c.723-.384 1.35-.956 1.653-1.715a4.498 4.498 0 0 0 .322-1.672V2.75a.75.75 0 0 1 .75-.75 2.25 2.25 0 0 1 2.25 2.25c0 1.152-.26 2.243-.723 3.218-.266.558.107 1.282.725 1.282m0 0h3.126c1.026 0 1.945.694 2.054 1.715.045.422.068.85.068 1.285a11.95 11.95 0 0 1-2.649 7.521c-.388.482-.987.729-1.602.729H13.48c-.408 0-.812-.1-1.185-.292a10.14 10.14 0 0 1-1.664-1.04l-.083-.066a9.753 9.753 0 0 0-2.285-1.242c-.227-.086-.467-.13-.709-.13H1.5v-7.375h5.133Z" /></svg>
          </span>
          <div class="stat-body">
            <strong>{{ auth.user?.liked_post_count ?? 0 }}</strong>
            <span>좋아요한 글</span>
          </div>
        </button>
        <button class="stat" @click="goTab('liked-contents')">
          <span class="stat-ico ico-content">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" class="stat-svg content-color"><path stroke-linecap="round" stroke-linejoin="round" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12Z" /></svg>
          </span>
          <div class="stat-body">
            <strong>{{ auth.user?.liked_content_count ?? 0 }}</strong>
            <span>좋아요한 콘텐츠</span>
          </div>
        </button>
        <button class="stat" @click="goTab('scrap')">
          <span class="stat-ico ico-scrap">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" class="stat-svg scrap-color"><path stroke-linecap="round" stroke-linejoin="round" d="M17.593 3.322c1.1.128 1.907 1.077 1.907 2.185V21L12 17.25 4.5 21V5.507c0-1.108.806-2.057 1.907-2.185a48.507 48.507 0 0 1 11.186 0Z" /></svg>
          </span>
          <div class="stat-body">
            <strong>
              {{ (auth.user?.scrapped_content_count ?? 0) + (auth.user?.scrapped_event_count ?? 0) }}
            </strong>
            <span>스크랩</span>
          </div>
        </button>
      </section>

      <!-- EBTI -->
      <section class="ebti-card">
        <div class="ebti-head">
          <span class="section-label">경제 EBTI</span>
        </div>

        <!-- 결과 없음 -->
        <div v-if="!auth.user?.ebti_result" class="ebti-empty">
          <p>아직 EBTI 검사를 하지 않았어요.</p>
          <p class="ebti-empty-sub">검사를 완료하면 AI 추천이 더 정확해져요.</p>
        </div>

        <!-- 결과 있음 -->
        <template v-else>
          <div class="ebti-persona">
            <span class="ebti-emoji">{{ auth.user.ebti_result.persona.emoji }}</span>
            <div>
              <p class="ebti-persona-name">{{ auth.user.ebti_result.persona.name }}</p>
              <p class="ebti-persona-desc">{{ auth.user.ebti_result.persona.desc }}</p>
            </div>
            <span class="ebti-score-chip">
              강점 {{ auth.user.ebti_result.strongCount }} / 5 , 총점 {{ auth.user.ebti_result.breakdown.reduce((sum, b) => sum + getDisplayScore(b.score), 0) }}점
            </span>
          </div>

          <div class="ebti-breakdown">
            <div
              v-for="b in auth.user.ebti_result.breakdown"
              :key="b.key"
              class="ebti-row"
            >
              <span class="ebti-label">
                <svg v-if="b.strong" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="3" stroke="currentColor" class="breakdown-icon strong-icon">
                  <path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" />
                </svg>
                <svg v-else xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="3" stroke="currentColor" class="breakdown-icon normal-icon">
                  <path stroke-linecap="round" stroke-linejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L6.832 19.82a4.5 4.5 0 0 1-1.897 1.13l-2.685.8.8-2.685a4.5 4.5 0 0 1 1.13-1.897L16.863 4.487Zm0 0L19.5 7.125" />
                </svg>
                {{ b.name }}
              </span>
              <div class="ebti-bar">
                <div
                  class="ebti-fill"
                  :class="{ strong: b.strong }"
                  :style="{ width: (getDisplayScore(b.score) / 20 * 100) + '%' }"
                ></div>
              </div>
              <span class="ebti-score">{{ getDisplayScore(b.score) }}/20</span>
            </div>
          </div>
        </template>

        <!-- EBTI 실행/재시험 버튼 박스 -->
        <RouterLink to="/ebti" class="ebti-action-box">
          {{ auth.user?.ebti_result ? '경제 EBTI 다시 검사하기' : '경제 EBTI 검사 시작하기' }}
        </RouterLink>
      </section>

      <!-- 탭 -->
      <nav ref="tabsEl" class="tabs">
        <button
          v-for="t in tabs"
          :key="t.key"
          class="tab"
          :class="{ on: activeTab === t.key }"
          @click="activeTab = t.key"
        >
          {{ t.label }}
        </button>
      </nav>

      <p v-if="loading" class="empty">불러오는 중...</p>

      <!-- 내가 쓴 글 / 좋아요한 글 -->
      <template v-else-if="activeTab === 'posts' || activeTab === 'liked-posts'">
        <ul
          v-if="(activeTab === 'posts' ? myPosts : likedPosts).length"
          class="post-list"
        >
          <RouterLink
            v-for="p in activeTab === 'posts' ? myPosts : likedPosts"
            :key="p.id"
            :to="`/community/${p.id}`"
            class="row"
          >
            <span class="c-board"><em>{{ p.board_display }}</em></span>
            <span class="c-title">
              {{ p.title }}
              <span v-if="p.comment_count" class="cc">[{{ p.comment_count }}]</span>
            </span>
            <span class="c-meta">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" class="meta-icon like-meta-ico"><path stroke-linecap="round" stroke-linejoin="round" d="M6.633 10.25c.806 0 1.533-.446 2.031-1.08a9.041 9.041 0 0 1 2.861-2.4c.723-.384 1.35-.956 1.653-1.715a4.498 4.498 0 0 0 .322-1.672V2.75a.75.75 0 0 1 .75-.75 2.25 2.25 0 0 1 2.25 2.25c0 1.152-.26 2.243-.723 3.218-.266.558.107 1.282.725 1.282m0 0h3.126c1.026 0 1.945.694 2.054 1.715.045.422.068.85.068 1.285a11.95 11.95 0 0 1-2.649 7.521c-.388.482-.987.729-1.602.729H13.48c-.408 0-.812-.1-1.185-.292a10.14 10.14 0 0 1-1.664-1.04l-.083-.066a9.753 9.753 0 0 0-2.285-1.242c-.227-.086-.467-.13-.709-.13H1.5v-7.375h5.133Z" /></svg>
              {{ p.like_count }}
            </span>
            <span class="c-meta">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" class="meta-icon view-meta-ico"><path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.43 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z" /><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" /></svg>
              {{ p.views.toLocaleString() }}
            </span>
            <span class="c-date">{{ fmt(p.created_at) }}</span>
          </RouterLink>
        </ul>
        <p v-else class="empty">
          {{ activeTab === 'posts' ? '아직 작성한 글이 없어요.' : '아직 좋아요한 글이 없어요.' }}
        </p>
      </template>

      <!-- 좋아요한 콘텐츠 -->
      <template v-else-if="activeTab === 'liked-contents'">
        <div v-if="likedContents.length" class="content-grid">
          <RouterLink
            v-for="c in likedContents"
            :key="c.id"
            :to="`/contents/${c.id}`"
            class="content-card"
          >
            <div class="thumb">
              <img
                v-if="c.youtube_id"
                :src="`https://img.youtube.com/vi/${c.youtube_id}/mqdefault.jpg`"
                alt=""
              />
              <div v-else class="thumb-ph">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" class="tv-placeholder-ico"><path stroke-linecap="round" stroke-linejoin="round" d="M6 20.25h12m-7.5-3v3m3-3v3m-10.125-3h17.25c.621 0 1.125-.504 1.125-1.125V4.875c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125Z" /></svg>
              </div>
            </div>
            <div class="card-body">
              <span class="cat">{{ c.category_display }}</span>
              <h3>{{ c.title }}</h3>
              <p class="meta">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" class="meta-icon like-meta-ico"><path stroke-linecap="round" stroke-linejoin="round" d="M6.633 10.25c.806 0 1.533-.446 2.031-1.08a9.041 9.041 0 0 1 2.861-2.4c.723-.384 1.35-.956 1.653-1.715a4.498 4.498 0 0 0 .322-1.672V2.75a.75.75 0 0 1 .75-.75 2.25 2.25 0 0 1 2.25 2.25c0 1.152-.26 2.243-.723 3.218-.266.558.107 1.282.725 1.282m0 0h3.126c1.026 0 1.945.694 2.054 1.715.045.422.068.85.068 1.285a11.95 11.95 0 0 1-2.649 7.521c-.388.482-.987.729-1.602.729H13.48c-.408 0-.812-.1-1.185-.292a10.14 10.14 0 0 1-1.664-1.04l-.083-.066a9.753 9.753 0 0 0-2.285-1.242c-.227-.086-.467-.13-.709-.13H1.5v-7.375h5.133Z" /></svg>
                {{ c.like_count }} · 
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" class="meta-icon view-meta-ico"><path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.43 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z" /><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" /></svg>
                {{ c.views.toLocaleString() }}
              </p>
            </div>
          </RouterLink>
        </div>
        <p v-else class="empty">아직 좋아요한 콘텐츠가 없어요.</p>
      </template>

      <!-- 스크랩 (콘텐츠 · 교육행사 분리) -->
      <template v-else>
        <div class="scrap-toggle">
          <button
            class="seg"
            :class="{ on: scrapKind === 'contents' }"
            @click="scrapKind = 'contents'"
          >
            콘텐츠 {{ scrapContents.length }}
          </button>
          <button
            class="seg"
            :class="{ on: scrapKind === 'events' }"
            @click="scrapKind = 'events'"
          >
            교육행사 {{ scrapEvents.length }}
          </button>
        </div>

        <!-- 스크랩한 콘텐츠 -->
        <template v-if="scrapKind === 'contents'">
          <div v-if="scrapContents.length" class="content-grid">
            <RouterLink
              v-for="c in scrapContents"
              :key="c.id"
              :to="`/contents/${c.id}`"
              class="content-card"
            >
              <div class="thumb">
                <img
                  v-if="c.youtube_id"
                  :src="`https://img.youtube.com/vi/${c.youtube_id}/mqdefault.jpg`"
                  alt=""
                />
                <div v-else class="thumb-ph">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" class="tv-placeholder-ico"><path stroke-linecap="round" stroke-linejoin="round" d="M6 20.25h12m-7.5-3v3m3-3v3m-10.125-3h17.25c.621 0 1.125-.504 1.125-1.125V4.875c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125Z" /></svg>
                </div>
              </div>
              <div class="card-body">
                <span class="cat">{{ c.category_display }}</span>
                <h3>{{ c.title }}</h3>
                <p class="meta">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" class="meta-icon like-meta-ico"><path stroke-linecap="round" stroke-linejoin="round" d="M6.633 10.25c.806 0 1.533-.446 2.031-1.08a9.041 9.041 0 0 1 2.861-2.4c.723-.384 1.35-.956 1.653-1.715a4.498 4.498 0 0 0 .322-1.672V2.75a.75.75 0 0 1 .75-.75 2.25 2.25 0 0 1 2.25 2.25c0 1.152-.26 2.243-.723 3.218-.266.558.107 1.282.725 1.282m0 0h3.126c1.026 0 1.945.694 2.054 1.715.045.422.068.85.068 1.285a11.95 11.95 0 0 1-2.649 7.521c-.388.482-.987.729-1.602.729H13.48c-.408 0-.812-.1-1.185-.292a10.14 10.14 0 0 1-1.664-1.04l-.083-.066a9.753 9.753 0 0 0-2.285-1.242c-.227-.086-.467-.13-.709-.13H1.5v-7.375h5.133Z" /></svg>
                  {{ c.like_count }} · 
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" class="meta-icon view-meta-ico"><path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.43 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z" /><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" /></svg>
                  {{ c.views.toLocaleString() }}
                </p>
              </div>
            </RouterLink>
          </div>
          <p v-else class="empty">아직 스크랩한 콘텐츠가 없어요.</p>
        </template>

        <!-- 스크랩한 교육행사 -->
        <template v-else>
          <ul v-if="scrapEvents.length" class="event-list">
            <RouterLink
              v-for="e in scrapEvents"
              :key="e.id"
              :to="`/events/${e.id}`"
              class="event-row"
            >
              <span class="ev-dday" :class="{ urgent: e.d_day !== null && e.d_day <= 2 }">
                {{ ddayLabel(e) }}
              </span>
              <span class="ev-title">{{ e.title }}</span>
              <span class="ev-status" :class="e.status">{{ e.status_display }}</span>
              <span class="ev-meta">{{ e.online_display }}</span>
              <span class="ev-meta">{{ e.region || '온라인' }}</span>
            </RouterLink>
          </ul>
          <p v-else class="empty">아직 스크랩한 교육행사가 없어요.</p>
        </template>
      </template>
    </div>

    <!-- 프로필 수정 모달 -->
    <div v-if="editing" class="modal-bg" @click.self="editing = false">
      <div class="modal">
        <h2>프로필 수정</h2>
        <form @submit.prevent="save">
          <div class="img-edit">
            <div class="avatar-lg sm">
              <img
                v-if="imagePreview || auth.user?.profile_image"
                :src="imagePreview || auth.user.profile_image"
                alt=""
              />
              <span v-else>{{ (form.nickname || 'U').charAt(0) }}</span>
            </div>
            <label class="file-btn">
              이미지 변경
              <input type="file" accept="image/*" @change="onFile" hidden />
            </label>
          </div>

          <label class="field">
            <span>닉네임</span>
            <input v-model="form.nickname" placeholder="닉네임" />
          </label>
          <label class="field">
            <span>이메일</span>
            <input v-model="form.email" type="email" placeholder="이메일" />
          </label>
          <label class="field">
            <span>새 비밀번호 (선택)</span>
            <input v-model="form.password" type="password" placeholder="변경할 새 비밀번호" />
          </label>
          <label class="field">
            <span>새 비밀번호 확인</span>
            <input v-model="form.password2" type="password" placeholder="비밀번호 다시 입력" />
          </label>

          <p v-if="saveError" class="err">{{ saveError }}</p>

          <div class="modal-actions">
            <button type="button" class="btn btn-outline" @click="editing = false">
              취소
            </button>
            <button type="submit" class="btn btn-navy" :disabled="saving">
              {{ saving ? '저장 중...' : '저장' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </main>
</template>

<style scoped>
.mypage {
  padding: 36px 0 60px;
  min-height: 70vh;
}

/* 프로필 카드 */
.profile-card {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 24px;
  background: #fff;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 28px 30px;
}
.avatar-lg {
  width: 84px;
  height: 84px;
  border-radius: 22px; /* 스쿼클 */
  background: linear-gradient(135deg, var(--teal), var(--navy));
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
  font-size: 2.1rem;
  font-weight: 800;
  overflow: hidden;
  box-shadow: 0 6px 18px rgba(20, 32, 74, 0.12);
  border: 3px solid #ffffff;
}
.avatar-lg span {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  line-height: 1;
  padding-bottom: 4px; /* 대형 아바타 정렬 보정 */
}
.avatar-lg img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.name-row {
  display: flex;
  align-items: center;
  gap: 10px;
}
.name-row h1 {
  font-size: 1.5rem;
  font-weight: 800;
  letter-spacing: -0.5px;
}
.lv-badge {
  background: #e6f4f1;
  color: var(--teal);
  font-size: 0.78rem;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 999px;
}
.sub {
  color: var(--text-sub);
  font-size: 0.84rem;
  margin-top: 3px;
}
.email {
  margin-top: 1px;
}
.lv-bar {
  margin-top: 12px;
  height: 8px;
  background: var(--bg);
  border-radius: 999px;
  overflow: hidden;
  max-width: 360px;
}
.lv-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--teal), var(--green));
  border-radius: 999px;
  transition: width 0.3s ease;
}
.lv-hint {
  font-size: 0.78rem;
  color: var(--text-mute);
  margin-top: 6px;
}
.lv-hint strong {
  color: var(--teal);
}
.edit-btn {
  align-self: start;
  white-space: nowrap;
}

/* 섹션 제목 */
.section-title {
  font-size: 1.05rem;
  font-weight: 800;
  letter-spacing: -0.3px;
  color: var(--navy);
  margin: 26px 2px 12px;
}

/* 연속 출석 배지 */
.streak-badge {
  background: #fff3e6;
  color: #c2680c;
  font-size: 0.78rem;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 999px;
  white-space: nowrap;
}

/* 나의 활동 현황 */
.stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  margin: 0 0 8px;
}
.stat {
  display: flex;
  align-items: center;
  gap: 14px;
  background: #fff;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 18px 20px;
  text-align: left;
  cursor: pointer;
  transition: transform 0.12s, box-shadow 0.12s, border-color 0.12s;
}
.stat:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-hover);
  border-color: var(--navy);
}
.stat-ico {
  width: 46px;
  height: 46px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  font-size: 1.35rem;
  flex-shrink: 0;
}
.ico-post {
  background: #eef2ff;
}
.ico-like {
  background: #e6f4f1;
}
.ico-content {
  background: #fee2e2;
}
.ico-scrap {
  background: #fff3e6;
}
.stat-body {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}
.stat strong {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--navy);
}
.stat-body span {
  font-size: 0.8rem;
  color: var(--text-sub);
  margin-top: 2px;
}

/* EBTI 카드 */
.ebti-card {
  background: #fff;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 22px 24px;
  margin-bottom: 18px;
}
.ebti-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}
.section-label {
  font-size: 0.9rem;
  font-weight: 800;
  color: var(--navy);
}
.ebti-action-box {
  display: block;
  width: fit-content;
  margin: 10px auto 0;
  text-align: center;
  background: var(--bg);
  color: var(--navy);
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  padding: 10px 24px;
  font-size: 0.85rem;
  font-weight: 700;
  transition: all 0.15s ease;
  cursor: pointer;
  text-decoration: none;
}
.ebti-action-box:hover {
  background: var(--navy);
  border-color: var(--navy);
  color: #fff;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(27, 42, 89, 0.15);
}
.ebti-empty {
  text-align: center;
  padding: 4px 0 6px;
  color: var(--text-sub);
}
.ebti-empty-ico {
  font-size: 2rem;
  display: block;
  margin-bottom: 10px;
}
.ebti-empty p {
  font-size: 0.92rem;
  font-weight: 600;
}
.ebti-empty-sub {
  font-size: 0.8rem;
  color: var(--text-mute);
  margin-top: 4px;
}
.ebti-persona {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}
.ebti-emoji {
  font-size: 2.2rem;
  flex-shrink: 0;
  width: 58px;
  height: 58px;
  background: #f8fafc;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
  border: 1px solid var(--line);
}
.ebti-persona-name {
  font-size: 1rem;
  font-weight: 800;
  color: var(--navy);
  white-space: pre-line;
}
.ebti-persona-desc {
  font-size: 0.8rem;
  color: var(--text-sub);
  margin-top: 3px;
  line-height: 1.5;
  white-space: pre-line;
}
.ebti-score-chip {
  margin-left: auto;
  font-size: 0.78rem;
  font-weight: 700;
  color: var(--navy);
  background: var(--bg);
  padding: 5px 12px;
  border-radius: 999px;
  white-space: nowrap;
}
.ebti-breakdown {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.ebti-row {
  display: grid;
  grid-template-columns: 146px 1fr 64px;
  align-items: center;
  gap: 10px;
}
.ebti-label {
  font-size: 0.82rem;
  font-weight: 600;
  white-space: nowrap;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
.breakdown-icon {
  width: 14px;
  height: 14px;
  flex-shrink: 0;
}
.strong-icon {
  color: var(--teal);
}
.normal-icon {
  color: var(--text-mute);
}
.ebti-bar {
  position: relative;
  height: 8px;
  background: var(--bg);
  border-radius: 999px;
  overflow: hidden;
  border: 1px solid var(--line);
  transform: translateZ(0); /* WebKit/Blink clipping bug fix */
}
.ebti-fill {
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  background: var(--text-mute);
  border-radius: 0 999px 999px 0; /* Left side square for perfect alignment, right side rounded */
  transition: width 0.4s ease;
}
.ebti-fill.strong {
  background: linear-gradient(90deg, var(--teal), var(--green));
}
.ebti-score {
  font-size: 0.76rem;
  color: var(--text-mute);
  font-weight: 700;
  text-align: right;
  white-space: nowrap;
}

/* 탭 */
.tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}
.tab {
  background: #fff;
  border: 1px solid var(--line);
  border-radius: 999px;
  padding: 9px 18px;
  font-size: 0.86rem;
  font-weight: 600;
  color: var(--text-sub);
}
.tab.on {
  background: var(--navy);
  color: #fff;
  border-color: var(--navy);
}

.empty {
  color: var(--text-mute);
  padding: 50px 0;
  text-align: center;
}

/* 게시글 목록 */
.post-list {
  list-style: none;
  margin: 0;
  padding: 0;
  background: #fff;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  overflow: hidden;
}
.row {
  display: grid;
  grid-template-columns: 90px 1fr 70px 70px 70px;
  align-items: center;
  gap: 10px;
  padding: 14px 18px;
  border-bottom: 1px solid var(--line);
  font-size: 0.88rem;
}
.row:last-child {
  border-bottom: none;
}
.row:hover {
  background: var(--bg);
}
.c-board em {
  font-style: normal;
  font-size: 0.74rem;
  color: var(--teal);
  font-weight: 700;
  background: #e6f4f1;
  padding: 3px 8px;
  border-radius: 6px;
}
.c-title {
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.cc {
  color: var(--green);
  font-weight: 700;
  font-size: 0.8rem;
}
.c-meta,
.c-date {
  color: var(--text-mute);
  font-size: 0.8rem;
  text-align: center;
}

/* 스크랩 내부 토글 (콘텐츠 / 교육행사) */
.scrap-toggle {
  display: inline-flex;
  gap: 4px;
  background: var(--bg);
  border: 1px solid var(--line);
  border-radius: 999px;
  padding: 4px;
  margin-bottom: 18px;
}
.seg {
  border: none;
  background: transparent;
  border-radius: 999px;
  padding: 8px 18px;
  font-size: 0.84rem;
  font-weight: 700;
  color: var(--text-sub);
  cursor: pointer;
  transition: background 0.12s, color 0.12s;
}
.seg.on {
  background: #fff;
  color: var(--navy);
  box-shadow: var(--shadow);
}

/* 스크랩한 교육행사 목록 */
.event-list {
  list-style: none;
  margin: 0;
  padding: 0;
  background: #fff;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  overflow: hidden;
}
.event-row {
  display: grid;
  grid-template-columns: 72px 1fr 72px 90px 90px;
  align-items: center;
  gap: 12px;
  padding: 14px 18px;
  border-bottom: 1px solid var(--line);
  font-size: 0.88rem;
}
.event-row:last-child {
  border-bottom: none;
}
.event-row:hover {
  background: var(--bg);
}
.ev-dday {
  font-size: 0.74rem;
  font-weight: 800;
  color: #fff;
  background: #2563eb;
  padding: 4px 8px;
  border-radius: 7px;
  text-align: center;
}
.ev-dday.urgent {
  background: #dc2626;
}
.ev-title {
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.ev-status {
  font-size: 0.72rem;
  font-weight: 700;
  padding: 3px 9px;
  border-radius: 999px;
  color: #fff;
  text-align: center;
}
.ev-status.open { background: var(--green); }
.ev-status.closed { background: #d97706; }
.ev-status.ended { background: #6b7280; }
.ev-meta {
  color: var(--text-mute);
  font-size: 0.8rem;
  text-align: center;
}

/* 콘텐츠 그리드 */
.content-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
}
.content-card {
  background: #fff;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  overflow: hidden;
  transition: transform 0.12s, box-shadow 0.12s;
}
.content-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-hover);
}
.thumb {
  aspect-ratio: 16 / 9;
  background: var(--bg);
}
.thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.thumb-ph {
  width: 100%;
  height: 100%;
  display: grid;
  place-items: center;
  font-size: 2rem;
}
.card-body {
  padding: 14px;
}
.cat {
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--teal);
}
.card-body h3 {
  font-size: 0.95rem;
  font-weight: 600;
  margin: 6px 0;
  line-height: 1.35;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.card-body .meta {
  font-size: 0.78rem;
  color: var(--text-mute);
}

/* 모달 */
.modal-bg {
  position: fixed;
  inset: 0;
  background: rgba(20, 32, 74, 0.4);
  display: grid;
  place-items: center;
  z-index: 100;
  padding: 16px;
}
.modal {
  width: 100%;
  max-width: 400px;
  background: #fff;
  border-radius: 18px;
  padding: 28px;
  box-shadow: var(--shadow-hover);
}
.modal h2 {
  font-size: 1.2rem;
  font-weight: 800;
  margin-bottom: 18px;
}
.img-edit {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 18px;
}
.avatar-lg.sm {
  width: 64px;
  height: 64px;
  font-size: 1.5rem;
  border-radius: 18px; /* 모달 내 아바타 둥글기 */
}
.avatar-lg.sm span {
  padding-bottom: 3px; /* 소형 아바타 정렬 보정 */
}
.file-btn {
  font-size: 0.84rem;
  font-weight: 600;
  color: var(--navy);
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  padding: 9px 14px;
  cursor: pointer;
}
.file-btn:hover {
  border-color: var(--navy);
}
.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 14px;
}
.field span {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--text-sub);
}
.field input {
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  padding: 12px 14px;
  font-size: 0.9rem;
  outline: none;
}
.field input:focus {
  border-color: var(--navy);
}
.err {
  color: #dc2626;
  font-size: 0.8rem;
  margin-bottom: 10px;
}
.modal-actions {
  display: flex;
  gap: 10px;
  margin-top: 6px;
}
.modal-actions .btn {
  flex: 1;
}

@media (max-width: 680px) {
  .profile-card {
    grid-template-columns: auto 1fr;
  }
  .edit-btn {
    grid-column: 1 / -1;
    width: 100%;
  }
  .stats {
    grid-template-columns: 1fr 1fr;
  }
  .row {
    grid-template-columns: 1fr 60px 60px;
  }
  .c-board,
  .row .c-date {
    display: none;
  }
  .event-row {
    grid-template-columns: 60px 1fr 64px;
  }
  .event-row .ev-meta {
    display: none;
  }
}

/* 이모지 대체용 SVG 아이콘 스타일 */
.inline-icon {
  display: inline-block;
  width: 14px;
  height: 14px;
  vertical-align: -2px;
  margin-right: 4px;
}
.flame-icon {
  width: 13px;
  height: 13px;
  color: #ea580c;
  vertical-align: -1px;
}
.email-icon {
  color: var(--text-sub);
}
.stat-svg {
  width: 22px;
  height: 22px;
}
.post-color { color: #4f46e5; }
.like-color { color: #0d9488; }
.content-color { color: #e11d48; }
.scrap-color { color: #ea580c; }

.ebti-empty-svg {
  width: 44px;
  height: 44px;
  color: var(--text-mute);
  margin: 0 auto 12px;
  display: block;
}

.breakdown-icon {
  width: 14px;
  height: 14px;
  margin-right: 6px;
  vertical-align: -2px;
  display: inline-block;
}
.strong-icon {
  color: var(--green);
}
.normal-icon {
  color: var(--text-mute);
}

.meta-icon {
  width: 13px;
  height: 13px;
  vertical-align: -2px;
  display: inline-block;
  margin-right: 3px;
}
.like-meta-ico {
  color: var(--teal);
}
.view-meta-ico {
  color: var(--text-mute);
}

.tv-placeholder-ico {
  width: 48px;
  height: 48px;
  color: var(--text-mute);
  opacity: 0.6;
}
</style>
