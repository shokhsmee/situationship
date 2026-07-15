<script setup>
import { ref } from 'vue'
import { useAdminStore } from '@/stores/admin'
import { useUiStore } from '@/stores/ui'

const props = defineProps({ scenario: { type: Object, required: true } })
const admin = useAdminStore()
const ui = useUiStore()

const TRIGGERS = ['evidence_revealed', 'evidence_combined', 'location_visited', 'phase_started', 'vote_result']
const EFFECTS = ['unlock_evidence', 'lock_evidence', 'add_time', 'remove_time', 'reveal_hint', 'new_situation_text', 'swap_role_info']
const PHASES = ['intro', 'evidence', 'discussion', 'vote', 'insider_guess']

const blank = () => ({
  scenario_id: props.scenario.id,
  name: '', trigger_type: 'evidence_combined', effect_type: 'unlock_evidence',
  narration_text: '', fire_once: true,
  trigEvidence: [], trigPhase: 'evidence', trigLocation: null,
  effEvidence: [], effSeconds: 60, effText: '',
})
const draft = ref(blank())

function edit(ev) {
  const d = blank()
  Object.assign(d, {
    id: ev.id, name: ev.name, trigger_type: ev.trigger_type, effect_type: ev.effect_type,
    narration_text: ev.narration_text, fire_once: ev.fire_once,
    trigEvidence: ev.trigger_payload.evidence_ids || [],
    trigPhase: ev.trigger_payload.phase || 'evidence',
    trigLocation: ev.trigger_payload.location_id ?? null,
    effEvidence: ev.effect_payload.evidence_ids || [],
    effSeconds: ev.effect_payload.seconds ?? 60,
    effText: ev.effect_payload.text || '',
  })
  draft.value = d
}
const reset = () => (draft.value = blank())

function buildTrigger(d) {
  if (['evidence_revealed', 'evidence_combined'].includes(d.trigger_type)) return { evidence_ids: d.trigEvidence }
  if (d.trigger_type === 'phase_started') return { phase: d.trigPhase }
  return { location_id: d.trigLocation }
}
function buildEffect(d) {
  if (['unlock_evidence', 'lock_evidence'].includes(d.effect_type)) return { evidence_ids: d.effEvidence }
  if (['add_time', 'remove_time'].includes(d.effect_type)) return { seconds: d.effSeconds }
  return { text: d.effText }
}

async function save() {
  const d = draft.value
  await admin.saveEvent({
    id: d.id, scenario_id: props.scenario.id, name: d.name,
    trigger_type: d.trigger_type, trigger_payload: buildTrigger(d),
    effect_type: d.effect_type, effect_payload: buildEffect(d),
    narration_text: d.narration_text, fire_once: d.fire_once,
  })
  ui.toast('Event saved', 'success')
  reset()
}
async function remove(ev) {
  await admin.deleteEvent(ev.id, props.scenario.id)
  ui.toast('Event deleted')
}
const evTitle = (id) => props.scenario.evidence.find((e) => e.id === id)?.title || `#${id}`
</script>

<template>
  <div class="space-y-4">
    <!-- IF / THEN builder -->
    <div class="card p-4 space-y-3">
      <input v-model="draft.name" class="input" placeholder="Event name" />

      <div class="grid md:grid-cols-2 gap-3">
        <!-- IF block -->
        <div class="rounded-lg border border-noir-600 p-3">
          <p class="text-xs uppercase text-amber-glow mb-2">IF (trigger)</p>
          <select v-model="draft.trigger_type" class="input mb-2">
            <option v-for="t in TRIGGERS" :key="t" :value="t">{{ t }}</option>
          </select>
          <div v-if="['evidence_revealed', 'evidence_combined'].includes(draft.trigger_type)" class="space-y-1 max-h-40 overflow-y-auto">
            <label v-for="e in scenario.evidence" :key="e.id" class="flex items-center gap-2 text-xs">
              <input v-model="draft.trigEvidence" type="checkbox" :value="e.id" /> {{ e.title }}
            </label>
          </div>
          <select v-else-if="draft.trigger_type === 'phase_started'" v-model="draft.trigPhase" class="input">
            <option v-for="p in PHASES" :key="p" :value="p">{{ p }}</option>
          </select>
          <select v-else v-model="draft.trigLocation" class="input">
            <option v-for="l in scenario.locations" :key="l.id" :value="l.id">{{ l.name }}</option>
          </select>
        </div>

        <!-- THEN block -->
        <div class="rounded-lg border border-noir-600 p-3">
          <p class="text-xs uppercase text-emerald-400 mb-2">THEN (effect)</p>
          <select v-model="draft.effect_type" class="input mb-2">
            <option v-for="e in EFFECTS" :key="e" :value="e">{{ e }}</option>
          </select>
          <div v-if="['unlock_evidence', 'lock_evidence'].includes(draft.effect_type)" class="space-y-1 max-h-40 overflow-y-auto">
            <label v-for="e in scenario.evidence" :key="e.id" class="flex items-center gap-2 text-xs">
              <input v-model="draft.effEvidence" type="checkbox" :value="e.id" /> {{ e.title }}
            </label>
          </div>
          <input v-else-if="['add_time', 'remove_time'].includes(draft.effect_type)" v-model.number="draft.effSeconds" type="number" class="input" placeholder="seconds" />
          <textarea v-else v-model="draft.effText" class="input" rows="2" placeholder="text" />
        </div>
      </div>

      <textarea v-model="draft.narration_text" class="input" rows="2" placeholder="Dramatic narration shown to players when this fires…" />
      <label class="flex items-center gap-2 text-sm"><input v-model="draft.fire_once" type="checkbox" /> Fire once</label>
      <div class="flex gap-2">
        <button class="btn-amber flex-1" @click="save">{{ draft.id ? 'Update event' : 'Add event' }}</button>
        <button v-if="draft.id" class="btn-ghost" @click="reset">Cancel</button>
      </div>
    </div>

    <!-- Existing events as connected blocks -->
    <div v-for="ev in scenario.events" :key="ev.id" class="card p-3">
      <div class="flex justify-between items-start">
        <div class="text-sm">
          <span class="font-display">{{ ev.name || 'Event' }}</span>
          <div class="flex items-center gap-2 mt-1 flex-wrap text-xs">
            <span class="px-2 py-0.5 rounded bg-noir-800 text-amber-glow">IF {{ ev.trigger_type }}</span>
            <span v-for="id in ev.trigger_payload.evidence_ids || []" :key="id" class="text-evidence/60">{{ evTitle(id) }}</span>
            <span>→</span>
            <span class="px-2 py-0.5 rounded bg-noir-800 text-emerald-400">{{ ev.effect_type }}</span>
          </div>
        </div>
        <span class="flex gap-2">
          <button class="text-xs text-amber-glow" @click="edit(ev)">Edit</button>
          <button class="text-xs text-red-400" @click="remove(ev)">Del</button>
        </span>
      </div>
    </div>
  </div>
</template>
