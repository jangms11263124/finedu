<script setup>
import { inject, ref } from 'vue'
import { RouterLink } from 'vue-router'
import api from '@/api'
import { useAuthStore } from '@/stores/auth'

const props = defineProps({
  comment: { type: Object, required: true },
  postId: { type: [Number, String], required: true },
  depth: { type: Number, default: 0 },
})
const emit = defineEmits(['deleted'])

const auth = useAuthStore()
const bumpCount = inject('bumpCommentCount', () => {})

const editing = ref(false)
const editText = ref('')
const replying = ref(false)
const replyText = ref('')

const mine = () => auth.user && props.comment.author_id === auth.user.id

async function toggleLike() {
  if (!auth.isLoggedIn) return alert('로그인이 필요합니다.')
  const { data } = await api.post(`/comments/${props.comment.id}/like/`)
  props.comment.is_liked = data.liked
  props.comment.like_count = data.like_count
}

function startEdit() {
  editing.value = true
  editText.value = props.comment.content
}
async function saveEdit() {
  if (!editText.value.trim()) return
  const { data } = await api.patch(`/comments/${props.comment.id}/`, {
    content: editText.value.trim(),
  })
  props.comment.content = data.content
  editing.value = false
}

async function remove() {
  if (!confirm('댓글을 삭제할까요?')) return
  await api.delete(`/comments/${props.comment.id}/`)
  // 대댓글 수까지 합산해 카운트 감소
  bumpCount(-(1 + (props.comment.replies?.length || 0)))
  emit('deleted', props.comment.id)
}

async function submitReply() {
  if (!replyText.value.trim()) return
  const { data } = await api.post('/comments/', {
    post: props.postId,
    parent: props.comment.id,
    content: replyText.value.trim(),
  })
  if (!props.comment.replies) props.comment.replies = []
  props.comment.replies.push(data)
  bumpCount(1)
  replyText.value = ''
  replying.value = false
}

function onChildDeleted(id) {
  props.comment.replies = props.comment.replies.filter((r) => r.id !== id)
}

function fmt(dt) {
  return new Date(dt).toLocaleString('ko-KR', {
    month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit',
  })
}
</script>

<template>
  <li class="cmt" :class="{ reply: depth > 0 }">
    <div class="c-top">
      <strong>{{ comment.author }}</strong>
      <span class="c-date">{{ fmt(comment.created_at) }}</span>
    </div>

    <div v-if="editing" class="c-edit">
      <input v-model="editText" @keyup.enter="saveEdit" />
      <button class="btn btn-navy sm" @click="saveEdit">저장</button>
      <button class="btn btn-outline sm" @click="editing = false">취소</button>
    </div>
    <template v-else>
      <p class="c-body">{{ comment.content }}</p>
      <div class="c-actions">
        <button class="like" :class="{ on: comment.is_liked }" @click="toggleLike">
          {{ comment.is_liked ? '❤️' : '🤍' }} {{ comment.like_count }}
        </button>
        <button v-if="auth.isLoggedIn && depth < 2" @click="replying = !replying">
          답글
        </button>
        <button v-if="mine()" @click="startEdit">수정</button>
        <button v-if="mine()" @click="remove">삭제</button>
      </div>
    </template>

    <!-- 답글 입력 -->
    <form v-if="replying" class="reply-form" @submit.prevent="submitReply">
      <input v-model="replyText" placeholder="답글을 입력하세요" />
      <button class="btn btn-navy sm" type="submit">등록</button>
    </form>

    <!-- 대댓글 -->
    <ul v-if="comment.replies && comment.replies.length" class="replies">
      <CommentItem
        v-for="r in comment.replies"
        :key="r.id"
        :comment="r"
        :post-id="postId"
        :depth="depth + 1"
        @deleted="onChildDeleted"
      />
    </ul>
  </li>
</template>

<style scoped>
.cmt {
  padding: 14px 0;
  border-bottom: 1px solid var(--line);
  list-style: none;
}
.cmt.reply {
  border-bottom: none;
  padding: 12px 0 4px;
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
  margin-top: 8px;
  display: flex;
  align-items: center;
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
.c-actions .like {
  border: 1px solid var(--line);
  border-radius: 999px;
  padding: 3px 9px;
  font-weight: 600;
}
.c-actions .like.on {
  background: #fee2e2;
  border-color: #fca5a5;
  color: #dc2626;
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
.reply-form {
  display: flex;
  gap: 6px;
  margin: 10px 0 4px;
}
.reply-form input {
  flex: 1;
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  padding: 9px 12px;
  font-size: 0.86rem;
  outline: none;
}
.reply-form input:focus {
  border-color: var(--navy);
}
.btn.sm {
  padding: 7px 12px;
  font-size: 0.8rem;
}
/* 대댓글 들여쓰기 */
.replies {
  margin: 6px 0 0;
  padding: 0 0 0 18px;
  border-left: 2px solid var(--line);
}
</style>
