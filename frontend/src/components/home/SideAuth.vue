<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

const username = ref('')
const password = ref('')
const error = ref('')

async function submit() {
  error.value = ''
  try {
    await auth.login(username.value, password.value)
  } catch {
    error.value = '아이디 또는 비밀번호를 확인해주세요.'
  }
}
</script>

<template>
  <!-- 로그인 상태: 프로필 카드 -->
  <div v-if="auth.isLoggedIn" class="widget profile">
    <!-- 우측 상단 미니멀 로그아웃 버튼 -->
    <button class="logout-btn" @click="auth.logout()" title="로그아웃">
      로그아웃
    </button>

    <!-- 아바타 그라데이션 데코 링 -->
    <div class="avatar-ring">
      <div class="avatar">
        <img v-if="auth.user?.profile_image" :src="auth.user.profile_image" alt="" />
        <span v-else>{{ (auth.user?.nickname || 'U').charAt(0) }}</span>
      </div>
    </div>

    <!-- 유저 기본 정보 -->
    <div class="who">
      <div class="name-row">
        <strong>{{ auth.user?.nickname }}</strong>
        <!-- 연속 출석일 뱃지 -->
        <span v-if="auth.user?.attendance_streak" class="streak-badge" title="연속 출석">
          <svg class="streak-ico" viewBox="0 0 24 24" fill="currentColor">
            <path d="M17.557 11.237c-.31-.83-.75-1.57-1.3-2.22-.38-.45-.81-.85-1.29-1.2a10.97 10.97 0 0 0-4.4-2.1c-.26-.06-.5-.22-.61-.47-.11-.25-.09-.54.06-.77.56-.84.97-1.78 1.2-2.78.07-.31-.05-.63-.31-.81-.26-.18-.6-.2-.88-.04-1.95 1.15-3.52 2.82-4.52 4.81-1.39 2.76-1.58 6.06-.21 8.92 1.34 2.81 4.22 4.67 7.37 4.67 3.32 0 6.27-2.05 7.42-5.14.73-1.96.67-4.14-.13-6.07v-.01zM11.93 17.5c-2.48 0-4.5-2.02-4.5-4.5 0-1.12.41-2.14 1.09-2.93.18-.21.21-.51.08-.75-.13-.24-.39-.37-.66-.32a6.38 6.38 0 0 0-3.32 1.94 6.42 6.42 0 0 0-1.33 6.64 6.47 6.47 0 0 0 6.01 4.19c3.34 0 6.13-2.54 6.46-5.84a6.49 6.49 0 0 1-3.83 1.57z"/>
          </svg>
          <span>연속 {{ auth.user.attendance_streak }}일</span>
        </span>
      </div>
      <span class="lv">@{{ auth.user?.username }}</span>
    </div>

    <!-- 미니 대시보드 통계 지표 -->
    <div class="user-stats">
      <div class="stat-item">
        <span class="stat-lbl">작성한 글</span>
        <span class="stat-val">{{ auth.user?.post_count ?? 0 }}</span>
      </div>
      <div class="stat-divider"></div>
      <div class="stat-item">
        <span class="stat-lbl">좋아요한 글</span>
        <span class="stat-val">{{ auth.user?.liked_post_count ?? 0 }}</span>
      </div>
      <div class="stat-divider"></div>
      <div class="stat-item">
        <span class="stat-lbl">스크랩 콘텐츠</span>
        <span class="stat-val">{{ auth.user?.liked_content_count ?? 0 }}</span>
      </div>
    </div>

    <!-- 메뉴 버튼 (2열 슬림 구성) -->
    <div class="prof-menu">
      <RouterLink to="/mypage?tab=liked-contents" class="menu-item">
        <svg class="menu-ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>
        </svg>
        <span>스크랩 콘텐츠</span>
      </RouterLink>
      <RouterLink to="/mypage?edit=true" class="menu-item">
        <svg class="menu-ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="3"></circle>
          <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
        </svg>
        <span>프로필 설정</span>
      </RouterLink>
    </div>
  </div>

  <!-- 비로그인: 로그인 폼 -->
  <div v-else class="widget login">
    <form @submit.prevent="submit">
      <input v-model="username" placeholder="아이디" autocomplete="username" />
      <input
        v-model="password"
        type="password"
        placeholder="비밀번호"
        autocomplete="current-password"
      />
      <p v-if="error" class="err">{{ error }}</p>
      <button class="btn btn-navy btn-block" type="submit">로그인</button>
    </form>
    <div class="links">
      <RouterLink to="/signup">회원가입</RouterLink>
      <span>·</span>
      <a href="#">아이디 찾기</a>
      <span>·</span>
      <a href="#">비밀번호 찾기</a>
    </div>
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
.login form {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.login input {
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  padding: 11px 12px;
  font-size: 0.88rem;
  outline: none;
}
.login input:focus {
  border-color: var(--navy);
}
.err {
  color: #dc2626;
  font-size: 0.76rem;
}
.login .btn {
  margin-top: 4px;
}
.links {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-top: 12px;
  font-size: 0.76rem;
  color: var(--text-mute);
}
.links a:hover {
  color: var(--navy);
}

/* 프로필 카드 */
.profile {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px 20px;
  text-align: center;
}

/* 로그아웃 텍스트 버튼 */
.logout-btn {
  position: absolute;
  top: 14px;
  right: 16px;
  background: none;
  border: none;
  color: var(--text-mute);
  font-size: 0.74rem;
  font-weight: 600;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  transition: all 0.15s ease;
}
.logout-btn:hover {
  background: #fee2e2;
  color: #dc2626;
}

/* 아바타 그라데이션 링 효과 */
.avatar-ring {
  padding: 3px;
  border-radius: 18px;
  background: linear-gradient(135deg, var(--teal), var(--navy));
  box-shadow: 0 4px 14px rgba(20, 32, 74, 0.14);
  margin-bottom: 12px;
  transition: transform 0.2s ease;
}
.avatar-ring:hover {
  transform: scale(1.05) rotate(2deg);
}
.avatar {
  width: 52px;
  height: 52px;
  border-radius: 15px; /* 스쿼클 */
  background: #ffffff;
  color: var(--navy);
  font-weight: 800;
  display: grid;
  place-items: center;
  font-size: 1.25rem;
  overflow: hidden;
  border: 2px solid #ffffff;
}
.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 13px;
}
.avatar span {
  background: linear-gradient(135deg, var(--teal), var(--navy));
  color: #fff;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
  padding-bottom: 2px;
  border-radius: 13px;
}

