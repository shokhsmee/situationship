<script setup>
import { ref, computed } from 'vue'
import EvidenceCard from './EvidenceCard.vue'

const props = defineProps({
  board: { type: Array, default: () => [] },
  threads: { type: Array, default: () => [] },
})
const emit = defineEmits(['connect', 'disconnect'])

const selected = ref(null)

// Deterministic loose-grid layout (percent coords) so pins feel hand-placed.
function pos(index, id) {
  const cols = 4
  const col = index % cols
  const row = Math.floor(index / cols)
  const jx = ((id * 37) % 8) - 4
  const jy = ((id * 53) % 8) - 4
  return {
    x: 12 + col * 24 + jx,
    y: 14 + row * 30 + jy,
  }
}

const placed = computed(() =>
  props.board.map((ev, i) => ({ ev, ...pos(i, ev.id) })),
)
const byId = computed(() => Object.fromEntries(placed.value.map((p) => [p.ev.id, p])))

function tap(ev) {
  if (selected.value == null) {
    selected.value = ev.id
  } else if (selected.value === ev.id) {
    selected.value = null
  } else {
    const pair = { from: selected.value, to: ev.id }
    const exists = props.threads.some(
      (t) => (t.from === pair.from && t.to === pair.to) || (t.from === pair.to && t.to === pair.from),
    )
    emit(exists ? 'disconnect' : 'connect', pair)
    selected.value = null
  }
}
</script>

<template>
  <div class="corkboard relative rounded-xl border-4 border-[#4a3319] overflow-hidden min-h-[22rem]">
    <!-- string threads -->
    <svg class="absolute inset-0 w-full h-full pointer-events-none" viewBox="0 0 100 100" preserveAspectRatio="none">
      <line
        v-for="(t, i) in threads"
        :key="i"
        :x1="byId[t.from]?.x"
        :y1="byId[t.from]?.y"
        :x2="byId[t.to]?.x"
        :y2="byId[t.to]?.y"
        stroke="#c0392b"
        stroke-width="0.4"
        vector-effect="non-scaling-stroke"
        style="stroke-width: 2px"
      />
    </svg>

    <div v-if="!board.length" class="absolute inset-0 flex items-center justify-center text-[#e8d9b5]/60 font-display">
      {{ $t('game.board') }} — empty
    </div>

    <div
      v-for="p in placed"
      :key="p.ev.id"
      class="absolute -translate-x-1/2 -translate-y-1/2 animate-fly-to-board"
      :style="{ left: p.x + '%', top: p.y + '%' }"
    >
      <div class="relative" :class="selected === p.ev.id ? 'ring-2 ring-amber-glow rounded-lg' : ''">
        <span class="absolute -top-1 left-1/2 -translate-x-1/2 w-3 h-3 rounded-full bg-red-600 shadow z-10" />
        <EvidenceCard :evidence="p.ev" compact @select="tap" />
      </div>
    </div>
  </div>
</template>
