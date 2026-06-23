<script setup>
import { onMounted, ref } from 'vue'
import api from '@/api'
import { useAuthStore } from '@/stores/auth'
import CommunityTabs from '@/components/community/CommunityTabs.vue'

const auth = useAuthStore()

const tab = ref('contents') // 'contents' | 'users'
const contents = ref([])
const users = ref([])
const loading = ref(true)

const medals = ['🥇', '🥈', '🥉']

const gradients = {
  economy: 'linear-gradient(135deg,#0f766e,#0891b2)',
  invest: 'linear-gradient(135deg,#1b2a59,#3b82f6)',
  saving: 'linear-gradient(135deg,#15803d,#65a30d)',
  finance: 'linear-gradient(135deg,#7c3aed,#2563eb)',
  etc: 'linear-gradient(135deg,#475569,#94a3b8)',
}
const icons = { economy: '📈', invest: '💹', saving: '🏦', finance: '💳', etc: '📰' }

async function load() {
  loading.value = true
  try {
    const [c, u] = await Promise.all([
      api.get('/contents/ranking/'),
      api.get('/accounts/ranking/'),
    ])
    contents.value = c.data
    users.value = u.data
  } finally {
    loading.value = false
  }
}

async function toggleLike(content) {
  if (!auth.isLoggedIn) {
    alert('로그인이 필요합니다.')
    return
  }
  const { data } = await api.post(`/contents/${content.id}/like/`)
  content.is_liked = data.liked
  content.like_count = data.like_count
}

onMounted(load)
</script>

<template>
  <main class="community">
    <div class="container">
      <CommunityTabs />

      <div class="sub-tabs">
        <button :class="{ on: tab === 'contents' }" @click="tab = 'contents'">
          🔥 콘텐츠 랭킹
        </button>
        <button :class="{ on: tab === 'users' }" @click="tab = 'users'">
          👑 사용자 랭킹
        </button>
      </div>

      <p v-if="loading" class="empty">불러오는 중...</p>

      <!-- 콘텐츠 좋아요 랭킹 -->
      <ul v-else-if="tab === 'contents'" class="rank-list">
        <li v-for="(c, i) in contents" :key="c.id" class="rank-row">
          <span class="rank" :class="{ top: i < 3 }">{{ medals[i] || i + 1 }}</span>
          <span
            class="thumb"
            :style="{ background: gradients[c.category] || gradients.etc }"
          >{{ icons[c.category] || '📰' }}</span>
          <div class="info">
            <strong>{{ c.title }}</strong>
            <span class="cat">{{ c.category_display }}</span>
          </div>
          <div class="stats">
            <span>💬 {{ c.comment_count }}</span>
            <span>👁 {{ c.views.toLocaleString() }}</span>
            <button class="like" :class="{ on: c.is_liked }" @click="toggleLike(c)">
              {{ c.is_liked ? '❤️' : '🤍' }} {{ c.like_count }}
            </button>
          </div>
        </li>
      </ul>

      <!-- 사용자 활동 랭킹 -->
      <ul v-else class="rank-list">
        <li v-for="(u, i) in users" :key="u.id" class="rank-row">
          <span class="rank" :class="{ top: i < 3 }">{{ medals[i] || i + 1 }}</span>
          <span class="avatar">{{ (u.nickname || 'U').charAt(0) }}</span>
          <div class="info">
            <strong>{{ u.nickname }}</strong>
            <span class="cat">Lv.{{ u.level }}</span>
          </div>
          <div class="stats">
            <span class="point">{{ u.points.toLocaleString() }} P</span>
          </div>
        </li>
      </ul>
    </div>
  </main>
</template>

<style scoped>
.community {
  padding: 36px 0 20px;
  min-height: 70vh;
}
.sub-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 18px;
}
.sub-tabs button {
  background: #fff;
  border: 1px solid var(--line);
  border-radius: 999px;
  padding: 8px 16px;
  font-size: 0.86rem;
  font-weight: 600;
  color: var(--text-sub);
}
.sub-tabs button.on {
  background: #e6f4f1;
  color: var(--teal);
  border-color: #b9e0d8;
}
.empty {
  color: var(--text-mute);
  padding: 40px 0;
  text-align: center;
}
.rank-list {
  list-style: none;
  margin: 0;
  padding: 0;
  background: #fff;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  overflow: hidden;
}
.rank-row {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 18px;
  border-bottom: 1px solid var(--line);
}
.rank-row:last-child {
  border-bottom: none;
}
.rank-row:hover {
  background: var(--bg);
}
.rank {
  width: 30px;
  text-align: center;
  font-weight: 800;
  font-size: 1.05rem;
  color: var(--text-mute);
}
.rank.top {
  font-size: 1.3rem;
}
.thumb {
  width: 46px;
  height: 46px;
  border-radius: 10px;
  display: grid;
  place-items: center;
  font-size: 1.3rem;
  flex-shrink: 0;
}
.avatar {
  width: 46px;
  height: 46px;
  border-radius: 999px;
  background: linear-gradient(135deg, var(--teal), var(--navy));
  color: #fff;
  font-weight: 800;
  display: grid;
  place-items: center;
  flex-shrink: 0;
}
.info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 3px;
}
.info strong {
  font-size: 0.95rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.cat {
  font-size: 0.76rem;
  color: var(--teal);
  font-weight: 600;
}
.stats {
  display: flex;
  align-items: center;
  gap: 14px;
  font-size: 0.8rem;
  color: var(--text-mute);
  white-space: nowrap;
}
.point {
  font-weight: 800;
  color: var(--navy);
  font-size: 0.95rem;
}
.like {
  background: var(--bg);
  border: 1px solid var(--line);
  border-radius: 999px;
  padding: 6px 12px;
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--text-sub);
}
.like.on {
  background: #fee2e2;
  border-color: #fca5a5;
  color: #dc2626;
}
@media (max-width: 560px) {
  .stats span:nth-child(2) {
    display: none;
  }
}
</style>
