import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api'

// AI 맞춤 추천 결과를 보관하는 스토어.
// 페이지를 다시 방문해도 캐시된 결과를 그대로 보여주고,
// 사용자가 '추천 받기 / 다시 추천받기'를 눌렀을 때만 새로 호출한다.
export const useRecommendStore = defineStore('recommend', () => {
  const summary = ref('')
  const bundles = ref([])
  const source = ref('') // 'ai' | 'rule'
  const signalsMeta = ref(null)
  const loaded = ref(false) // 한 번이라도 추천을 받았는지
  const loading = ref(false)
  const error = ref('')

  function getEbti() {
    try {
      return JSON.parse(localStorage.getItem('ebtiResult') || 'null')
    } catch {
      return null
    }
  }

  async function fetch() {
    loading.value = true
    error.value = ''
    try {
      const { data } = await api.post('/contents/ai-recommend/', {
        ebti: getEbti(),
      })
      summary.value = data.summary
      bundles.value = data.bundles || []
      source.value = data.source
      signalsMeta.value = data.signals_meta || null
      loaded.value = true
    } catch {
      error.value = '추천을 불러오지 못했어요. 잠시 후 다시 시도해주세요.'
    } finally {
      loading.value = false
    }
  }

  // 로그아웃 등으로 캐시를 비울 때 사용 (다른 계정으로 결과가 새지 않게)
  function reset() {
    summary.value = ''
    bundles.value = []
    source.value = ''
    signalsMeta.value = null
    loaded.value = false
    loading.value = false
    error.value = ''
  }

  return {
    summary, bundles, source, signalsMeta, loaded, loading, error,
    fetch, reset,
  }
})
