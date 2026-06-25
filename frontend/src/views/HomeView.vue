<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import api from '@/api'
import ContentCard from '@/components/home/ContentCard.vue'
import EventCard from '@/components/home/EventCard.vue'
import CardCarousel from '@/components/common/CardCarousel.vue'
import HeroCarousel from '@/components/home/HeroCarousel.vue'
import SideAuth from '@/components/home/SideAuth.vue'
import SideQuiz from '@/components/home/SideQuiz.vue'
import SideCalendar from '@/components/home/SideCalendar.vue'
import SideTerms from '@/components/home/SideTerms.vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

const recommended = ref([])
const latest = ref([])
const popular = ref([])
const events = ref([])
const posts = ref([])

const loadingContents = ref(true)
const loadingRec = ref(true)

// 콘텐츠 캐시 (5분 TTL)
const CACHE_KEY = 'home_cache'
const CACHE_TTL = 5 * 60 * 1000

// AI 추천 캐시 키 (사용자별, TTL 없음)
const recCacheKey = computed(() => `home_rec_${auth.user?.id ?? 'anon'}`)

function loadCache() {
  try {
    const raw = localStorage.getItem(CACHE_KEY)
    if (!raw) return null
    const { ts, data } = JSON.parse(raw)
    if (Date.now() - ts > CACHE_TTL) return null
    return data
  } catch { return null }
}

function saveCache(data) {
  try { localStorage.setItem(CACHE_KEY, JSON.stringify({ ts: Date.now(), data })) } catch {}
}

function loadRecCache() {
  try {
    const raw = localStorage.getItem(recCacheKey.value)
    return raw ? JSON.parse(raw) : null
  } catch { return null }
}

function saveRecCache(data) {
  try { localStorage.setItem(recCacheKey.value, JSON.stringify(data)) } catch {}
}

function applyData({ pop, ev, ps, lat }) {
  popular.value = (pop || []).slice(0, 16)
  events.value = (ev || []).slice(0, 16)
  posts.value = (ps || []).slice(0, 5)
  latest.value = (lat || []).slice(0, 16)
}

function getEbti() {
  try { return JSON.parse(localStorage.getItem('ebtiResult') || 'null') } catch { return null }
}

onMounted(async () => {
  // 캐시 즉시 표시
  const cached = loadCache()
  if (cached) { applyData(cached); loadingContents.value = false }

  const cachedRec = loadRecCache()
  if (cachedRec?.length) { recommended.value = cachedRec; loadingRec.value = false }

  // 비로그인이면 추천 로딩 상태 즉시 해제 (로그인 유도 표시)
  if (!auth.isLoggedIn) loadingRec.value = false

  // 콘텐츠 fetch (항상 최신으로 갱신)
  try {
    const [pop, ev, ps, lat] = await Promise.all([
      api.get('/contents/', { params: { ordering: 'views' } }),
      api.get('/events/', { params: { status: 'open' } }),
      api.get('/posts/', { params: { popular: 1 } }),
      api.get('/contents/'),
    ])
    const fresh = { pop: pop.data || [], ev: ev.data || [], ps: ps.data || [], lat: lat.data || [] }
    applyData(fresh)
    saveCache(fresh)
  } catch (e) {
    console.error('콘텐츠 로딩 실패', e)
  } finally {
    loadingContents.value = false
  }

  // AI 추천 — 캐시가 없을 때만 fetch
  if (auth.isLoggedIn && !cachedRec?.length) {
    try {
      const res = await api.post('/contents/ai-recommend/', {
        ebti: getEbti(),
        region: auth.user?.region || '',
      })
      const rec = (res.data.items || []).map(it => it.content).slice(0, 16)
      recommended.value = rec
      if (rec.length) saveRecCache(rec)
    } catch {
      try {
        const res = await api.get('/contents/', { params: { recommended: 1 } })
        const rec = (res.data || []).slice(0, 16)
        recommended.value = rec
        if (rec.length) saveRecCache(rec)
      } catch {}
    } finally {
      loadingRec.value = false
    }
  }
})
</script>

