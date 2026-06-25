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
  try {
    let payload
    if (imageFile.value) {
      payload = new FormData()
      payload.append('nickname', form.value.nickname)
      payload.append('email', form.value.email)
      payload.append('profile_image', imageFile.value)
    } else {
      payload = { nickname: form.value.nickname, email: form.value.email }
    }
    await auth.updateProfile(payload)
    editing.value = false
  } catch (err) {
    saveError.value =
      err.response?.data?.nickname?.[0] ||
      err.response?.data?.email?.[0] ||
      '저장에 실패했어요. 다시 시도해주세요.'
  } finally {
    saving.value = false
  }
}

/* ── 표시용 계산값 ─────────────────────── */
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
              🔥 연속 출석 {{ auth.user.attendance_streak }}일
            </span>
          </div>
          <p class="sub">@{{ auth.user?.username }}</p>
          <p class="sub email" v-if="auth.user?.email">✉️ {{ auth.user.email }}</p>
        </div>

        <button class="btn btn-outline edit-btn" @click="startEdit">프로필 수정</button>
      </section>

      <!-- 나의 활동 현황 -->
      <h2 class="section-title">나의 활동 현황</h2>
      <section class="stats">
        <button class="stat" @click="goTab('posts')">
          <span class="stat-ico ico-post">📝</span>
          <div class="stat-body">
            <strong>{{ auth.user?.post_count ?? 0 }}</strong>
            <span>작성 글</span>
          </div>
        </button>
        <button class="stat" @click="goTab('liked-posts')">
          <span class="stat-ico ico-like">👍</span>
          <div class="stat-body">
            <strong>{{ auth.user?.liked_post_count ?? 0 }}</strong>
            <span>좋아요한 글</span>
          </div>
        </button>
        <button class="stat" @click="goTab('liked-contents')">
          <span class="stat-ico ico-content">❤️</span>
          <div class="stat-body">
            <strong>{{ auth.user?.liked_content_count ?? 0 }}</strong>
            <span>좋아요한 콘텐츠</span>
          </div>
        </button>
        <button class="stat" @click="goTab('scrap')">
          <span class="stat-ico ico-scrap">🔖</span>
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
          <RouterLink to="/ebti" class="ebti-retest">
            {{ auth.user?.ebti_result ? '다시 검사하기' : 'EBTI 검사하기' }} →
          </RouterLink>
        </div>

        <!-- 결과 없음 -->
        <div v-if="!auth.user?.ebti_result" class="ebti-empty">
          <span class="ebti-empty-ico">📋</span>
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
              강점 {{ auth.user.ebti_result.strongCount }} / 5
            </span>
          </div>

          <div class="ebti-breakdown">
            <div
              v-for="b in auth.user.ebti_result.breakdown"
              :key="b.key"
              class="ebti-row"
            >
              <span class="ebti-label">
                {{ b.strong ? '✅' : '✏️' }} {{ b.name }}
              </span>
              <div class="ebti-bar">
                <div
                  class="ebti-fill"
                  :class="{ strong: b.strong }"
                  :style="{ width: Math.max(b.ratio * 100, 4) + '%' }"
                ></div>
              </div>
              <span class="ebti-score">{{ b.score }}점</span>
            </div>
          </div>
        </template>
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
            <span class="c-meta">👍 {{ p.like_count }}</span>
            <span class="c-meta">👁 {{ p.views.toLocaleString() }}</span>
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
              <div v-else class="thumb-ph">📺</div>
            </div>
            <div class="card-body">
              <span class="cat">{{ c.category_display }}</span>
              <h3>{{ c.title }}</h3>
              <p class="meta">👍 {{ c.like_count }} · 👁 {{ c.views.toLocaleString() }}</p>
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
                <div v-else class="thumb-ph">📺</div>
              </div>
              <div class="card-body">
                <span class="cat">{{ c.category_display }}</span>
                <h3>{{ c.title }}</h3>
                <p class="meta">👍 {{ c.like_count }} · 👁 {{ c.views.toLocaleString() }}</p>
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
  border-radius: 999px;
  background: linear-gradient(135deg, var(--teal), var(--navy));
  color: #fff;
  display: grid;
  place-items: center;
  font-size: 2.1rem;
  font-weight: 800;
  overflow: hidden;
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
.ebti-retest {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--teal);
}
.ebti-retest:hover {
  text-decoration: underline;
}
.ebti-empty {
  text-align: center;
  padding: 24px 0 10px;
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
  font-size: 2.4rem;
  flex-shrink: 0;
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
  grid-template-columns: 120px 1fr 40px;
  align-items: center;
  gap: 10px;
}
.ebti-label {
  font-size: 0.82rem;
  font-weight: 600;
}
.ebti-bar {
  height: 8px;
  background: var(--bg);
  border-radius: 999px;
  overflow: hidden;
  border: 1px solid var(--line);
}
.ebti-fill {
  height: 100%;
  background: var(--text-mute);
  border-radius: 999px;
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
</style>
