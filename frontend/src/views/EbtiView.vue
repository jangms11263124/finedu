<script setup>
import { computed, ref } from 'vue'
import { RouterLink } from 'vue-router'
import {
  SCALE,
  THEME_MIN,
  THEME_MAX,
  STRONG_RATIO,
  themes,
  personaFor,
} from '@/data/ebti'

/**
 * 경제 EBTI 테스트 (기획재정부 경제배움e+ 진단 기반)
 * 5개 역량(소비·자산·변화·위기·노후) × 3문항, 5점 척도.
 * 데이터는 src/data/ebti.js 참고.
 */

// 모든 문항을 (주제 + 문항)으로 평탄화
const questions = themes.flatMap((t) =>
  t.questions.map((text) => ({ themeKey: t.key, themeName: t.name, text }))
)
const themeMap = Object.fromEntries(themes.map((t) => [t.key, t]))

const STEP = { INTRO: 'intro', QUIZ: 'quiz', RESULT: 'result' }
const step = ref(STEP.INTRO)
const current = ref(0)
const answers = ref([]) // 각 문항의 선택 점수 저장

const progress = computed(() =>
  Math.round((current.value / questions.length) * 100)
)

const result = ref(null)

function start() {
  step.value = STEP.QUIZ
  current.value = 0
  answers.value = []
}

function choose(option) {
  answers.value[current.value] = option.score
  if (current.value < questions.length - 1) {
    current.value++
  } else {
    finish()
  }
}

function prev() {
  if (current.value > 0) current.value--
}

