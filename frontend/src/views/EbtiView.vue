<script setup>
import { computed, ref } from 'vue'
import { RouterLink } from 'vue-router'

/**
 * 경제 EBTI 테스트
 * 5개 축(소비 관리·자산 관리·변화 대응·위기 관리·노후 대비)을 측정한다.
 * 문항은 아래 배열만 교체하면 되도록 데이터 주도로 구성했다.
 * 각 보기의 strong: true 는 해당 축의 '강점' 응답.
 */
const dimensions = {
  spend: '소비 관리',
  asset: '자산 관리',
  change: '변화 대응',
  risk: '위기 관리',
  retire: '노후 대비',
}

const questions = [
  {
    dim: 'spend',
    text: '이번 달 카드값이 대략 얼마인지 알고 있나요?',
    options: [
      { label: '정확히 파악하고 있다', strong: true },
      { label: '잘 모르겠다', strong: false },
    ],
  },
  {
    dim: 'spend',
    text: '갖고 싶은 물건이 생기면 보통?',
    options: [
      { label: '예산을 따져보고 결정한다', strong: true },
      { label: '일단 지르고 본다', strong: false },
    ],
  },
  {
    dim: 'asset',
    text: '내 예적금·투자 현황을 얼마나 챙기나요?',
    options: [
      { label: '정기적으로 점검한다', strong: true },
      { label: '거의 신경 쓰지 않는다', strong: false },
    ],
  },
  {
    dim: 'asset',
    text: '여윳돈이 생기면?',
    options: [
      { label: '저축·투자 계획을 세운다', strong: true },
      { label: '통장에 그냥 둔다', strong: false },
    ],
  },
  {
    dim: 'change',
    text: '새로운 금융 상품이나 제도가 나오면?',
    options: [
      { label: '찾아보고 활용한다', strong: true },
      { label: '딱히 관심 없다', strong: false },
    ],
  },
  {
    dim: 'change',
    text: '금리가 크게 바뀌면 내 자산 계획은?',
    options: [
      { label: '상황에 맞춰 조정한다', strong: true },
      { label: '그대로 둔다', strong: false },
    ],
  },
  {
    dim: 'risk',
    text: '갑자기 큰돈이 필요해진다면?',
    options: [
      { label: '비상금으로 대비돼 있다', strong: true },
      { label: '막막할 것 같다', strong: false },
    ],
  },
  {
    dim: 'risk',
    text: '보험·안전장치에 대해 생각해보면?',
    options: [
      { label: '최소한은 준비해 두었다', strong: true },
      { label: '거의 준비가 없다', strong: false },
    ],
  },
  {
    dim: 'retire',
    text: '은퇴 후 자금에 대한 계획이 있나요?',
    options: [
      { label: '조금씩 준비하고 있다', strong: true },
      { label: '아직 생각해보지 못했다', strong: false },
    ],
  },
  {
    dim: 'retire',
    text: '연금이나 장기 저축은?',
    options: [
      { label: '이미 실천하고 있다', strong: true },
      { label: '생각만 하고 있다', strong: false },
    ],
  },
]

// 강점 개수(0~5)에 따른 페르소나
const personas = [
  { emoji: '🌱', name: '금융 새싹', desc: '이제 막 첫걸음을 뗀 단계예요. 작은 습관부터 시작해볼까요?' },
  { emoji: '🧭', name: '금융 탐색가', desc: '관심은 충분해요. 방향만 잡으면 빠르게 성장할 타입!' },
  { emoji: '🚶', name: '금융 실천러', desc: '기본기를 갖춰가는 중. 꾸준함이 무기가 될 거예요.' },
  { emoji: '📈', name: '금융 성장러', desc: '제법 탄탄해요. 부족한 축만 보완하면 상위권!' },
  { emoji: '♟️', name: '금융 전략가', desc: '대부분의 영역을 챙기는 전략가. 디테일만 다듬으면 완성형.' },
  { emoji: '👑', name: '금융 마스터', desc: '5개 영역을 모두 갖춘 진정한 경제 고수! 멋져요.' },
]

const STEP = { INTRO: 'intro', QUIZ: 'quiz', RESULT: 'result' }
const step = ref(STEP.INTRO)
const current = ref(0)
const answers = ref([]) // 각 문항의 strong 여부 저장

