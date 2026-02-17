import { onMounted, onUnmounted, ref } from 'vue'

export const useFullscreen = () => {
  const isFullscreen = ref(false)

  const syncState = () => {
    isFullscreen.value = Boolean(document.fullscreenElement)
  }

  const toggleFullscreen = async () => {
    if (!document.fullscreenElement) {
      await document.documentElement.requestFullscreen()
    } else {
      await document.exitFullscreen()
    }
    syncState()
  }

  onMounted(() => {
    document.addEventListener('fullscreenchange', syncState)
    syncState()
  })

  onUnmounted(() => {
    document.removeEventListener('fullscreenchange', syncState)
  })

  return { isFullscreen, toggleFullscreen }
}