<template>
  <main class="home">
    <div class="layout">
      <!-- ===== 본문 ===== -->
      <div class="main-col">
        <!-- 히어로 배너 (캐러셀) -->
        <HeroCarousel />

        <!-- AI 추천 콘텐츠 -->
        <section class="block">
          <div class="section-head">
            <h2> 추천 콘텐츠<span class="sub">나에게 딱 맞는 콘텐츠를 추천해드려요</span></h2>
            <RouterLink :to="auth.isLoggedIn ? '/ai-recommend' : '/login'" class="more">
              <span>더보기</span>
              <svg class="arrow-ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="9 18 15 12 9 6"></polyline>
              </svg>
            </RouterLink>
          </div>

          <!-- 비로그인 -->
          <div v-if="!auth.isLoggedIn" class="rec-wrap">
            <div class="skel-row static">
              <div v-for="n in 4" :key="n" class="skel-card"><div class="skel-thumb static"></div><div class="skel-body"><div class="skel-line w80 static"></div><div class="skel-line w60 static"></div><div class="skel-line w40 mt8 static"></div></div></div>
            </div>
            <div class="rec-lock">
              <div class="lock-box">
                <p class="lock-title">나만을 위한 맞춤 콘텐츠가 기다리고 있어요</p>
                <p class="lock-desc">로그인하면 관심사에 딱 맞는 콘텐츠를 추천해드려요.</p>
                <RouterLink to="/login" class="btn btn-navy">로그인하고 추천받기 →</RouterLink>
                <p class="lock-sub">아직 회원이 아니신가요? <RouterLink to="/signup">회원가입</RouterLink></p>
              </div>
            </div>
          </div>

          <!-- 로그인 + 로딩 중 -->
          <div v-else-if="loadingRec" class="skel-row">
            <div v-for="n in 4" :key="n" class="skel-card"><div class="skel-thumb"></div><div class="skel-body"><div class="skel-line w80"></div><div class="skel-line w60"></div><div class="skel-line w40 mt8"></div></div></div>
          </div>

          <!-- 로그인 + 추천 데이터 없음 -->
          <div v-else-if="!recommended.length" class="rec-empty">
            <p class="rec-empty-title">아직 추천 콘텐츠가 없어요</p>
            <p class="rec-empty-desc">관심 분야를 설정하면 나에게 딱 맞는 콘텐츠를 추천해드려요.</p>
            <RouterLink to="/ai-recommend" class="btn btn-navy">AI 추천 받기 →</RouterLink>
          </div>

          <!-- 로그인 + 추천 데이터 있음 -->
          <CardCarousel v-else :items="recommended" v-slot="{ item }">
            <ContentCard :content="item" />
          </CardCarousel>
        </section>

        <!-- 최신 콘텐츠 -->
        <section class="block">
          <div class="section-head">
            <h2>최신 콘텐츠<span class="sub">새로 등록된 콘텐츠를 만나보세요</span></h2>
            <RouterLink to="/contents" class="more">
              <span>더보기</span>
              <svg class="arrow-ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="9 18 15 12 9 6"></polyline>
              </svg>
            </RouterLink>
          </div>
          <div v-if="loadingContents && !latest.length" class="skel-row">
            <div v-for="n in 4" :key="n" class="skel-card"><div class="skel-thumb"></div><div class="skel-body"><div class="skel-line w80"></div><div class="skel-line w60"></div><div class="skel-line w40 mt8"></div></div></div>
          </div>
          <CardCarousel v-else :items="latest" v-slot="{ item }">
            <ContentCard :content="item" />
          </CardCarousel>
        </section>

        <!-- 인기 콘텐츠 -->
        <section class="block">
          <div class="section-head">
            <h2>인기 콘텐츠<span class="sub">지금 가장 많이 본 콘텐츠</span></h2>
            <RouterLink to="/contents" class="more">
              <span>더보기</span>
              <svg class="arrow-ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="9 18 15 12 9 6"></polyline>
              </svg>
            </RouterLink>
          </div>
          <div v-if="loadingContents && !popular.length" class="skel-row">
            <div v-for="n in 4" :key="n" class="skel-card"><div class="skel-thumb"></div><div class="skel-body"><div class="skel-line w80"></div><div class="skel-line w60"></div><div class="skel-line w40 mt8"></div></div></div>
          </div>
          <CardCarousel v-else :items="popular" v-slot="{ item }">
            <ContentCard :content="item" />
          </CardCarousel>
        </section>

        <!-- 교육 행사 & 프로그램 -->
        <section class="block">
          <div class="section-head">
            <h2>교육 행사 &amp; 프로그램</h2>
            <RouterLink to="/events" class="more">
              <span>더보기</span>
              <svg class="arrow-ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="9 18 15 12 9 6"></polyline>
              </svg>
            </RouterLink>
          </div>
          <div v-if="loadingContents && !events.length" class="skel-row">
            <div v-for="n in 4" :key="n" class="skel-card"><div class="skel-thumb skel-thumb-event"></div><div class="skel-body"><div class="skel-line w80"></div><div class="skel-line w60"></div><div class="skel-line w40 mt8"></div></div></div>
          </div>
          <CardCarousel v-else :items="events" v-slot="{ item }">
            <EventCard :event="item" />
          </CardCarousel>
        </section>

        <!-- 인기 게시글 -->
        <section class="block">
          <div class="section-head">
            <h2>인기 게시글</h2>
            <RouterLink to="/community" class="more">
              <span>더보기</span>
              <svg class="arrow-ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="9 18 15 12 9 6"></polyline>
              </svg>
            </RouterLink>
          </div>
          <ul v-if="loadingContents && !posts.length" class="post-list">
            <li v-for="n in 5" :key="n" class="skel-post-row">
              <span class="skel-rank"></span>
              <span class="skel-badge"></span>
              <span class="skel-line flex1"></span>
              <span class="skel-line w60 skel-info"></span>
            </li>
          </ul>
          <ul v-else class="post-list">
            <RouterLink
              v-for="(p, i) in posts"
              :key="p.id"
              :to="`/community/${p.id}`"
              custom
              v-slot="{ navigate }"
            >
              <li @click="navigate">
                <span class="rank">{{ i + 1 }}</span>
                <span class="board">{{ p.board_display }}</span>
                <span class="title">{{ p.title }}</span>
                <span class="info">
                  💬 {{ p.comment_count }} · 👁 {{ p.views.toLocaleString() }}
                </span>
              </li>
            </RouterLink>
          </ul>
        </section>
      </div>

      <!-- ===== 사이드바 ===== -->
      <aside class="side-col">
        <SideAuth />
        <SideQuiz />
        <SideCalendar />
        <SideTerms />
      </aside>
    </div>
  </main>
