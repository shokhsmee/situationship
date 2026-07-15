import { ref, computed, watch, onUnmounted } from 'vue'

/**
 * Renders a countdown from a server-authoritative deadline (epoch seconds).
 * The server owns the clock; this only interpolates for display. `total` (the
 * phase length in seconds) is optional and used to compute the progress ring.
 */
export function useTimer(deadlineRef, totalRef) {
  const nowMs = ref(Date.now())
  let handle = null

  function tick() {
    nowMs.value = Date.now()
  }

  function startLoop() {
    stopLoop()
    handle = setInterval(tick, 250)
  }
  function stopLoop() {
    if (handle) clearInterval(handle)
    handle = null
  }

  watch(
    () => deadlineRef.value,
    (d) => (d ? startLoop() : stopLoop()),
    { immediate: true },
  )
  onUnmounted(stopLoop)

  const remaining = computed(() => {
    if (!deadlineRef.value) return null
    return Math.max(0, deadlineRef.value * 1000 - nowMs.value) / 1000
  })

  const label = computed(() => {
    if (remaining.value == null) return '--:--'
    const s = Math.ceil(remaining.value)
    return `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`
  })

  const progress = computed(() => {
    const total = totalRef?.value
    if (!total || remaining.value == null) return 0
    return Math.min(1, Math.max(0, remaining.value / total))
  })

  const urgent = computed(() => remaining.value != null && remaining.value <= 10)

  return { remaining, label, progress, urgent }
}
