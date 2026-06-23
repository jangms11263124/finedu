<script setup>
import { RouterView, useRoute } from 'vue-router'
import { computed } from 'vue'
import TheNavbar from '@/components/TheNavbar.vue'
import TheFooter from '@/components/TheFooter.vue'

const route = useRoute()
// 로그인/회원가입은 헤더·푸터 없는 단독 레이아웃
const bare = computed(() => ['login', 'signup'].includes(route.name))
</script>

<template>
  <TheNavbar v-if="!bare" />
  <RouterView />
  <TheFooter v-if="!bare" />
</template>
