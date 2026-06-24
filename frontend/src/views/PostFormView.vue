<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import api from '@/api'

const route = useRoute()
const router = useRouter()

const isEdit = computed(() => !!route.params.id)

const boards = [
  { key: 'free', label: '자유게시판' },
  { key: 'review', label: '후기게시판' },
  { key: 'info', label: '정보게시판' },
  { key: 'qna', label: '질문게시판' },
  { key: 'study', label: '스터디 모집' },
]

const form = ref({ board: 'free', title: '', content: '' })
const error = ref('')
const saving = ref(false)

const imageFile = ref(null)
const imagePreview = ref('')

onMounted(async () => {
  if (isEdit.value) {
    try {
      const { data } = await api.get(`/posts/${route.params.id}/`)
      form.value = { board: data.board, title: data.title, content: data.content }
      if (data.image) {
        imagePreview.value = data.image
      }
    } catch {
      alert('게시글을 불러올 수 없습니다.')
      router.push('/community')
    }
  }
})

function onImageChange(e) {
  const file = e.target.files[0]
  if (file) {
    imageFile.value = file
    imagePreview.value = URL.createObjectURL(file)
  }
}

function removeImage() {
  imageFile.value = null
  imagePreview.value = ''
  const input = document.getElementById('image')
  if (input) input.value = ''
}

async function submit() {
  error.value = ''
  if (!form.value.title.trim() || !form.value.content.trim()) {
    error.value = '제목과 내용을 모두 입력해주세요.'
    return
  }
  saving.value = true
  try {
    const formData = new FormData()
    formData.append('board', form.value.board)
    formData.append('title', form.value.title)
    formData.append('content', form.value.content)
    
    if (imageFile.value) {
      formData.append('image', imageFile.value)
    } else if (!imagePreview.value) {
      formData.append('image', '')
    }

    if (isEdit.value) {
      await api.patch(`/posts/${route.params.id}/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      router.push(`/community/${route.params.id}`)
    } else {
      const { data } = await api.post('/posts/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
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
      <RouterLink to="/community" class="back">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" class="back-icon">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5" />
        </svg>
        <span>목록으로</span>
      </RouterLink>

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

          <label>이미지 첨부 (선택)</label>
          <div class="image-upload">
            <input type="file" id="image" accept="image/*" @change="onImageChange" class="file-input" />
            <label for="image" class="file-label">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.2" stroke="currentColor" class="upload-icon">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 16.5V9.75m0 0l3 3m-3-3l-3 3M6.75 19.5a4.5 4.5 0 01-1.41-8.775 5.25 5.25 0 0110.233-2.33 3 3 0 013.758 3.848A3.752 3.752 0 0118 19.5H6.75z" />
              </svg>
              <span>{{ imagePreview ? '이미지 변경하기' : '이미지 선택하기' }}</span>
            </label>
            <div v-if="imagePreview" class="preview-box">
              <img :src="imagePreview" alt="미리보기" />
              <button type="button" class="remove-image" @click="removeImage">✕ 삭제</button>
            </div>
          </div>

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
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 20px;
  font-size: 0.86rem;
  font-weight: 600;
  color: var(--text-sub);
  text-decoration: none;
  transition: transform 0.2s ease, color 0.2s ease;
}
.back:hover {
  transform: translateX(-3px);
  color: var(--navy);
}
.back-icon {
  width: 14px;
  height: 14px;
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
.image-upload {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.file-input {
  display: none;
}
.file-label {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: #fff;
  border: 1px dashed var(--line);
  border-radius: var(--radius-sm);
  padding: 12px 20px;
  font-size: 0.86rem;
  font-weight: 600;
  color: var(--text-sub);
  cursor: pointer;
  transition: all 0.15s ease;
  width: fit-content;
}
.file-label:hover {
  border-color: var(--navy);
  color: var(--navy);
  background: var(--bg);
}
.upload-icon {
  width: 16px;
  height: 16px;
}
.preview-box {
  position: relative;
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-top: 8px;
  background: var(--bg);
  padding: 12px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--line);
  width: fit-content;
}
.preview-box img {
  display: block;
  max-width: 240px;
  max-height: 180px;
  object-fit: cover;
  border-radius: 6px;
  border: 1px solid var(--line);
}
.remove-image {
  background: #fee2e2;
  color: #dc2626;
  border: 1px solid #fca5a5;
  border-radius: 6px;
  padding: 6px 12px;
  font-size: 0.78rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.15s ease;
}
.remove-image:hover {
  background: #fecaca;
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
