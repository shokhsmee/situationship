import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import http from '@/api/http'
import { useUiStore } from './ui'

/**
 * Authoritative game state lives on the server; this store mirrors the latest
 * per-player snapshot and mutates it in response to WebSocket events.
 */
export const useGameStore = defineStore('game', () => {
  const ui = useUiStore()

  const state = ref(null) // full player snapshot
  const threads = ref([]) // corkboard string connections {from,to}
  const result = ref(null)

  const gameId = computed(() => state.value?.id ?? null)
  const phase = computed(() => state.value?.phase ?? 'lobby')
  const round = computed(() => state.value?.round ?? 0)
  const deadline = computed(() => state.value?.deadline ?? null)
  const me = computed(() => state.value?.me ?? null)
  const players = computed(() => state.value?.players ?? [])
  const board = computed(() => state.value?.board ?? [])
  const locations = computed(() => state.value?.locations ?? [])
  const scenario = computed(() => state.value?.scenario ?? {})
  const isHost = computed(() => !!me.value?.is_host)

  // --- REST actions ------------------------------------------------------
  async function create(scenarioId, settings = {}) {
    return (await http.post('/games', { scenario_id: scenarioId, settings })).data
  }
  async function join(code) {
    state.value = (await http.post('/games/join', { code })).data
    return state.value
  }
  async function fetchState(id) {
    state.value = (await http.get(`/games/${id}/state`)).data
    return state.value
  }
  async function start() {
    state.value = (await http.post(`/games/${gameId.value}/start`)).data
  }
  const reveal = (evidenceId) => http.post(`/games/${gameId.value}/reveal`, { evidence_id: evidenceId })
  const vote = (locationId) => http.post(`/games/${gameId.value}/vote`, { location_id: locationId })
  const guessInsider = (targetPlayerId) =>
    http.post(`/games/${gameId.value}/insider-guess`, { target_player_id: targetPlayerId })
  const advance = () => http.post(`/games/${gameId.value}/advance`)
  async function fetchResult(id) {
    result.value = (await http.get(`/games/${id}/result`)).data
    return result.value
  }

  // --- WebSocket event application --------------------------------------
  function applyEvent(evt) {
    if (!evt?.type) return
    switch (evt.type) {
      case 'snapshot':
        state.value = evt.state
        break
      case 'phase_changed':
        if (state.value) {
          state.value.phase = evt.phase
          state.value.round = evt.round
          state.value.deadline = evt.deadline
        }
        // A new phase may unlock cards / change my hand — pull a fresh snapshot.
        if (gameId.value) fetchState(gameId.value)
        break
      case 'evidence_revealed':
        _pushBoard(evt.evidence)
        break
      case 'event_fired':
        ui.pushEvent(evt)
        if (evt.new_deadline && state.value) state.value.deadline = evt.new_deadline
        if (gameId.value) fetchState(gameId.value) // unlocked evidence into my hand
        break
      case 'vote_update':
        if (state.value) state.value.vote_tally = evt.tally
        break
      case 'presence': {
        const p = players.value.find((x) => x.id === evt.player_id)
        if (p) p.connected = evt.online
        break
      }
      case 'thread_add':
        threads.value.push({ from: evt.from, to: evt.to })
        break
      case 'thread_remove':
        threads.value = threads.value.filter((t) => !(t.from === evt.from && t.to === evt.to))
        break
      case 'game_result':
        result.value = evt
        if (state.value) state.value.phase = 'result'
        break
    }
  }

  function _pushBoard(ev) {
    if (!state.value) return
    if (!state.value.board.some((b) => b.id === ev.id)) state.value.board.push(ev)
  }

  function reset() {
    state.value = null
    threads.value = []
    result.value = null
  }

  return {
    state, threads, result,
    gameId, phase, round, deadline, me, players, board, locations, scenario, isHost,
    create, join, fetchState, start, reveal, vote, guessInsider, advance, fetchResult,
    applyEvent, reset,
  }
})
