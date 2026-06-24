<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import api from '@/api'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const content = ref(null)
const comments = ref([])
const newComment = ref('')
const loading = ref(true)

const embedUrl = computed(() =>
  content.value?.youtube_id
    ? `https://www.youtube.com/embed/${content.value.youtube_id}`
    : null
)

async function load() {
  loading.value = true
  try {
    const { data } = await api.get(`/contents/${route.params.id}/`)
    content.value = data
    const res = await api.get(`/contents/${route.params.id}/comments/`)
    comments.value = res.data
  } catch {
    alert('콘텐츠를 찾을 수 없습니다.')
    router.push('/contents')
  } finally {
    loading.value = false
  }
}

async function toggleLike() {
  if (!auth.isLoggedIn) {
    if (confirm('로그인이 필요합니다. 로그인 페이지로 이동하시겠습니까?')) {
      router.push({ name: 'login', query: { redirect: route.fullPath } })
    }
    return
  }
  const { data } = await api.post(`/contents/${content.value.id}/like/`)
  content.value.is_liked = data.liked
  content.value.like_count = data.like_count
}

async function addComment() {
  if (!newComment.value.trim()) return
  const { data } = await api.post(`/contents/${content.value.id}/comments/`, {
    body: newComment.value.trim(),
  })
  comments.value.push(data)
  content.value.comment_count++
  newComment.value = ''
}

function fmt(dt) {
  return new Date(dt).toLocaleString('ko-KR', {
    year: '2-digit', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit',
  })
}

function fmtDate(dt) {
  return new Date(dt).toLocaleDateString('ko-KR', {
    year: '2-digit', month: '2-digit', day: '2-digit'
  })
}

watch(() => route.params.id, load)
onMounted(load)
</script>

<template>
  <main class="detail">
    <div class="container narrow">
      <RouterLink to="/contents" class="back">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" class="back-icon">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5" />
        </svg>
        <span>콘텐츠 목록</span>
      </RouterLink>

      <p v-if="loading" class="empty">불러오는 중...</p>

      <template v-else-if="content">
        <!-- 유튜브 영상 -->
        <div class="player">
          <iframe
            v-if="embedUrl"
            :src="embedUrl"
            title="YouTube video player"
            frameborder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
            allowfullscreen
          ></iframe>
          <div v-else class="no-video">영상이 등록되지 않았습니다.</div>
        </div>

        <!-- 정보 -->
        <div class="info">
          <span class="badge">{{ content.category_display }}</span>
          <h1>{{ content.title }}</h1>
          <div class="meta">
            <span>
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="meta-icon"><path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z" /><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" /></svg>
              조회 {{ content.views.toLocaleString() }}
            </span>
            <span>
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="meta-icon"><path stroke-linecap="round" stroke-linejoin="round" d="M12 20.25c4.97 0 9-3.694 9-8.25s-4.03-8.25-9-8.25S3 7.444 3 12c0 2.104.859 4.023 2.273 5.48.432.447.74 1.04.586 1.641a4.483 4.483 0 0 1-1.923 2.07c-.464.248.035.75.502.578a11.97 11.97 0 0 0 3.42-1.48c.53-.18 1.09-.208 1.644-.208Z" /></svg>
              댓글 {{ content.comment_count }}
            </span>
            <span>
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="meta-icon"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" /></svg>
              {{ fmtDate(content.created_at) }}
            </span>
          </div>
          <p class="body">{{ content.body }}</p>
          <button class="like" :class="{ on: content.is_liked }" @click="toggleLike">
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
            <span>좋아요 {{ content.like_count }}</span>
          </button>
        </div>

        <!-- 댓글 -->
        <section class="comments">
          <h2>댓글 <span>{{ content.comment_count }}</span></h2>

          <ul v-if="comments.length" class="c-list">
            <li v-for="c in comments" :key="c.id">
              <div class="c-top">
                <strong>{{ c.author }}</strong>
                <span class="c-date">{{ fmt(c.created_at) }}</span>
              </div>
              <p class="c-body">{{ c.body }}</p>
            </li>
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
  padding: 28px 0 20px;
  min-height: 72vh;
}
.narrow {
  max-width: 820px;
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
  padding: 60px 0;
}
.player {
  position: relative;
  width: 100%;
  aspect-ratio: 16 / 9;
  border-radius: 14px;
  overflow: hidden;
  background: #000;
  box-shadow: var(--shadow);
}
.player iframe {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}
.no-video {
  position: absolute;
  inset: 0;
  display: grid;
  place-items: center;
  color: #fff;
  font-size: 0.9rem;
}
.info {
  margin-top: 22px;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--line);
}
.badge {
  font-size: 0.74rem;
  font-weight: 700;
  color: var(--teal);
  background: #e6f4f1;
  padding: 4px 10px;
  border-radius: 6px;
}
.info h1 {
  font-size: 1.5rem;
  font-weight: 800;
  letter-spacing: -0.5px;
  margin: 14px 0 12px;
  line-height: 1.35;
}
.meta {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 0.82rem;
  color: var(--text-mute);
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
.body {
  margin: 18px 0;
  font-size: 0.96rem;
  line-height: 1.75;
  color: var(--text-sub);
  white-space: pre-wrap;
}
.like {
  display: inline-flex;
  align-items: center;
  gap: 8px;
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
.like:hover {
  border-color: #fca5a5;
  background-color: #fff5f5;
}
.like.on {
  background: #fee2e2;
  border-color: #fca5a5;
  color: #dc2626;
}
.heart-icon {
  width: 18px;
  height: 18px;
  transition: transform 0.2s ease, fill 0.2s ease, stroke 0.2s ease;
  fill: transparent;
  stroke: var(--text-sub);
}
.like:hover .heart-icon {
  stroke: #dc2626;
}
.like.on .heart-icon {
  fill: #dc2626;
  stroke: #dc2626;
  animation: heart-bounce 0.4s ease;
}
@keyframes heart-bounce {
  0% { transform: scale(1); }
  50% { transform: scale(1.35); }
  100% { transform: scale(1); }
}
.comments {
  margin-top: 26px;
}
.comments h2 {
  font-size: 1.1rem;
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
