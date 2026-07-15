<script setup>
import { ref } from 'vue'
import { useAdminStore } from '@/stores/admin'
import { useUiStore } from '@/stores/ui'

const props = defineProps({ scenario: { type: Object, required: true } })
const admin = useAdminStore()
const ui = useUiStore()

const blank = () => ({ scenario_id: props.scenario.id, name: '', description: '', map_x: 50, map_y: 50, is_correct_answer: false })
const draft = ref(blank())

function edit(loc) {
  draft.value = { ...loc }
}
function reset() {
  draft.value = blank()
}
async function save() {
  if (!draft.value.name) return
  await admin.saveLocation(draft.value)
  ui.toast('Location saved', 'success')
  reset()
}
async function remove(loc) {
  await admin.deleteLocation(loc.id, props.scenario.id)
  ui.toast('Location deleted')
}

// Click the map to place the current pin (stores percentage coords).
function place(e) {
  const r = e.currentTarget.getBoundingClientRect()
  draft.value.map_x = Math.round(((e.clientX - r.left) / r.width) * 1000) / 10
  draft.value.map_y = Math.round(((e.clientY - r.top) / r.height) * 1000) / 10
}
</script>

<template>
  <div class="grid lg:grid-cols-2 gap-4">
    <!-- Map placement -->
    <div>
      <p class="label">Click the map to place the pin</p>
      <div class="relative w-full aspect-[16/10] rounded-xl border border-noir-600 bg-noir-900 cursor-crosshair" @click="place">
        <span
          v-for="loc in scenario.locations"
          :key="loc.id"
          class="absolute -translate-x-1/2 -translate-y-full text-xl"
          :class="loc.is_correct_answer ? 'grayscale-0' : 'opacity-70'"
          :style="{ left: loc.map_x + '%', top: loc.map_y + '%' }"
          :title="loc.name"
        >{{ loc.is_correct_answer ? '⭐' : '📍' }}</span>
        <span
          class="absolute -translate-x-1/2 -translate-y-full text-2xl animate-bounce"
          :style="{ left: draft.map_x + '%', top: draft.map_y + '%' }"
        >📌</span>
      </div>
    </div>

    <!-- Form + list -->
    <div class="space-y-3">
      <div class="card p-4 space-y-2">
        <input v-model="draft.name" class="input" placeholder="Location name" />
        <textarea v-model="draft.description" class="input" rows="2" placeholder="Description" />
        <div class="flex gap-2">
          <input v-model.number="draft.map_x" type="number" class="input" placeholder="x%" />
          <input v-model.number="draft.map_y" type="number" class="input" placeholder="y%" />
        </div>
        <label class="flex items-center gap-2 text-sm">
          <input v-model="draft.is_correct_answer" type="checkbox" /> Correct answer
        </label>
        <div class="flex gap-2">
          <button class="btn-amber flex-1" @click="save">{{ draft.id ? 'Update' : 'Add' }}</button>
          <button v-if="draft.id" class="btn-ghost" @click="reset">Cancel</button>
        </div>
      </div>

      <div v-for="loc in scenario.locations" :key="loc.id" class="card p-3 flex items-center justify-between">
        <span class="text-sm">
          {{ loc.is_correct_answer ? '⭐ ' : '' }}{{ loc.name }}
          <span class="text-evidence/40 text-xs">({{ loc.map_x }}, {{ loc.map_y }})</span>
        </span>
        <span class="flex gap-2">
          <button class="text-xs text-amber-glow" @click="edit(loc)">Edit</button>
          <button class="text-xs text-red-400" @click="remove(loc)">Del</button>
        </span>
      </div>
    </div>
  </div>
</template>
