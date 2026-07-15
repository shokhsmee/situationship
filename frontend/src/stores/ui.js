import { defineStore } from 'pinia'
import { ref } from 'vue'
import { setLocale as applyLocale } from '@/i18n'

export const useUiStore = defineStore('ui', () => {
  const eventQueue = ref([]) // pending dramatic event popups
  const currentEvent = ref(null)
  const toasts = ref([])
  const soundEnabled = ref(localStorage.getItem('situationship_sound') !== 'off')
  const locale = ref(localStorage.getItem('situationship_locale') || 'en')

  function pushEvent(evt) {
    eventQueue.value.push(evt)
    if (!currentEvent.value) nextEvent()
  }
  function nextEvent() {
    currentEvent.value = eventQueue.value.shift() || null
  }
  function dismissEvent() {
    nextEvent()
  }

  let toastId = 0
  function toast(message, kind = 'info') {
    const id = ++toastId
    toasts.value.push({ id, message, kind })
    setTimeout(() => {
      toasts.value = toasts.value.filter((t) => t.id !== id)
    }, 3500)
  }

  function toggleSound() {
    soundEnabled.value = !soundEnabled.value
    localStorage.setItem('situationship_sound', soundEnabled.value ? 'on' : 'off')
  }

  function setLocale(l) {
    locale.value = l
    applyLocale(l)
  }

  return {
    eventQueue, currentEvent, toasts, soundEnabled, locale,
    pushEvent, dismissEvent, toast, toggleSound, setLocale,
  }
})
