<script setup>
import { RouterView, useRoute } from 'vue-router'
import { computed, ref, onMounted, onUnmounted } from 'vue'
import TheNavbar from '@/components/TheNavbar.vue'
import TheFooter from '@/components/TheFooter.vue'

const route = useRoute()
// 로그인/회원가입은 헤더·푸터 없는 단독 레이아웃
const bare = computed(() => ['login', 'signup'].includes(route.name))

const showTopBtn = ref(false)

const handleScroll = () => {
  showTopBtn.value = window.scrollY > 300
}

const scrollToTop = () => {
  window.scrollTo({
    top: 0,
    behavior: 'smooth',
  })
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<template>
  <TheNavbar v-if="!bare" />
  <RouterView />
  <TheFooter v-if="!bare" />

  <!-- Scroll to Top 플로팅 버튼 -->
  <Transition name="fade">
    <button
      v-if="showTopBtn"
      class="scroll-top-btn"
      @click="scrollToTop"
      aria-label="맨 위로 이동"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        stroke-width="2.5"
        stroke="currentColor"
        class="arrow-up-icon"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          d="M4.5 15.75l7.5-7.5 7.5 7.5"
        />
      </svg>
    </button>
  </Transition>
</template>

<style scoped>
.scroll-top-btn {
  position: fixed;
  bottom: 30px;
  right: 30px;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: var(--navy);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(27, 42, 89, 0.2);
  cursor: pointer;
  z-index: 99;
  border: none;
  outline: none;
  transition: transform 0.2s, background-color 0.2s, opacity 0.2s;
}

.scroll-top-btn:hover {
  background: var(--navy-dark);
  transform: translateY(-3px);
}

.scroll-top-btn:active {
  transform: translateY(-1px);
}

.arrow-up-icon {
  width: 20px;
  height: 20px;
}

/* fade 트랜지션 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: scale(0.9);
}
</style>