const progress = computed(() =>
  Math.round((current.value / questions.length) * 100)
)

function start() {
  step.value = STEP.QUIZ
  current.value = 0
  answers.value = []
}

function choose(option) {
  answers.value[current.value] = option.strong
  if (current.value < questions.length - 1) {
    current.value++
  } else {
    finish()
  }
}

function prev() {
  if (current.value > 0) current.value--
}

// 축별 강점 점수 집계
const scores = ref({})
const result = ref(null)

function finish() {
  const tally = { spend: 0, asset: 0, change: 0, risk: 0, retire: 0 }
  const max = { spend: 0, asset: 0, change: 0, risk: 0, retire: 0 }
  questions.forEach((q, i) => {
    max[q.dim]++
    if (answers.value[i]) tally[q.dim]++
  })
  // 축별 강점 여부(O/X): 강점 응답이 절반 이상이면 O
  const strongDims = Object.keys(tally).filter(
    (d) => tally[d] / max[d] >= 0.5
  )
  scores.value = Object.fromEntries(
    Object.keys(tally).map((d) => [d, { got: tally[d], total: max[d] }])
  )
  result.value = {
    strongCount: strongDims.length,
    strongDims,
    persona: personas[strongDims.length],
  }
  // 결과를 로컬에 저장 (기획서: EBTI 결과는 로컬스토리지 처리)
  localStorage.setItem('ebtiResult', JSON.stringify(result.value))
  step.value = STEP.RESULT
}

function restart() {
  step.value = STEP.INTRO
  result.value = null
}
</script>

<template>
  <main class="ebti">
    <div class="container narrow">
      <!-- 인트로 -->
      <section v-if="step === STEP.INTRO" class="intro card">
        <span class="badge">경제 성향 테스트</span>
        <h1>나의 경제 EBTI는?</h1>
        <p class="lead">
          10개의 질문으로 알아보는 나의 금융 성향.<br />
          소비·자산·변화·위기·노후 5가지 영역을 진단해드려요.
        </p>
        <div class="dims">
          <span v-for="(label, key) in dimensions" :key="key" class="dim-chip">
            {{ label }}
          </span>
        </div>
        <button class="btn btn-navy big" @click="start">테스트 시작하기 →</button>
        <p class="time">⏱ 약 1분 소요 · 10문항</p>
      </section>

      <!-- 문항 -->
      <section v-else-if="step === STEP.QUIZ" class="quiz card">
        <div class="bar">
          <div class="bar-fill" :style="{ width: progress + '%' }"></div>
        </div>
        <div class="q-top">
          <span class="q-dim">{{ dimensions[questions[current].dim] }}</span>
          <span class="q-count">{{ current + 1 }} / {{ questions.length }}</span>
        </div>
        <h2 class="q-text">{{ questions[current].text }}</h2>
        <div class="options">
          <button
            v-for="(o, i) in questions[current].options"
            :key="i"
            class="opt"
            @click="choose(o)"
          >
            {{ o.label }}
          </button>
        </div>
        <button v-if="current > 0" class="back" @click="prev">← 이전 질문</button>
      </section>

      <!-- 결과 -->
      <section v-else class="result card">
        <span class="badge">테스트 결과</span>
        <div class="persona">
          <span class="p-emoji">{{ result.persona.emoji }}</span>
          <h1>{{ result.persona.name }}</h1>
          <p class="p-desc">{{ result.persona.desc }}</p>
          <span class="p-score">강점 영역 {{ result.strongCount }} / 5</span>
        </div>

        <div class="breakdown">
          <div v-for="(label, key) in dimensions" :key="key" class="row">
            <span class="r-label">
              {{ result.strongDims.includes(key) ? '✅' : '⬜' }} {{ label }}
            </span>
            <div class="r-bar">
              <div
                class="r-fill"
                :class="{ strong: result.strongDims.includes(key) }"
                :style="{ width: (scores[key].got / scores[key].total) * 100 + '%' }"
              ></div>
            </div>
          </div>
        </div>

        <div class="actions">
          <RouterLink to="/" class="btn btn-navy">맞춤 콘텐츠 보러가기 →</RouterLink>
          <button class="btn btn-outline" @click="restart">다시 테스트하기</button>
        </div>
      </section>
    </div>
  </main>
