<script setup>
import { nextTick, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import api from '@/api'
import { useAuthStore } from '@/stores/auth'
import { hasKakaoKey, loadKakao } from '@/utils/kakaoMap'
import { getEventTheme } from '@/utils/eventTheme'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const event = ref(null)
const loading = ref(true)
const mapEl = ref(null)
const mapError = ref('') // 'NO_KEY' | 'LOAD_FAILED' | ''

const ddayLabel = (e) =>
  e.d_day === null ? '접수마감' : e.d_day === 0 ? 'D-DAY' : `D-${e.d_day}`

async function load() {
  loading.value = true
  try {
    const { data } = await api.get(`/events/${route.params.id}/`)
    event.value = data
  } catch {
    alert('행사를 찾을 수 없습니다.')
    router.push('/events')
    return
  } finally {
    loading.value = false
  }
  // 지도 초기화는 API 에러 catch 바깥에서 — 지도 오류가 잘못된 alert를 유발하지 않도록
  await nextTick()
  const data = event.value
  if (data.latitude && data.longitude) {
    // lat/lng가 있어도 Kakao SDK를 먼저 로드한 뒤 initMap 호출
    if (!hasKakaoKey()) {
      mapError.value = 'NO_KEY'
    } else {
      try {
        await loadKakao()
        initMap(data.latitude, data.longitude, data)
      } catch (err) {
        mapError.value = err.message === 'NO_KEY' ? 'NO_KEY' : 'LOAD_FAILED'
      }
    }
  } else if (data.address) {
    geocodeAndShow(data.address, data)
  }
}

async function geocodeAndShow(address, e) {
  mapError.value = ''
  if (!hasKakaoKey()) { mapError.value = 'NO_KEY'; return }
  try {
    const kakao = await loadKakao()
    const geocoder = new kakao.maps.services.Geocoder()
    geocoder.addressSearch(address, (result, status) => {
      if (status === kakao.maps.services.Status.OK) {
        initMap(parseFloat(result[0].y), parseFloat(result[0].x), e)
      } else {
        mapError.value = 'GEOCODE_FAILED'
      }
    })
  } catch (err) {
    mapError.value = err.message === 'NO_KEY' ? 'NO_KEY' : 'LOAD_FAILED'
  }
}

function initMap(lat, lng, e) {
  mapError.value = ''
  if (!window.kakao?.maps) { mapError.value = 'NO_KEY'; return }
  const center = new window.kakao.maps.LatLng(lat, lng)
  const map = new window.kakao.maps.Map(mapEl.value, { center, level: 4 })
  const marker = new window.kakao.maps.Marker({ position: center })
  marker.setMap(map)
  const iw = new window.kakao.maps.InfoWindow({
    content:
      `<div style="padding:6px 10px;font-size:12px;font-weight:600;white-space:nowrap">`
      + (e.place_name || e.region) + `</div>`,
  })
  iw.open(map, marker)
}

async function toggleScrap() {
  if (!auth.isLoggedIn) {
    if (confirm('로그인이 필요합니다. 로그인 페이지로 이동하시겠습니까?')) {
      router.push({ name: 'login', query: { redirect: route.fullPath } })
    }
    return
  }
  const { data } = await api.post(`/events/${event.value.id}/scrap/`)
  event.value.is_scrapped = data.scrapped
  event.value.scrap_count = data.scrap_count
}

function fmtDate(d) {
  return d ? d.replaceAll('-', '.') : ''
}

watch(() => route.params.id, load)
onMounted(load)
</script>

<template>
  <main class="detail">
    <div class="container narrow">
      <RouterLink to="/events" class="back">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" class="back-icon">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5" />
        </svg>
        <span>행사 목록</span>
      </RouterLink>

      <p v-if="loading" class="empty">불러오는 중...</p>

      <template v-else-if="event">
        <!-- 헤더 배너 -->
        <div class="banner" :style="getEventTheme(event).image ? {} : { background: getEventTheme(event).gradient }">
          <img v-if="getEventTheme(event).image" :src="getEventTheme(event).image" :alt="event.title" class="banner-img" />
          <template v-else>
            <span class="b-icon main">{{ getEventTheme(event).icons[0] }}</span>
            <span class="b-icon sub1">{{ getEventTheme(event).icons[1] }}</span>
            <span class="b-icon sub2">{{ getEventTheme(event).icons[2] }}</span>
          </template>
          <span class="dday" :class="{ urgent: event.d_day !== null && event.d_day <= 2 }">
            {{ ddayLabel(event) }}
          </span>
        </div>

        <div class="head">
          <span class="status" :class="event.status">{{ event.status_display }}</span>
          <h1>{{ event.title }}</h1>
          <p class="summary">{{ event.summary }}</p>
          <button class="scrap" :class="{ on: event.is_scrapped }" @click="toggleScrap">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke-width="2"
              stroke="currentColor"
              class="bookmark-icon"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M17.593 3.322c1.1.128 1.907 1.077 1.907 2.185V21L12 17.25 4.5 21V5.507c0-1.108.806-2.057 1.907-2.185a48.507 48.507 0 0 1 11.186 0Z"
              />
            </svg>
            <span>{{ event.is_scrapped ? '스크랩됨' : '스크랩' }} {{ event.scrap_count }}</span>
          </button>
        </div>

        <!-- 정보 테이블 -->
        <dl class="info">
          <div><dt>주최</dt><dd>{{ event.host || '-' }}</dd></div>
          <div><dt>지역</dt><dd>{{ event.region || '-' }}</dd></div>
          <div><dt>진행 방식</dt><dd>{{ event.online_display }}</dd></div>
          <div>
            <dt>접수 기간</dt>
            <dd>{{ fmtDate(event.start_date) }} ~ {{ fmtDate(event.end_date) }}</dd>
          </div>
          <div v-if="event.place_name">
            <dt>장소</dt>
            <dd>{{ event.place_name }}</dd>
          </div>
          <div v-if="event.address">
            <dt>주소</dt>
            <dd>{{ event.address }}</dd>
          </div>
        </dl>

        <!-- 본문 -->
        <section class="body-sec">
          <h2>행사 소개</h2>
          <p class="body">{{ event.body }}</p>
        </section>

        <!-- 지도 -->
        <section class="map-sec">
          <h2>오시는 길</h2>

          <template v-if="event.latitude && event.longitude || event.address">
            <div ref="mapEl" class="map"></div>
            <p v-if="mapError === 'NO_KEY'" class="map-msg">
              🗺️ 카카오맵 키가 설정되지 않았습니다.
              <code>frontend/.env</code>의 <code>VITE_KAKAO_MAP_KEY</code>에
              키를 넣으면 지도가 표시됩니다.
            </p>
            <p v-else-if="mapError === 'LOAD_FAILED'" class="map-msg">
              지도를 불러오지 못했습니다. 키와 사이트 도메인 등록을 확인해주세요.
            </p>
            <p v-else-if="mapError === 'GEOCODE_FAILED'" class="map-msg">
              주소를 지도에 표시하지 못했습니다.
            </p>
            <p v-else class="addr">📍 {{ event.place_name }} · {{ event.address }}</p>
          </template>

          <p v-else-if="event.online_type === 'online' || event.online_type === 'both'" class="online-note">💻 온라인으로 진행되는 행사입니다.</p>
          <p v-else class="no-map-note">📍 장소 정보가 아직 등록되지 않았습니다.</p>
        </section>

        <RouterLink to="/events" class="btn btn-navy block">목록으로 돌아가기</RouterLink>
      </template>
    </div>
  </main>
</template>

<style scoped>
.detail {
  padding: 28px 0 30px;
  min-height: 72vh;
}
.narrow {
  max-width: 800px;
}
.back {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 20px;
  font-size: 0.86rem;
  font-weight: 600;
  color: var(--text-sub);
  text-decoration: none;
  transition: transform 0.2s ease;
}
.back:hover {
  transform: translateX(-3px);
  color: var(--navy);
}
.back-icon {
  width: 14px;
  height: 14px;
}
.empty {
  text-align: center;
  color: var(--text-mute);
  padding: 60px 0;
}
.banner {
  position: relative;
  aspect-ratio: 21 / 7;
  border-radius: 16px;
  background: linear-gradient(135deg, #0b1f3a, #133a5e 60%, #0f766e);
  display: grid;
  place-items: center;
  overflow: hidden;
}
.banner-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.b-icon {
  position: absolute;
  filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.4));
  user-select: none;
  pointer-events: none;
}
.b-icon.main {
  font-size: 4.5rem;
  right: 60px;
  top: 50%;
  transform: translateY(-55%);
}
.b-icon.sub1 {
  font-size: 2.6rem;
  right: 160px;
  top: 16px;
  opacity: 0.8;
}
.b-icon.sub2 {
  font-size: 2.2rem;
  right: 40px;
  bottom: 16px;
  opacity: 0.7;
}
.dday {
  position: absolute;
  top: 14px;
  left: 14px;
  font-size: 0.8rem;
  font-weight: 800;
  color: #fff;
  background: #2563eb;
  padding: 5px 12px;
  border-radius: 8px;
}
.dday.urgent {
  background: #dc2626;
}
.head {
  margin: 22px 0;
}
.status {
  font-size: 0.74rem;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 999px;
  color: #fff;
}
.status.open { background: var(--green); }
.status.closed { background: #d97706; }
.status.ended { background: #6b7280; }
.head h1 {
  font-size: 1.6rem;
  font-weight: 800;
  letter-spacing: -0.5px;
  margin: 12px 0 10px;
  line-height: 1.35;
}
.summary {
  color: var(--text-sub);
  font-size: 0.95rem;
}
.scrap {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-top: 16px;
  background: var(--bg);
  border: 1px solid var(--line);
  border-radius: 999px;
  padding: 10px 22px;
  font-size: 0.88rem;
  font-weight: 700;
  color: var(--text-sub);
  cursor: pointer;
  transition: all 0.2s ease;
}
.scrap:hover {
  border-color: var(--teal);
  background-color: #f0faf8;
}
.scrap.on {
  background: #e6f4f1;
  border-color: var(--teal);
  color: var(--teal);
}
.bookmark-icon {
  width: 18px;
  height: 18px;
  transition: transform 0.2s ease, fill 0.2s ease, stroke 0.2s ease;
  fill: transparent;
  stroke: var(--text-sub);
}
.scrap:hover .bookmark-icon {
  stroke: var(--teal);
}
.scrap.on .bookmark-icon {
  fill: var(--teal);
  stroke: var(--teal);
  animation: scrap-pop 0.4s ease;
}
@keyframes scrap-pop {
  0% { transform: scale(1); }
  50% { transform: scale(1.3); }
  100% { transform: scale(1); }
}
.info {
  margin: 0 0 26px;
  border: 1px solid var(--line);
  border-radius: 14px;
  overflow: hidden;
}
.info > div {
  display: grid;
  grid-template-columns: 120px 1fr;
  border-bottom: 1px solid var(--line);
}
.info > div:last-child {
  border-bottom: none;
}
.info dt {
  background: var(--bg);
  padding: 13px 16px;
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--text-sub);
}
.info dd {
  margin: 0;
  padding: 13px 16px;
  font-size: 0.9rem;
}
.body-sec,
.map-sec {
  margin-bottom: 28px;
}
.body-sec h2,
.map-sec h2 {
  font-size: 1.1rem;
  font-weight: 800;
  margin-bottom: 14px;
}
.body {
  font-size: 0.95rem;
  line-height: 1.75;
  color: var(--text-sub);
  white-space: pre-wrap;
}
.map {
  width: 100%;
  height: 340px;
  border-radius: 14px;
  border: 1px solid var(--line);
  background: var(--bg);
}
.map :deep(img) {
  max-width: none !important;
  max-height: none !important;
}
.map-msg {
  margin-top: 12px;
  font-size: 0.84rem;
  color: var(--text-sub);
  line-height: 1.6;
  background: var(--bg);
  border: 1px dashed var(--line);
  border-radius: 10px;
  padding: 14px;
}
.map-msg code {
  background: #fff;
  border: 1px solid var(--line);
  border-radius: 5px;
  padding: 1px 6px;
  font-size: 0.8rem;
}
.addr {
  margin-top: 12px;
  font-size: 0.88rem;
  color: var(--text-sub);
}
.online-note,
.no-map-note {
  background: var(--bg);
  border-radius: 12px;
  padding: 28px;
  text-align: center;
  font-size: 0.95rem;
  color: var(--text-sub);
}
.block {
  width: 100%;
}
</style>
