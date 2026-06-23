<script setup>
import { ref } from 'vue'

const quiz = {
  q: '금리가 오르면 일반적으로 채권 가격은?',
  options: ['올라간다', '내려간다'],
  answer: 1,
}
const picked = ref(null)
const done = ref(false)

function choose(i) {
  if (done.value) return
  picked.value = i
  done.value = true
}
</script>

<template>
  <div class="widget">
    <div class="head">
      <span class="ico">💡</span>
      <strong>오늘의 퀴즈</strong>
    </div>
    <p class="q">{{ quiz.q }}</p>
    <div class="opts">
      <button
        v-for="(o, i) in quiz.options"
        :key="i"
        class="opt"
        :class="done && {
          right: i === quiz.answer,
          wrong: picked === i && i !== quiz.answer,
        }"
        @click="choose(i)"
      >
        {{ o }}
      </button>
    </div>
    <p v-if="done" class="result">
      {{ picked === quiz.answer ? '정답이에요! +10P 🎉' : '아쉬워요, 정답은 ' + quiz.options[quiz.answer] }}
    </p>
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
.q {
  font-size: 0.86rem;
  line-height: 1.45;
  color: var(--text);
  margin-bottom: 12px;
}
.opts {
  display: flex;
  gap: 8px;
}
.opt {
  flex: 1;
  background: var(--bg);
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  padding: 10px;
  font-size: 0.84rem;
  font-weight: 600;
  color: var(--text-sub);
}
.opt:hover {
  border-color: var(--navy);
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
  font-weight: 600;
  color: var(--navy);
  text-align: center;
}
</style>