</template>

<style scoped>
.home {
  padding: 26px 0 10px;
}
.layout {
  position: relative;
  width: 100%;
  max-width: 1160px;
  margin: 0 auto;
  padding: 0 20px;
}
.main-col {
  display: flex;
  flex-direction: column;
  gap: 38px;
  min-width: 0;
}
.side-col {
  position: absolute;
  top: 0;
  left: calc(100% + 28px);
  width: 320px;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

/* 사이드바를 넣을 공간이 부족하면(약 1850px 이하) 기존 2단 레이아웃으로 */
@media (max-width: 1860px) {
  .layout {
    display: grid;
    grid-template-columns: 1fr 320px;
    gap: 28px;
    align-items: start;
  }
  .side-col {
    position: static;
    width: auto;
  }
}

/* ===== 스켈레톤 UI ===== */
@keyframes shimmer {
  0%   { background-position: -600px 0 }
  100% { background-position: 600px 0 }
}
.skel-row {
  display: flex;
  gap: 16px;
  overflow: hidden;
  padding: 4px 2px;
}
.skel-card {
  flex: 0 0 calc((100% - 48px) / 4);
  background: #fff;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  overflow: hidden;
}
.skel-thumb {
  aspect-ratio: 16 / 10;
  background: linear-gradient(90deg, #e8eaf0 25%, #f4f5f8 50%, #e8eaf0 75%);
  background-size: 600px 100%;
  animation: shimmer 1.4s infinite linear;
}
.skel-thumb-event {
  aspect-ratio: 16 / 9;
}
.skel-body {
  padding: 13px 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.skel-line {
  height: 12px;
  border-radius: 6px;
  background: linear-gradient(90deg, #e8eaf0 25%, #f4f5f8 50%, #e8eaf0 75%);
  background-size: 600px 100%;
  animation: shimmer 1.4s infinite linear;
}
.skel-line.w80 { width: 80%; }
.skel-line.w60 { width: 60%; }
.skel-line.w40 { width: 40%; }
.skel-line.flex1 { flex: 1; }
.skel-line.mt8 { margin-top: 4px; }

/* 게시글 스켈레톤 */
.skel-post-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 18px;
  border-bottom: 1px solid var(--line);
}
.skel-post-row:last-child { border-bottom: none; }
.skel-rank {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  flex-shrink: 0;
  background: linear-gradient(90deg, #e8eaf0 25%, #f4f5f8 50%, #e8eaf0 75%);
  background-size: 600px 100%;
  animation: shimmer 1.4s infinite linear;
}
.skel-badge {
  width: 48px;
  height: 20px;
  border-radius: 6px;
  flex-shrink: 0;
  background: linear-gradient(90deg, #e8eaf0 25%, #f4f5f8 50%, #e8eaf0 75%);
  background-size: 600px 100%;
  animation: shimmer 1.4s infinite linear;
}
.skel-info { height: 12px; border-radius: 6px; flex-shrink: 0; }

/* AI 추천 없음 CTA */
.rec-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 40px 24px;
  background: #fff;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  text-align: center;
}
.rec-empty-title {
  font-size: 1rem;
  font-weight: 800;
  color: var(--navy);
}
.rec-empty-desc {
  font-size: 0.86rem;
  color: var(--text-sub);
}
.rec-empty .btn {
  margin-top: 6px;
  padding: 10px 22px;
  font-size: 0.88rem;
}

/* 비로그인 정적 회색 카드 (애니메이션 없음) */
.skel-thumb.static,
.skel-line.static {
  background: #e8eaf0;
  animation: none;
}

/* 추천 콘텐츠 잠금 (비로그인) */
.rec-wrap {
  position: relative;
}
.blurred {
  filter: blur(6px);
  pointer-events: none;
  user-select: none;
}
.rec-lock {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(238, 240, 248, 0.25);
  border-radius: var(--radius);
  z-index: 10;
}
.lock-box {
  background: #ffffff;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 24px 32px;
  box-shadow: 0 10px 30px rgba(27, 42, 89, 0.15);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  gap: 10px;
  max-width: 420px;
  width: 90%;
}
.lock-title {
  font-size: 1.05rem;
  font-weight: 800;
  color: var(--navy);
}
.lock-desc {
  font-size: 0.86rem;
  color: var(--text-sub);
}
.lock-box .btn {
  padding: 10px 20px;
  font-size: 0.88rem;
  margin: 4px 0;
}
.lock-sub {
  font-size: 0.8rem;
  color: var(--text-sub);
}
.lock-sub a {
  color: var(--navy);
  font-weight: 700;
}

/* 그리드 */
.grid-4 {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}
.grid-3 {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
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
.post-list li {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 18px;
  border-bottom: 1px solid var(--line);
  font-size: 0.88rem;
}
.post-list li:last-child {
  border-bottom: none;
}
.post-list li:hover {
  background: var(--bg);
}
.post-list li {
  cursor: pointer;
}
.rank {
  font-weight: 800;
  color: var(--navy);
  width: 18px;
  text-align: center;
}
.board {
  font-size: 0.72rem;
  color: var(--teal);
  font-weight: 700;
  background: #e6f4f1;
  padding: 3px 8px;
  border-radius: 6px;
  white-space: nowrap;
}
.post-list .title {
  flex: 1;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.post-list .info {
  font-size: 0.75rem;
  color: var(--text-mute);
  white-space: nowrap;
}

/* 반응형 */
@media (max-width: 1299.98px) {
  .layout {
    grid-template-columns: 1fr;
  }
  .side-col {
    display: none;
  }
}
@media (max-width: 768px) {
  .grid-4 {
    grid-template-columns: repeat(2, 1fr);
  }
}
@media (max-width: 560px) {
  .grid-4,
  .grid-3 {
    grid-template-columns: 1fr;
  }
  .post-list .info {
    display: none;
  }
}
</style>
