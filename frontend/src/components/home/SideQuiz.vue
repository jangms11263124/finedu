<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import api from '@/api'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

const loading = ref(true)
const quiz = ref(null) // { question, options }
const picked = ref(null)
const done = ref(false)
const submitting = ref(false)
const needLogin = ref(false)

const authed = ref(false)
const isCorrect = ref(false)
const answerIndex = ref(null)
const explanation = ref('')
const attendanceStreak = ref(0)
const correctStreak = ref(0)

function apply(data) {
  authed.value = data.authenticated ?? authed.value
  attendanceStreak.value = data.attendance_streak ?? 0
  correctStreak.value = data.correct_streak ?? 0
  if (data.answered) {
    done.value = true
    picked.value = data.selected_index
    isCorrect.value = data.is_correct
    answerIndex.value = data.answer_index
    explanation.value = data.explanation || ''
  }
}

function reset() {
  picked.value = null
  done.value = false
  needLogin.value = false
  isCorrect.value = false
  answerIndex.value = null
  explanation.value = ''
  attendanceStreak.value = 0
  correctStreak.value = 0
}

async function load() {
  loading.value = true
  reset()
  try {
    const { data } = await api.get('/quiz/today/')
    quiz.value = { question: data.question, options: data.options }
    apply(data)
  } catch {
    quiz.value = null
  } finally {
    loading.value = false
  }
}

async function choose(i) {
  if (done.value || submitting.value) return
  picked.value = i
  submitting.value = true
  try {
    const { data } = await api.post('/quiz/today/', { selected_index: i })
    apply(data)
  } catch (e) {
    picked.value = null
    if (e.response?.status === 401) needLogin.value = true
  } finally {
    submitting.value = false
  }
}

const resultText = computed(() => {
  if (!done.value) return ''
  if (isCorrect.value) return '정답이에요! 🎉'
  const ans = quiz.value?.options?.[answerIndex.value]
  return ans ? `아쉬워요, 정답은 "${ans}"` : '아쉬워요!'
})

onMounted(load)

// 로그인/로그아웃 시 위젯을 다시 불러와 내 응답 상태·스트릭을 갱신
watch(() => auth.isLoggedIn, () => load())
</script>

<template>
  <div class="widget">
    <div class="head">
      <span class="ico">💡</span>
      <strong>오늘의 퀴즈</strong>
      <span class="ai-badge">AI</span>
    </div>

    <!-- 출석/정답 스트릭 -->
    <div v-if="authed && (attendanceStreak || correctStreak)" class="streaks">
      <span class="streak">📅 {{ attendanceStreak }}일째 접속 중</span>
      <span v-if="correctStreak" class="streak hot">
        🔥 {{ correctStreak }}일째 정답 중!
      </span>
    </div>

    <div v-if="loading" class="skeleton">오늘의 퀴즈를 불러오는 중…</div>

    <template v-else-if="quiz">
      <p class="q">{{ quiz.question }}</p>
      <div class="opts">
        <button
          v-for="(o, i) in quiz.options"
          :key="i"
          class="opt"
          :disabled="submitting"
          :class="done && {
            right: i === answerIndex,
            wrong: picked === i && i !== answerIndex,
          }"
          @click="choose(i)"
        >
          {{ o }}
        </button>
      </div>

      <p v-if="done" class="result" :class="{ ok: isCorrect }">
        {{ resultText }}
      </p>
      <p v-if="done && explanation" class="explain">{{ explanation }}</p>

      <p v-if="needLogin" class="hint">
        <RouterLink to="/login">로그인</RouterLink>하면 정답 확인과
        출석·연속 정답 기록이 저장돼요.
      </p>
    </template>

    <p v-else class="skeleton">퀴즈를 불러오지 못했어요.</p>
  </div>
</template>

<style scoped>
.widget {
  background: #fff;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 18px;
  box-shadow: var(--shadow);
}
.head {
  display: flex;
  align-items: center;
  gap: 7px;
  margin-bottom: 12px;
}
.head strong {
  font-size: 0.95rem;
}
.ai-badge {
  margin-left: auto;
  font-size: 0.62rem;
  font-weight: 800;
  color: #fff;
  background: linear-gradient(120deg, #4f46e5, #7c3aed);
  padding: 2px 7px;
  border-radius: 6px;
}
.streaks {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 12px;
}
.streak {
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--navy);
  background: #eef2ff;
  border: 1px solid #ddd6fe;
  border-radius: 999px;
  padding: 4px 9px;
}
.streak.hot {
  color: #b45309;
  background: #fff7ed;
  border-color: #fed7aa;
}
.skeleton {
  font-size: 0.82rem;
  color: var(--text-mute);
  padding: 8px 0;
}
.q {
  font-size: 0.86rem;
  line-height: 1.45;
  color: var(--text);
  margin-bottom: 12px;
}
.opts {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.opt {
  flex: 1 1 calc(50% - 4px);
  background: var(--bg);
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  padding: 10px;
  font-size: 0.84rem;
  font-weight: 600;
  color: var(--text-sub);
  cursor: pointer;
}
.opt:hover:not(:disabled) {
  border-color: var(--navy);
}
.opt:disabled {
  cursor: default;
}
.opt.right {
  background: #dcfce7;
  border-color: var(--green);
  color: var(--green-dark);
}
.opt.wrong {
  background: #fee2e2;
  border-color: #dc2626;
  color: #dc2626;
}
.result {
  margin-top: 12px;
  font-size: 0.82rem;
  font-weight: 700;
  color: #dc2626;
  text-align: center;
}
.result.ok {
  color: var(--green-dark);
}
.explain {
  margin-top: 8px;
  font-size: 0.78rem;
  line-height: 1.5;
  color: var(--text-sub);
  background: var(--bg);
  border-radius: var(--radius-sm);
  padding: 9px 11px;
}
.hint {
  margin-top: 10px;
  font-size: 0.78rem;
  color: var(--text-sub);
  text-align: center;
}
.hint a {
  color: var(--navy);
  font-weight: 700;
}
</style>
