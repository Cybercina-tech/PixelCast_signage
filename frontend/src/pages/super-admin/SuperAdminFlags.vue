<template>
  <div class="space-y-6">
    <div class="flex flex-wrap justify-between items-center gap-4">
      <div>
        <h1 class="text-2xl font-bold text-primary">Feature flags</h1>
        <p class="text-sm text-muted mt-1">Per-tenant toggles (merged on save)</p>
      </div>
      <button type="button" class="btn-outline px-4 py-2 rounded-lg text-sm" :disabled="loading || !selectedTenantId" @click="loadFlags">
        Reload
      </button>
    </div>

    <div
      v-if="bannerError"
      class="rounded-2xl border border-amber-500/40 bg-amber-500/10 px-4 py-3 text-sm text-amber-900 dark:text-amber-100"
    >
      {{ bannerError }}
    </div>

    <Card>
      <div class="max-w-md mb-6">
        <label class="label-base block text-sm mb-1">Tenant</label>
        <select v-model="selectedTenantId" class="select-base w-full px-3 py-2 rounded-lg" @change="onTenantChange">
          <option value="" disabled>Select a tenant</option>
          <option v-for="t in tenants" :key="t.id" :value="t.id">{{ t.name }}</option>
        </select>
      </div>

      <div v-if="!selectedTenantId" class="text-sm text-muted">Choose a tenant to view flags.</div>
      <div v-else-if="flagsLoading" class="text-center py-10 text-muted">Loading flags…</div>
      <div v-else class="space-y-6">
        <div class="space-y-3">
          <h3 class="text-sm font-semibold text-primary">Current flags</h3>
          <div v-if="!flagEntries.length" class="text-sm text-muted">No flags yet — add one below.</div>
          <div v-for="entry in flagEntries" :key="entry.key" class="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-border-color/60 px-3 py-2">
            <span class="text-sm font-mono text-primary break-all">{{ entry.key }}</span>
            <label class="flex items-center gap-2 text-sm text-secondary">
              <input v-model="entry.boolValue" type="checkbox" class="rounded border-border-color" />
              <span>Enabled</span>
            </label>
          </div>
        </div>

        <div class="rounded-xl border border-border-color/60 p-4 space-y-3">
          <h3 class="text-sm font-semibold text-primary">Add flag</h3>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="label-base block text-xs mb-1">Key</label>
              <input v-model="newKey" type="text" class="input-base w-full px-3 py-2 rounded-lg" placeholder="feature.example" />
            </div>
            <div class="flex items-end gap-3">
              <label class="flex items-center gap-2 text-sm text-secondary">
                <input v-model="newVal" type="checkbox" class="rounded border-border-color" />
                Value
              </label>
            </div>
          </div>
          <button type="button" class="btn-outline px-4 py-2 rounded-lg text-sm" @click="addFlag">Add to list</button>
        </div>

        <div class="flex flex-wrap gap-2">
          <button type="button" class="btn-primary px-4 py-2 rounded-lg text-sm" :disabled="saving" @click="saveFlags">
            {{ saving ? 'Saving…' : 'Save' }}
          </button>
        </div>
      </div>
    </Card>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import Card from '@/components/common/Card.vue'
import { platformAPI } from '@/services/api'
import { normalizeApiError } from '@/utils/apiError'

const loading = ref(true)
const flagsLoading = ref(false)
const saving = ref(false)
const bannerError = ref(null)
const tenants = ref([])
const selectedTenantId = ref('')
const flags = ref({})
const flagEntries = ref([])

const newKey = ref('')
const newVal = ref(false)

const payloadObject = computed(() => {
  const o = {}
  for (const e of flagEntries.value) {
    if (e.key && String(e.key).trim()) {
      o[String(e.key).trim()] = Boolean(e.boolValue)
    }
  }
  return o
})

async function loadTenants() {
  const { data } = await platformAPI.tenants.list({ page_size: 500 })
  tenants.value = data.results || data || []
}

function syncEntriesFromFlags(obj) {
  const src = obj && typeof obj === 'object' ? obj : {}
  flagEntries.value = Object.entries(src).map(([key, val]) => ({ key, boolValue: Boolean(val) }))
}

async function loadFlags() {
  if (!selectedTenantId.value) return
  flagsLoading.value = true
  bannerError.value = null
  try {
    const { data } = await platformAPI.tenantFeatureFlags.get(selectedTenantId.value)
    flags.value = data && typeof data === 'object' ? data : {}
    syncEntriesFromFlags(flags.value)
  } catch (e) {
    bannerError.value = normalizeApiError(e).userMessage || 'Could not load flags'
    syncEntriesFromFlags({})
  } finally {
    flagsLoading.value = false
  }
}

function onTenantChange() {
  loadFlags()
}

function addFlag() {
  const k = (newKey.value || '').trim()
  if (!k) return
  const list = [...flagEntries.value]
  const idx = list.findIndex((e) => e.key === k)
  if (idx >= 0) list[idx] = { ...list[idx], boolValue: Boolean(newVal.value) }
  else list.push({ key: k, boolValue: Boolean(newVal.value) })
  flagEntries.value = list
  newKey.value = ''
  newVal.value = false
}

async function saveFlags() {
  if (!selectedTenantId.value) return
  saving.value = true
  bannerError.value = null
  try {
    await platformAPI.tenantFeatureFlags.update(selectedTenantId.value, payloadObject.value)
    await loadFlags()
  } catch (e) {
    bannerError.value = normalizeApiError(e).userMessage || 'Save failed'
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  loading.value = true
  try {
    await loadTenants()
  } catch (e) {
    bannerError.value = normalizeApiError(e).userMessage || 'Could not load tenants'
  } finally {
    loading.value = false
  }
})
</script>