</template>

<style scoped>
.ebti {
  padding: 48px 0 30px;
  min-height: 72vh;
}
.narrow {
  max-width: 600px;
}
.card {
  background: #fff;
  border: 1px solid var(--line);
  border-radius: 20px;
  padding: 40px 36px;
  box-shadow: var(--shadow);
}
.badge {
  display: inline-block;
  font-size: 0.78rem;
  font-weight: 700;
  color: var(--teal);
  background: #e6f4f1;
  padding: 5px 12px;
  border-radius: 999px;
}

/* 인트로 */
.intro {
  text-align: center;
}
.intro h1 {
  font-size: 1.8rem;
  font-weight: 800;
  letter-spacing: -0.6px;
  margin: 16px 0 12px;
}
.lead {
  color: var(--text-sub);
  font-size: 0.94rem;
  line-height: 1.6;
}
.dims {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 8px;
  margin: 24px 0;
}
.dim-chip {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--navy);
  background: var(--bg);
  border: 1px solid var(--line);
  border-radius: 999px;
  padding: 7px 14px;
}
.btn.big {
  padding: 14px 28px;
  font-size: 1rem;
}
.time {
  margin-top: 14px;
  font-size: 0.8rem;
  color: var(--text-mute);
}

/* 문항 */
.bar {
  height: 7px;
  background: var(--bg);
  border-radius: 999px;
  overflow: hidden;
  margin-bottom: 24px;
}
.bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--teal), var(--green));
  border-radius: 999px;
  transition: width 0.3s ease;
}
.q-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}
.q-dim {
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--teal);
  background: #e6f4f1;
  padding: 4px 10px;
  border-radius: 999px;
}
.q-count {
  font-size: 0.82rem;
  color: var(--text-mute);
  font-weight: 600;
}
.q-text {
  font-size: 1.3rem;
  font-weight: 800;
  line-height: 1.45;
  letter-spacing: -0.4px;
  margin-bottom: 28px;
}
.options {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.opt {
  background: #fff;
  border: 1.5px solid var(--line);
  border-radius: 14px;
  padding: 18px 20px;
  font-size: 0.98rem;
  font-weight: 600;
  color: var(--text);
  text-align: left;
  transition: all 0.14s;
}
.opt:hover {
  border-color: var(--navy);
  background: #f7f9ff;
  transform: translateY(-2px);
}
.back {
  margin-top: 20px;
  background: transparent;
  color: var(--text-mute);
  font-size: 0.85rem;
}
.back:hover {
  color: var(--navy);
}

/* 결과 */
.result {
  text-align: center;
}
.persona {
  margin: 10px 0 28px;
}
.p-emoji {
  font-size: 3.6rem;
  display: block;
}
.persona h1 {
  font-size: 1.8rem;
  font-weight: 800;
  margin: 10px 0 8px;
}
.p-desc {
  color: var(--text-sub);
  font-size: 0.92rem;
  line-height: 1.55;
  max-width: 380px;
  margin: 0 auto 14px;
}
.p-score {
  display: inline-block;
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--navy);
  background: var(--bg);
  padding: 6px 14px;
  border-radius: 999px;
}
.breakdown {
  text-align: left;
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin: 8px 0 30px;
  padding: 22px;
  background: var(--bg);
  border-radius: 14px;
}
.row {
  display: grid;
  grid-template-columns: 120px 1fr;
  align-items: center;
  gap: 12px;
}
.r-label {
  font-size: 0.86rem;
  font-weight: 600;
}
.r-bar {
  height: 9px;
  background: #fff;
  border-radius: 999px;
  overflow: hidden;
  border: 1px solid var(--line);
}
.r-fill {
  height: 100%;
  background: var(--text-mute);
  border-radius: 999px;
  transition: width 0.5s ease;
}
.r-fill.strong {
  background: linear-gradient(90deg, var(--teal), var(--green));
}
.actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
@media (max-width: 560px) {
  .card {
    padding: 30px 22px;
  }
  .row {
    grid-template-columns: 96px 1fr;
  }
}
</style>
