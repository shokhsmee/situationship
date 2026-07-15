import { ref, onUnmounted } from 'vue'
import { useGameStore } from '@/stores/game'
import { useAuthStore } from '@/stores/auth'

/**
 * Native WebSocket wrapper for a game room. Dispatches every server message to
 * the game store and auto-reconnects with backoff; on each (re)connect the
 * server pushes a fresh snapshot, so reconnection restores full state.
 */
export function useGameSocket() {
  const game = useGameStore()
  const auth = useAuthStore()

  const connected = ref(false)
  let ws = null
  let currentGameId = null
  let manualClose = false
  let attempts = 0
  let heartbeat = null

  function _url(gameId) {
    const proto = location.protocol === 'https:' ? 'wss' : 'ws'
    return `${proto}://${location.host}/ws/game/${gameId}?token=${auth.token}`
  }

  function connect(gameId) {
    manualClose = false
    currentGameId = gameId
    ws = new WebSocket(_url(gameId))

    ws.onopen = () => {
      connected.value = true
      attempts = 0
      heartbeat = setInterval(() => send({ type: 'ping' }), 25000)
    }
    ws.onmessage = (e) => {
      try {
        game.applyEvent(JSON.parse(e.data))
      } catch {
        /* ignore malformed frame */
      }
    }
    ws.onclose = () => {
      connected.value = false
      clearInterval(heartbeat)
      if (!manualClose) _scheduleReconnect()
    }
    ws.onerror = () => ws?.close()
  }

  function _scheduleReconnect() {
    attempts += 1
    const delay = Math.min(10000, 500 * 2 ** attempts)
    setTimeout(() => {
      if (!manualClose && currentGameId) connect(currentGameId)
    }, delay)
  }

  function send(msg) {
    if (ws?.readyState === WebSocket.OPEN) ws.send(JSON.stringify(msg))
  }

  function disconnect() {
    manualClose = true
    clearInterval(heartbeat)
    ws?.close()
    ws = null
  }

  onUnmounted(disconnect)

  return { connect, disconnect, send, connected }
}
