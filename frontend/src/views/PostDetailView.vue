<script setup>
import { computed, onMounted, provide, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import api from '@/api'
import { useAuthStore } from '@/stores/auth'
import CommentItem from '@/components/community/CommentItem.vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const post = ref(null)
const loading = ref(true)
const newComment = ref('')

const isAuthor = computed(
  () => post.value && auth.user && post.value.author_id === auth.user.id
)

// 대댓글 추가/삭제 시 전체 댓글 수를 조정
provide('bumpCommentCount', (delta) => {
  if (post.value) post.value.comment_count += delta
})

async function load() {
  loading.value = true
  try {
    const { data } = await api.get(`/posts/${route.params.id}/`)
    post.value = data
  } catch {
    alert('게시글을 찾을 수 없습니다.')
    router.push('/community')
  } finally {
    loading.value = false
  }
}

async function togglePostLike() {
  if (!auth.isLoggedIn) {
    if (confirm('로그인이 필요합니다. 로그인 페이지로 이동하시겠습니까?')) {
      router.push({ name: 'login', query: { redirect: route.fullPath } })
    }
    return
  }
  const { data } = await api.post(`/posts/${post.value.id}/like/`)
  post.value.is_liked = data.liked
  post.value.like_count = data.like_count
}

async function removePost() {
  if (!confirm('이 게시글을 삭제할까요?')) return
  await api.delete(`/posts/${post.value.id}/`)
  router.push('/community')
}

async function addComment() {
  if (!newComment.value.trim()) return
  const { data } = await api.post('/comments/', {
    post: post.value.id,
    content: newComment.value.trim(),
  })
  post.value.comments.push(data)
  post.value.comment_count++
  newComment.value = ''
}

function onTopDeleted(id) {
  post.value.comments = post.value.comments.filter((c) => c.id !== id)
}

function fmt(dt) {
  return new Date(dt).toLocaleString('ko-KR', {
    year: '2-digit',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

onMounted(load)
</script>

<template>
  <main class="detail">
    <div class="container narrow">
      <RouterLink to="/community" class="back">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" class="back-icon">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5" />
        </svg>
        <span>목록으로</span>
      </RouterLink>

      <p v-if="loading" class="empty">불러오는 중...</p>

      <template v-else-if="post">
        <article class="post card">
          <span class="board">{{ post.board_display }}</span>
          <h1>{{ post.title }}</h1>
          <div class="meta">
            <span>
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="meta-icon"><path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.501 20.118a7.5 7.5 0 0 1 14.998 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.499-1.632Z" /></svg>
              {{ post.author }}
            </span>
            <span>
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="meta-icon"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" /></svg>
              {{ fmt(post.created_at) }}
            </span>
            <span>
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="meta-icon"><path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z" /><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" /></svg>
              조회 {{ post.views.toLocaleString() }}
            </span>
          </div>
          <div v-if="post.image" class="post-image">
            <img :src="post.image" alt="첨부 이미지" />
          </div>
          <div class="body">{{ post.content }}</div>

          <div class="post-foot">
            <button
              class="post-like"
              :class="{ on: post.is_liked }"
              @click="togglePostLike"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke-width="2"
                stroke="currentColor"
                class="heart-icon"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12Z"
                />
              </svg>
              <span>좋아요 {{ post.like_count }}</span>
            </button>

            <div v-if="isAuthor" class="owner-actions">
              <RouterLink :to="`/community/${post.id}/edit`" class="btn btn-outline sm">
                수정
              </RouterLink>
              <button class="btn btn-outline sm danger" @click="removePost">
                삭제
              </button>
            </div>
          </div>
        </article>

        <!-- 댓글 -->
        <section class="comments card">
          <h2>댓글 <span>{{ post.comment_count }}</span></h2>

          <ul v-if="post.comments.length" class="c-list">
            <CommentItem
              v-for="c in post.comments"
              :key="c.id"
              :comment="c"
              :post-id="post.id"
              @deleted="onTopDeleted"
            />
          </ul>
          <p v-else class="no-comment">첫 댓글을 남겨보세요.</p>

          <form v-if="auth.isLoggedIn" class="c-form" @submit.prevent="addComment">
            <input v-model="newComment" placeholder="댓글을 입력하세요" />
            <button class="btn btn-navy" type="submit">등록</button>
          </form>
          <p v-else class="login-hint">
            댓글을 작성하려면 <RouterLink to="/login">로그인</RouterLink>이 필요해요.
          </p>
        </section>
      </template>
    </div>
  </main>
</template>

<style scoped>
.detail {
  padding: 30px 0 20px;
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
  transition: transform 0.2s ease;
}
.back:hover {
  transform: translateX(-3px);
}
.back-icon {
  width: 14px;
  height: 14px;
}
.empty {
  text-align: center;
  color: var(--text-mute);
  padding: 50px 0;
}
.card {
  background: #fff;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 28px;
  box-shadow: var(--shadow);
}
.post .board {
  font-size: 0.84rem;
  color: var(--text-sub);
  font-weight: 700;
}
.post h1 {
  font-size: 1.5rem;
  font-weight: 800;
  margin: 14px 0 12px;
  letter-spacing: -0.5px;
}
.meta {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 0.8rem;
  color: var(--text-mute);
  padding-bottom: 18px;
  border-bottom: 1px solid var(--line);
}
.meta span {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
.meta-icon {
  width: 14px;
  height: 14px;
  stroke: var(--text-mute);
}
.post-image {
  margin: 16px 0 8px;
  border-radius: var(--radius-sm);
  overflow: hidden;
  max-width: 100%;
}
.post-image img {
  display: block;
  max-width: 100%;
  max-height: 500px;
  object-fit: contain;
  border-radius: var(--radius-sm);
}
.body {
  padding: 22px 2px;
  font-size: 0.95rem;
  line-height: 1.7;
  white-space: pre-wrap;
  min-height: 80px;
}
.post-foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  border-top: 1px solid var(--line);
  padding-top: 16px;
}
.post-like {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: var(--bg);
  border: 1px solid var(--line);
  border-radius: 999px;
  padding: 9px 20px;
  font-size: 0.86rem;
  font-weight: 700;
  color: var(--text-sub);
  cursor: pointer;
  transition: all 0.2s ease;
}
.post-like:hover {
  border-color: #fca5a5;
  background-color: #fff5f5;
}
.post-like.on {
  background: #fee2e2;
  border-color: #fca5a5;
  color: #dc2626;
}
.post-like .heart-icon {
  width: 17px;
  height: 17px;
  transition: transform 0.2s ease, fill 0.2s ease, stroke 0.2s ease;
  fill: transparent;
  stroke: var(--text-sub);
}
.post-like:hover .heart-icon {
  stroke: #dc2626;
}
.post-like.on .heart-icon {
  fill: #dc2626;
  stroke: #dc2626;
  animation: heart-bounce 0.4s ease;
}
@keyframes heart-bounce {
  0% { transform: scale(1); }
  50% { transform: scale(1.35); }
  100% { transform: scale(1); }
}
.owner-actions {
  display: flex;
  gap: 8px;
}
.btn.sm {
  padding: 7px 14px;
  font-size: 0.82rem;
}
.btn.danger:hover {
  border-color: #dc2626;
  color: #dc2626;
}

/* 댓글 */
.comments {
  margin-top: 18px;
}
.comments h2 {
  font-size: 1.05rem;
  font-weight: 800;
  margin-bottom: 16px;
}
.comments h2 span {
  color: var(--teal);
}
.c-list {
  list-style: none;
  margin: 0 0 18px;
  padding: 0;
  display: flex;
  flex-direction: column;
}
.c-list li {
  padding: 14px 0;
  border-bottom: 1px solid var(--line);
}
.c-top {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
}
.c-top strong {
  font-size: 0.88rem;
}
.c-date {
  font-size: 0.74rem;
  color: var(--text-mute);
}
.c-body {
  font-size: 0.9rem;
  line-height: 1.5;
}
.c-actions {
  margin-top: 6px;
  display: flex;
  gap: 12px;
}
.c-actions button {
  background: transparent;
  font-size: 0.76rem;
  color: var(--text-mute);
}
.c-actions button:hover {
  color: var(--navy);
}
.c-edit {
  display: flex;
  gap: 6px;
}
.c-edit input {
  flex: 1;
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  padding: 8px 10px;
  font-size: 0.86rem;
  outline: none;
}
.no-comment {
  color: var(--text-mute);
  font-size: 0.86rem;
  padding: 8px 0 18px;
}
.c-form {
  display: flex;
  gap: 8px;
}
.c-form input {
  flex: 1;
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  padding: 12px 14px;
  font-size: 0.9rem;
  outline: none;
}
.c-form input:focus {
  border-color: var(--navy);
}
.login-hint {
  font-size: 0.84rem;
  color: var(--text-sub);
}
.login-hint a {
  color: var(--navy);
  font-weight: 700;
}
</style>
