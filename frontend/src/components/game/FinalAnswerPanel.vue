<script setup>
import { ref } from 'vue'
import CityMap from './CityMap.vue'

const props = defineProps({
  locations: { type: Array, default: () => [] },
  tally: { type: Object, default: () => ({}) },
  submitted: { type: Boolean, default: false },
})
const emit = defineEmits(['submit'])

const chosen = ref(null)
function pick(loc) {
  chosen.value = loc.id
  emit('submit', loc.id) // vote is live; last pick wins
}
</script>

<template>
  <div class="space-y-4">
    <h2 class="font-display text-xl text-center text-amber-glow">{{ $t('phases.vote') }}</h2>
    <CityMap :locations="locations" selectable :selected-id="chosen" :tally="tally" @select="pick" />

    <div class="grid grid-cols-2 gap-2">
      <button
        v-for="loc in locations"
        :key="loc.id"
        class="btn text-sm"
        :class="chosen === loc.id ? 'btn-amber' : 'btn-ghost'"
        @click="pick(loc)"
      >
        {{ loc.name }}
        <span v-if="tally[loc.id]" class="ml-1 text-xs">· {{ tally[loc.id] }}</span>
      </button>
    </div>
    <p v-if="chosen" class="text-center text-sm text-evidence/60">
      {{ $t('game.voteFor') }}: <span class="text-amber-glow">{{ locations.find((l) => l.id === chosen)?.name }}</span>
    </p>
  </div>
</template>
