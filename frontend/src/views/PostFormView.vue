<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import api from '@/api'

const route = useRoute()
const router = useRouter()

const isEdit = computed(() => !!route.params.id)

const boards = [
  { key: 'free', label: '자유게시판' },
  { key: 'info', label: '정보공유' },
  { key: 'qna', label: '질문답변' },
]

const form = ref({ board: 'free', title: '', content: '' })
const error = ref('')
const saving = ref(false)

onMounted(async () => {
  if (isEdit.value) {
    try {
      const { data } = await api.get(`/posts/${route.params.id}/`)
      form.value = { board: data.board, title: data.title, content: data.content }
    } catch {
      alert('게시글을 불러올 수 없습니다.')
      router.push('/community')
    }
  }
})

async function submit() {
  error.value = ''
  if (!form.value.title.trim() || !form.value.content.trim()) {
    error.value = '제목과 내용을 모두 입력해주세요.'
    return
  }
  saving.value = true
  try {
    if (isEdit.value) {
      await api.put(`/posts/${route.params.id}/`, form.value)
      router.push(`/community/${route.params.id}`)
    } else {
      const { data } = await api.post('/posts/', form.value)
      router.push(`/community/${data.id}`)
    }
  } catch (e) {
    error.value = e.response?.data
      ? Object.values(e.response.data).flat().join(' ')
      : '저장에 실패했습니다.'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <main class="form-page">
    <div class="container narrow">
      <RouterLink to="/community" class="back">‹ 목록으로</RouterLink>

      <div class="card">
        <h1>{{ isEdit ? '글 수정' : '글쓰기' }}</h1>

        <form @submit.prevent="submit">
          <label>게시판</label>
          <div class="board-pick">
            <button
              v-for="b in boards"
              :key="b.key"
              type="button"
              class="chip"
              :class="{ on: form.board === b.key }"
              @click="form.board = b.key"
            >
              {{ b.label }}
            </button>
          </div>

          <label>제목</label>
          <input v-model="form.title" placeholder="제목을 입력하세요" maxlength="200" />

          <label>내용</label>
          <textarea
            v-model="form.content"
            rows="12"
            placeholder="내용을 입력하세요"
          ></textarea>

          <p v-if="error" class="err">{{ error }}</p>

          <div class="actions">
            <RouterLink to="/community" class="btn btn-outline">취소</RouterLink>
            <button class="btn btn-navy" type="submit" :disabled="saving">
              {{ saving ? '저장 중...' : isEdit ? '수정하기' : '등록하기' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </main>
</template>

<style scoped>
.form-page {
  padding: 30px 0 24px;
  min-height: 70vh;
}
.narrow {
  max-width: 720px;
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
.card {
  background: #fff;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 30px;
  box-shadow: var(--shadow);
}
.card h1 {
  font-size: 1.4rem;
  font-weight: 800;
  margin-bottom: 22px;
}
form {
  display: flex;
  flex-direction: column;
}
label {
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--text-sub);
  margin: 16px 0 8px;
}
label:first-of-type {
  margin-top: 0;
}
.board-pick {
  display: flex;
  gap: 6px;
}
.chip {
  background: #fff;
  border: 1px solid var(--line);
  border-radius: 999px;
  padding: 8px 16px;
  font-size: 0.84rem;
  font-weight: 600;
  color: var(--text-sub);
}
.chip.on {
  background: var(--navy);
  color: #fff;
  border-color: var(--navy);
}
input,
textarea {
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  padding: 13px 14px;
  font-size: 0.92rem;
  outline: none;
  font-family: inherit;
}
input:focus,
textarea:focus {
  border-color: var(--navy);
}
textarea {
  resize: vertical;
  line-height: 1.6;
}
.err {
  color: #dc2626;
  font-size: 0.82rem;
  margin-top: 12px;
}
.actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 24px;
}
</style>
