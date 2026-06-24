<script setup>
import { nextTick, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import api from '@/api'
import { hasKakaoKey, loadKakao } from '@/utils/kakaoMap'

const route = useRoute()
const router = useRouter()

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
    loading.value = false
    await nextTick()
    if (data.latitude && data.longitude) initMap(data)
  } catch {
    alert('행사를 찾을 수 없습니다.')
    router.push('/events')
  } finally {
    loading.value = false
  }
}

async function initMap(e) {
  mapError.value = ''
  if (!hasKakaoKey()) {
    mapError.value = 'NO_KEY'
    return
  }
  try {
    const kakao = await loadKakao()
    const center = new kakao.maps.LatLng(e.latitude, e.longitude)
    const map = new kakao.maps.Map(mapEl.value, { center, level: 4 })
    const marker = new kakao.maps.Marker({ position: center })
    marker.setMap(map)
    // 장소명 말풍선
    const iw = new kakao.maps.InfoWindow({
      content:
        `<div style="padding:6px 10px;font-size:12px;font-weight:600;white-space:nowrap">`
        + (e.place_name || e.region) + `</div>`,
    })
    iw.open(map, marker)
  } catch (err) {
    mapError.value = err.message === 'NO_KEY' ? 'NO_KEY' : 'LOAD_FAILED'
  }
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
      <RouterLink to="/events" class="back">‹ 행사 목록</RouterLink>

      <p v-if="loading" class="empty">불러오는 중...</p>

      <template v-else-if="event">
        <!-- 헤더 배너 -->
        <div class="banner">
          <span class="emoji">🎓</span>
          <span class="dday" :class="{ urgent: event.d_day !== null && event.d_day <= 2 }">
            {{ ddayLabel(event) }}
          </span>
        </div>

        <div class="head">
          <span class="status" :class="event.status">{{ event.status_display }}</span>
          <h1>{{ event.title }}</h1>
          <p class="summary">{{ event.summary }}</p>
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

          <template v-if="event.latitude && event.longitude">
            <div ref="mapEl" class="map"></div>
            <p v-if="mapError === 'NO_KEY'" class="map-msg">
              🗺️ 카카오맵 키가 설정되지 않았습니다.
              <code>frontend/.env</code>의 <code>VITE_KAKAO_MAP_KEY</code>에
              키를 넣으면 지도가 표시됩니다.
            </p>
            <p v-else-if="mapError === 'LOAD_FAILED'" class="map-msg">
              지도를 불러오지 못했습니다. 키와 사이트 도메인 등록을 확인해주세요.
            </p>
            <p v-else class="addr">📍 {{ event.place_name }} · {{ event.address }}</p>
          </template>

          <p v-else class="online-note">💻 온라인으로 진행되는 행사입니다.</p>
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
  max-width: 760px;
}
.back {
  display: inline-block;
  margin-bottom: 16px;
  font-size: 0.86rem;
  color: var(--text-sub);
}
.back:hover {
  color: var(--navy);
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
.banner .emoji {
  font-size: 3.4rem;
  filter: drop-shadow(0 4px 10px rgba(0, 0, 0, 0.4));
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
.online-note {
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
