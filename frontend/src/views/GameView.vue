<script setup>
import { onMounted, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useGameStore } from '@/stores/game'
import { useUiStore } from '@/stores/ui'
import { useGameSocket } from '@/composables/useGameSocket'
import PhaseTimer from '@/components/game/PhaseTimer.vue'
import PlayerList from '@/components/game/PlayerList.vue'
import RoleCard from '@/components/game/RoleCard.vue'
import EvidenceCard from '@/components/game/EvidenceCard.vue'
import EvidenceBoard from '@/components/game/EvidenceBoard.vue'
import CityMap from '@/components/game/CityMap.vue'
import FinalAnswerPanel from '@/components/game/FinalAnswerPanel.vue'
import VotePanel from '@/components/game/VotePanel.vue'

const route = useRoute()
const router = useRouter()
const game = useGameStore()
const ui = useUiStore()
const socket = useGameSocket()
const gameId = Number(route.params.id)

const PHASE_TOTALS = { intro: 60, evidence: 90, discussion: 150, vote: 60, insider_guess: 45 }
const total = computed(() => PHASE_TOTALS[game.phase] || 90)

onMounted(async () => {
  await game.fetchState(gameId)
  socket.connect(gameId)
})

watch(
  () => game.phase,
  (p) => {
    if (p === 'result') router.push({ name: 'result', params: { id: gameId } })
  },
)

async function reveal(ev) {
  try {
    await game.reveal(ev.id)
    await game.fetchState(gameId)
  } catch (e) {
    ui.toast(e.response?.data?.detail || 'Cannot reveal', 'error')
  }
}
const submitVote = (locId) => game.vote(locId).catch((e) => ui.toast(e.response?.data?.detail || 'Vote failed', 'error'))
const guess = (pid) => game.guessInsider(pid).then(() => ui.toast('Guess submitted', 'success'))
const skipGuess = () => ui.toast('Skipped')
const advance = () => game.advance().catch(() => ui.toast('Cannot advance', 'error'))

const connect = (pair) => socket.send({ type: 'thread_add', ...pair })
const disconnect = (pair) => socket.send({ type: 'thread_remove', ...pair })
</script>

<template>
  <div v-if="game.state" class="max-w-5xl mx-auto px-4 py-4 space-y-4">
    <!-- Header -->
    <div class="flex items-center justify-between gap-3">
      <div>
        <p class="text-xs uppercase tracking-widest text-evidence/50">
          {{ $t(`phases.${game.phase}`) }}
          <span v-if="game.round"> · Round {{ game.round }}</span>
        </p>
        <h1 class="font-display text-xl">{{ game.scenario.title }}</h1>
      </div>
      <PhaseTimer :deadline="game.deadline" :total="total" />
    </div>

    <PlayerList :players="game.players" :me-player-id="game.me?.player_id" />

    <!-- INTRO -->
    <div v-if="game.phase === 'intro'" class="space-y-5">
      <div class="card p-5">
        <p class="font-display text-lg leading-relaxed">{{ game.scenario.intro_text }}</p>
        <p class="mt-3 text-amber-glow text-sm">🎯 {{ game.scenario.task_text }}</p>
      </div>
      <RoleCard :role="game.me?.role" :is-insider="game.me?.is_insider" :insider-goal="game.me?.insider_goal" />
    </div>

    <!-- EVIDENCE / DISCUSSION -->
    <div v-else-if="['evidence', 'discussion', 'event'].includes(game.phase)" class="grid lg:grid-cols-3 gap-4">
      <div class="lg:col-span-2 space-y-4">
        <EvidenceBoard :board="game.board" :threads="game.threads" @connect="connect" @disconnect="disconnect" />
        <CityMap :locations="game.locations" />
      </div>
      <div class="space-y-3">
        <h2 class="font-display text-sm text-evidence/60">{{ $t('game.yourHand') }}</h2>
        <EvidenceCard
          v-for="ev in game.me?.hand || []"
          :key="ev.id"
          :evidence="ev"
          :revealable="ev.revealable && game.phase === 'evidence'"
          :revealed="ev.revealed"
          @reveal="reveal"
        />
        <p v-if="!(game.me?.hand || []).length" class="text-xs text-evidence/40">No evidence in hand.</p>
      </div>
    </div>

    <!-- VOTE -->
    <FinalAnswerPanel
      v-else-if="game.phase === 'vote'"
      :locations="game.locations"
      :tally="game.state.vote_tally"
      @submit="submitVote"
    />

    <!-- INSIDER GUESS -->
    <VotePanel
      v-else-if="game.phase === 'insider_guess'"
      :players="game.players"
      :me-player-id="game.me?.player_id"
      @guess="guess"
      @skip="skipGuess"
    />

    <!-- Host controls -->
    <div v-if="game.isHost && game.phase !== 'result'" class="text-center pt-2">
      <button class="btn-ghost text-xs" @click="advance">⏭ {{ $t('game.advance') }}</button>
    </div>
  </div>
  <div v-else class="text-center py-20 text-evidence/40">{{ $t('common.loading') }}</div>
</template>
