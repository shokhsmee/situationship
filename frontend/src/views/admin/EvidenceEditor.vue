<script setup>
import { ref, onMounted, watch } from 'vue'
import { useAdminStore } from '@/stores/admin'
import { useUiStore } from '@/stores/ui'

const props = defineProps({ scenario: { type: Object, required: true } })
const admin = useAdminStore()
const ui = useUiStore()

const TYPES = ['document', 'witness', 'physical', 'medical', 'rumor']
const coverage = ref(null)

const blank = () => ({
  scenario_id: props.scenario.id,
  role_id: props.scenario.roles[0]?.id ?? null,
  location_id: null,
  title: '', text: '', type: 'document',
  is_red_herring: false, reveal_phase: 1, weight: 1, starts_locked: false,
})
const draft = ref(blank())

async function loadCoverage() {
  coverage.value = await admin.coverage(props.scenario.id)
}
onMounted(loadCoverage)
watch(() => props.scenario.evidence.length, loadCoverage)

const edit = (e) => (draft.value = { ...e })
const reset = () => (draft.value = blank())

async function save() {
  if (!draft.value.title || !draft.value.role_id) return
  await admin.saveEvidence(draft.value)
  ui.toast('Evidence saved', 'success')
  reset()
}
async function remove(e) {
  await admin.deleteEvidence(e.id, props.scenario.id)
  ui.toast('Evidence deleted')
}
const roleName = (id) => props.scenario.roles.find((r) => r.id === id)?.name || '—'
</script>

<template>
  <div class="space-y-4">
    <!-- Coverage matrix -->
    <div v-if="coverage" class="card p-4">
      <h3 class="text-sm text-evidence/60 mb-2">Coverage · {{ coverage.total_evidence }} evidence total</h3>
      <div class="flex flex-wrap gap-2">
        <span
          v-for="r in coverage.roles"
          :key="r.role_id"
          class="px-3 py-1 rounded-lg text-xs"
          :class="r.evidence_count < 2 ? 'bg-red-950 text-red-300' : 'bg-noir-800'"
        >
          {{ r.name }}: {{ r.evidence_count }}<span v-if="r.red_herrings"> ({{ r.red_herrings }}🎭)</span>
        </span>
      </div>
    </div>

    <div class="grid lg:grid-cols-2 gap-4">
      <div class="card p-4 space-y-2 h-fit">
        <input v-model="draft.title" class="input" placeholder="Evidence title" />
        <textarea v-model="draft.text" class="input" rows="2" placeholder="Evidence text" />
        <div class="grid grid-cols-2 gap-2">
          <select v-model="draft.role_id" class="input">
            <option v-for="r in scenario.roles" :key="r.id" :value="r.id">{{ r.name }}</option>
          </select>
          <select v-model="draft.location_id" class="input">
            <option :value="null">No location</option>
            <option v-for="l in scenario.locations" :key="l.id" :value="l.id">{{ l.name }}</option>
          </select>
          <select v-model="draft.type" class="input">
            <option v-for="t in TYPES" :key="t" :value="t">{{ t }}</option>
          </select>
          <input v-model.number="draft.reveal_phase" type="number" min="1" class="input" placeholder="reveal round" />
          <input v-model.number="draft.weight" type="number" min="0" class="input" placeholder="weight" />
        </div>
        <div class="flex gap-4 text-sm">
          <label class="flex items-center gap-1"><input v-model="draft.is_red_herring" type="checkbox" /> Red herring</label>
          <label class="flex items-center gap-1"><input v-model="draft.starts_locked" type="checkbox" /> Starts locked</label>
        </div>
        <div class="flex gap-2">
          <button class="btn-amber flex-1" @click="save">{{ draft.id ? 'Update' : 'Add' }}</button>
          <button v-if="draft.id" class="btn-ghost" @click="reset">Cancel</button>
        </div>
      </div>

      <div class="space-y-2 max-h-[30rem] overflow-y-auto">
        <div v-for="e in scenario.evidence" :key="e.id" class="card p-3">
          <div class="flex justify-between">
            <span class="text-sm font-display">{{ e.title }}</span>
            <span class="flex gap-2">
              <button class="text-xs text-amber-glow" @click="edit(e)">Edit</button>
              <button class="text-xs text-red-400" @click="remove(e)">Del</button>
            </span>
          </div>
          <p class="text-xs text-evidence/50">
            {{ roleName(e.role_id) }} · {{ e.type }} · R{{ e.reveal_phase }} · w{{ e.weight }}
            <span v-if="e.is_red_herring">· 🎭</span><span v-if="e.starts_locked">· 🔒</span>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
