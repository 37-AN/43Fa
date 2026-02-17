import { onMounted, ref, watch } from 'vue'

const STORAGE_KEY = 'control-room-mode'

export const useControlRoomMode = () => {
  const controlRoomMode = ref(false)

  const applyMode = (enabled: boolean) => {
    document.documentElement.classList.toggle('control-room', enabled)
  }

  onMounted(() => {
    const stored = localStorage.getItem(STORAGE_KEY)
    controlRoomMode.value = stored === 'true'
    applyMode(controlRoomMode.value)
  })

  watch(controlRoomMode, (value) => {
    localStorage.setItem(STORAGE_KEY, String(value))
    applyMode(value)
  })

  return { controlRoomMode }
}
