// 카카오맵 JavaScript SDK 동적 로더
// .env 의 VITE_KAKAO_MAP_KEY 를 사용한다.

const KEY = import.meta.env.VITE_KAKAO_MAP_KEY

let loaderPromise = null

export function hasKakaoKey() {
  return !!KEY && KEY !== 'YOUR_KAKAO_JS_KEY'
}

export function loadKakao() {
  if (!hasKakaoKey()) {
    return Promise.reject(new Error('NO_KEY'))
  }
  if (window.kakao && window.kakao.maps) {
    return Promise.resolve(window.kakao)
  }
  if (loaderPromise) return loaderPromise

  loaderPromise = new Promise((resolve, reject) => {
    const script = document.createElement('script')
    script.src =
      `https://dapi.kakao.com/v2/maps/sdk.js?appkey=${KEY}&autoload=false`
    script.onload = () => window.kakao.maps.load(() => resolve(window.kakao))
    script.onerror = () => reject(new Error('LOAD_FAILED'))
    document.head.appendChild(script)
  })
  return loaderPromise
}