function finish() {
  // 주제별 점수 집계
  const totals = Object.fromEntries(themes.map((t) => [t.key, 0]))
  questions.forEach((q, i) => {
    totals[q.themeKey] += answers.value[i] ?? 0
  })

  const threshold = THEME_MIN + (THEME_MAX - THEME_MIN) * STRONG_RATIO
  const breakdown = themes.map((t) => {
    const score = totals[t.key]
    const strong = score >= threshold
    return {
      key: t.key,
      name: t.name,
      score,
      ratio: (score - THEME_MIN) / (THEME_MAX - THEME_MIN),
      strong,
      feedback: strong ? t.strong : t.weak,
      tags: strong ? [] : t.tags, // 보완 영역에만 추천 태그 노출 (원본과 동일)
    }
  })

  const strongCount = breakdown.filter((b) => b.strong).length
  result.value = {
    breakdown,
    strongCount,
    persona: personaFor(strongCount),
  }
  // 기획서: EBTI 결과는 로컬스토리지에 저장
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
        <span class="badge">경제 습관 진단</span>
        <h1>나의 경제 EBTI는?</h1>
        <p class="lead">
          {{ questions.length }}개의 질문으로 알아보는 나의 경제 습관.<br />
          소비·자산·변화·위기·노후 5가지 역량을 진단해드려요.
        </p>
        <p class="src">
          ※ 기획재정부 경제배움e+ ‘나의 경제 습관 테스트’ 기반
        </p>
        <div class="dims">
          <span v-for="t in themes" :key="t.key" class="dim-chip">
            {{ t.name }}
          </span>
        </div>
        <button class="btn btn-navy big" @click="start">진단 시작하기 →</button>
        <p class="time">⏱ 약 2분 소요 · {{ questions.length }}문항</p>
      </section>

      <!-- 문항 -->
      <section v-else-if="step === STEP.QUIZ" class="quiz card">
        <div class="bar">
          <div class="bar-fill" :style="{ width: progress + '%' }"></div>
        </div>
        <div class="q-top">
          <span class="q-dim">{{ questions[current].themeName }}</span>
          <span class="q-count">{{ current + 1 }} / {{ questions.length }}</span>
        </div>
        <h2 class="q-text">{{ questions[current].text }}</h2>
        <div class="options scale">
          <button
            v-for="(o, i) in SCALE"
            :key="i"
            class="opt"
            :class="{ on: answers[current] === o.score }"
            @click="choose(o)"
          >
            {{ o.label }}
          </button>
        </div>
        <button v-if="current > 0" class="back" @click="prev">← 이전 질문</button>
      </section>

      <!-- 결과 -->
      <section v-else class="result card">
        <span class="badge">경제 EBTI 진단 결과</span>
        <div class="persona">
          <span class="p-emoji">{{ result.persona.emoji }}</span>
          <h1 class="p-name">{{ result.persona.name }}</h1>
          <p class="p-desc">{{ result.persona.desc }}</p>
          <span class="p-score">강점 영역 {{ result.strongCount }} / 5</span>
        </div>

        <!-- 역량별 점수 막대 -->
        <div class="breakdown">
          <div v-for="b in result.breakdown" :key="b.key" class="row">
            <span class="r-label">
              {{ b.strong ? '✅' : '✏️' }} {{ b.name }}
            </span>
            <div class="r-bar">
              <div
                class="r-fill"
                :class="{ strong: b.strong }"
                :style="{ width: Math.max(b.ratio * 100, 4) + '%' }"
              ></div>
            </div>
            <span class="r-score">{{ b.score }}점</span>
          </div>
        </div>

        <!-- 역량별 상세 피드백 -->
        <div class="details">
          <article v-for="b in result.breakdown" :key="b.key" class="detail">
            <h3 class="d-head" :class="b.strong ? 'good' : 'todo'">
              {{ b.name }} - {{ b.strong ? '좋아요!' : '함께 공부해요!' }}
            </h3>
            <p class="d-desc">{{ themeMap[b.key].desc }}</p>
            <p class="d-fb">{{ b.feedback }}</p>
            <div v-if="b.tags.length" class="d-tags">
              <RouterLink
                v-for="tag in b.tags"
                :key="tag"
                :to="`/contents?q=${tag}`"
                class="tag"
              >#{{ tag }}</RouterLink>
            </div>
          </article>
        </div>

        <div class="actions">
          <RouterLink to="/contents" class="btn btn-navy">맞춤 콘텐츠 보러가기 →</RouterLink>
          <button class="btn btn-outline" @click="restart">다시 진단하기</button>
        </div>
      </section>
    </div>
  </main>
</template>

<style scoped>
.ebti {
  padding: 48px 0 40px;
  min-height: 72vh;
}
.narrow {
  max-width: 640px;
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
.src {
  margin-top: 8px;
  font-size: 0.76rem;
  color: var(--text-mute);
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
  padding: 16px 20px;
  font-size: 0.98rem;
  font-weight: 600;
  color: var(--text);
  text-align: center;
  transition: all 0.14s;
}
.opt:hover {
  border-color: var(--navy);
  background: #f7f9ff;
  transform: translateY(-2px);
}
.opt.on {
  border-color: var(--navy);
  background: var(--navy);
  color: #fff;
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
.p-name {
  font-size: 1.7rem;
  font-weight: 800;
  margin: 10px 0 10px;
  line-height: 1.3;
  white-space: pre-line;
}
.p-desc {
  color: var(--text-sub);
  font-size: 0.92rem;
  line-height: 1.6;
  max-width: 440px;
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
  margin: 8px 0 26px;
  padding: 22px;
  background: var(--bg);
  border-radius: 14px;
}
.row {
  display: grid;
  grid-template-columns: 130px 1fr 44px;
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
.r-score {
  font-size: 0.78rem;
  color: var(--text-mute);
  font-weight: 700;
  text-align: right;
}

/* 역량별 상세 */
.details {
  text-align: left;
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-bottom: 28px;
}
.detail {
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 18px 20px;
}
.d-head {
  display: inline-block;
  font-size: 0.92rem;
  font-weight: 800;
  color: #fff;
  padding: 6px 14px;
  border-radius: 999px;
  margin-bottom: 12px;
}
.d-head.good {
  background: linear-gradient(90deg, var(--teal), var(--green));
}
.d-head.todo {
  background: linear-gradient(90deg, #ec4899, #f43f5e);
}
.d-desc {
  font-size: 0.82rem;
  color: var(--text-mute);
  line-height: 1.55;
  margin-bottom: 8px;
}
.d-fb {
  font-size: 0.88rem;
  color: var(--text);
  line-height: 1.65;
}
.d-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 12px;
}
.tag {
  font-size: 0.76rem;
  font-weight: 600;
  color: var(--navy);
  background: var(--bg);
  border: 1px solid var(--line);
  border-radius: 999px;
  padding: 5px 11px;
}
.tag:hover {
  border-color: var(--navy);
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
    grid-template-columns: 96px 1fr 40px;
  }
}
</style>