/* 유저 정보 */
.who {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  width: 100%;
  margin-bottom: 16px;
}
.name-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  width: 100%;
  flex-wrap: wrap;
}
.who strong {
  font-size: 1.08rem;
  font-weight: 800;
  color: var(--navy);
}
.lv {
  font-size: 0.78rem;
  color: var(--text-mute);
  font-weight: 500;
}

/* 스트릭 미니 뱃지 */
.streak-badge {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  background: #fff3e6;
  color: #c2680c;
  font-size: 0.7rem;
  font-weight: 700;
  padding: 2px 7px;
  border-radius: 6px;
  white-space: nowrap;
}
.streak-ico {
  width: 11px;
  height: 11px;
  color: #ea580c; /* 주황 불꽃 */
}

/* 미니 대시보드 통계 */
.user-stats {
  display: flex;
  align-items: center;
  justify-content: space-around;
  width: 100%;
  background: var(--bg);
  border-radius: 12px;
  padding: 12px 4px;
  margin-bottom: 16px;
  border: 1px solid var(--line);
}
.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3px;
  flex: 1;
}
.stat-lbl {
  font-size: 0.68rem;
  color: var(--text-mute);
  font-weight: 600;
}
.stat-val {
  font-size: 0.95rem;
  font-weight: 800;
  color: var(--navy);
}
.stat-divider {
  width: 1px;
  height: 20px;
  background: var(--line);
}

/* 메뉴 버튼 (2열 슬림 구성) */
.prof-menu {
  display: flex;
  gap: 10px;
  width: 100%;
  border-top: 1px solid var(--line);
  padding-top: 16px;
}
.menu-item {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 8px;
  border-radius: 10px;
  background: #ffffff;
  border: 1px solid var(--line);
  text-decoration: none;
  box-shadow: 0 2px 6px rgba(20, 32, 74, 0.04);
  transition: all 0.15s ease;
}
.menu-item:hover {
  background: var(--navy);
  border-color: var(--navy);
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(20, 32, 74, 0.15);
}
.menu-ico {
  width: 16px;
  height: 16px;
  color: var(--navy);
  transition: color 0.15s;
}
.menu-item:hover .menu-ico {
  color: #ffffff;
}
.menu-item span {
  font-size: 0.78rem;
  font-weight: 700;
  color: var(--text-sub);
  transition: color 0.15s;
}
.menu-item:hover span {
  color: #ffffff;
}
</style>

