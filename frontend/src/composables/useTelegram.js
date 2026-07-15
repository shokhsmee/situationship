import { ref } from 'vue'

/**
 * Thin wrapper over the Telegram WebApp SDK (injected by telegram-web-app.js).
 * Degrades gracefully to a no-op when opened outside Telegram (plain browser).
 */
const tg = typeof window !== 'undefined' ? window.Telegram?.WebApp : null

export function useTelegram() {
  const isTelegram = ref(!!tg?.initData)

  function ready() {
    tg?.ready()
    tg?.expand()
  }

  function haptic(kind = 'light') {
    try {
      tg?.HapticFeedback?.impactOccurred(kind)
    } catch {
      /* not supported */
    }
  }

  const initData = tg?.initData || ''
  const tgUser = tg?.initDataUnsafe?.user || null
  const themeParams = tg?.themeParams || {}

  return { isTelegram, ready, haptic, initData, tgUser, themeParams }
}
