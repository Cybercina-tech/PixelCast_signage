<template>
  <div class="space-y-6">
    <div class="flex flex-wrap justify-between items-center gap-4">
      <div>
        <h1 class="text-2xl font-bold text-primary">Global devices</h1>
        <p class="text-sm text-muted mt-1">Screens across all tenants (requires developer access)</p>
      </div>
      <button type="button" class="btn-outline px-4 py-2 rounded-lg text-sm" :disabled="loading" @click="load">
        Refresh
      </button>
    </div>

    <div
      v-if="loadError"
      class="rounded-2xl border border-amber-500/40 bg-amber-500/10 px-4 py-3 text-sm text-amber-900 dark:text-amber-100"
    >
      {{ loadError }}
    </div>

    <div v-if="loading" class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <div v-for="i in 4" :key="i" class="card-base rounded-2xl p-6 animate-pulse h-24" />
    </div>

    <template v-else>
      <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <div class="card-base rounded-2xl p-5 border border-border-color/80">
          <p class="text-xs font-medium text-muted uppercase tracking-wide">Total screens</p>
          <p class="text-3xl font-bold text-primary mt-1">{{ kpis.total }}</p>
        </div>
        <div class="card-base rounded-2xl p-5 border border-border-color/80">
          <p class="text-xs font-medium text-muted uppercase tracking-wide">Online</p>
          <p class="text-3xl font-bold text-primary mt-1">{{ kpis.online }}</p>
        </div>
        <div class="card-base rounded-2xl p-5 border border-border-color/80">
          <p class="text-xs font-medium text-muted uppercase tracking-wide">Offline</p>
          <p class="text-3xl font-bold text-primary mt-1">{{ kpis.offline }}</p>
        </div>
        <div class="card-base rounded-2xl p-5 border border-border-color/80">
          <p class="text-xs font-medium text-muted uppercase tracking-wide">Error / stale</p>
          <p class="text-3xl font-bold text-primary mt-1">{{ kpis.error }}</p>
        </div>
      </div>

      <Card>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-4">
          <div>
            <label class="label-base block text-sm mb-1">Tenant</label>
            <select v-model="tenantId" class="select-base w-full px-3 py-2 rounded-lg" @change="applyFilters">
              <option value="">All tenants</option>
              <option v-for="t in tenantOptions" :key="t.id" :value="t.id">{{ t.name }}</option>
            </select>
            <p class="text-[11px] text-muted mt-1">Server list may not filter by tenant yet; selection narrows when supported.</p>
          </div>
          <div>
            <label class="label-base block text-sm mb-1">Status</label>
            <select v-model="statusFilter" class="select-base w-full px-3 py-2 rounded-lg" @change="applyFilters">
              <option value="all">All</option>
              <option value="online">Online</option>
              <option value="offline">Offline</option>
            </select>
          </div>
        </div>

        <div v-if="!filteredScreens.length" class="text-center py-12 text-muted">No screens match</div>
        <div v-else class="space-y-4">
          <div class="grid gap-3 lg:hidden">
            <article
              v-for="s in filteredScreens"
              :key="`m-${s.id}`"
              class="rounded-xl border border-border-color/70 bg-card/50 p-4 space-y-2"
            >
              <div class="flex justify-between gap-2">
                <h3 class="font-semibold text-primary">{{ s.name }}</h3>
                <span class="text-[11px] px-2 py-1 rounded-full border shrink-0" :class="statusBadgeClass(s)">
                  {{ statusLabel(s) }}
                </span>
              </div>
              <p class="text-xs text-muted">Tenant: {{ tenantColumn(s) }}</p>
              <p class="text-xs text-secondary">Heartbeat: {{ formatDate(s.last_heartbeat_at) }}</p>
              <p class="text-xs text-secondary">App: {{ s.app_version || '—' }}</p>
            </article>
          </div>

          <div class="hidden lg:block overflow-x-auto">
            <table class="min-w-full text-sm">
              <thead>
                <tr class="border-b border-border-color text-left text-muted">
                  <th class="py-2 pr-4">Screen</th>
                  <th class="py-2 pr-4">Tenant</th>
                  <th class="py-2 pr-4">Status</th>
                  <th class="py-2 pr-4">Last heartbeat</th>
                  <th class="py-2 pr-4">App version</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="s in filteredScreens"
                  :key="s.id"
                  class="border-b border-border-color/60 hover:bg-slate-50/50 dark:hover:bg-slate-800/30"
                >
                  <td class="py-2 pr-4 font-medium text-primary">{{ s.name }}</td>
                  <td class="py-2 pr-4 text-secondary text-xs">{{ tenantColumn(s) }}</td>
                  <td class="py-2 pr-4">
                    <span class="text-[11px] px-2 py-1 rounded-full border" :class="statusBadgeClass(s)">
                      {{ statusLabel(s) }}
                    </span>
                  </td>
                  <td class="py-2 pr-4 text-muted text-xs whitespace-nowrap">{{ formatDate(s.last_heartbeat_at) }}</td>
                  <td class="py-2 pr-4 text-secondary">{{ s.app_version || '—' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </Card>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import Card from '@/components/common/Card.vue'
import api, { platformAPI } from '@/services/api'
import { normalizeApiError } from '@/utils/apiError'

const loading = ref(true)
const loadError = ref(null)
const screens = ref([])
const tenantNameById = ref({})
const tenantId = ref('')
const statusFilter = ref('all')

const tenantOptions = computed(() =>
  Object.entries(tenantNameById.value).map(([id, name]) => ({ id, name })),
)

const kpis = computed(() => {
  const list = screens.value
  let online = 0
  let offline = 0
  let err = 0
  for (const s of list) {
    if (s.is_heartbeat_stale) err += 1
    if (s.is_online) online += 1
    else offline += 1
  }
  return { total: list.length, online, offline, error: err }
})

const filteredScreens = computed(() => {
  let list = screens.value
  if (statusFilter.value === 'online') list = list.filter((s) => s.is_online)
  else if (statusFilter.value === 'offline') list = list.filter((s) => !s.is_online)
  return list
})

function statusLabel(s) {
  if (s.is_heartbeat_stale) return 'Error'
  if (s.is_online) return 'Online'
  return 'Offline'
}

function statusBadgeClass(s) {
  if (s.is_heartbeat_stale) return 'border-amber-500/50 text-amber-700 dark:text-amber-200'
  if (s.is_online) return 'border-emerald-500/40 text-emerald-700 dark:text-emerald-200'
  return 'border-slate-500/40 text-muted'
}

function tenantColumn(s) {
  return s.tenant_name || s.owner_organization_name || '—'
}

function formatDate(iso) {
  if (!iso) return '—'
  try {
    return new Date(iso).toLocaleString()
  } catch {
    return iso
  }
}

async function fetchTenantsMap() {
  const { data } = await platformAPI.tenants.list({ page_size: 500 })
  const map = {}
  const list = data.results || data || []
  for (const t of list) {
    map[String(t.id)] = t.name
  }
  tenantNameById.value = map
}

async function fetchAllScreens() {
  const acc = []
  let page = 1
  const params = { page_size: 100 }
  if (tenantId.value) params.tenant_id = tenantId.value
  for (;;) {
    const { data } = await api.get('/screens/', { params: { ...params, page } })
    const chunk = data.results || []
    acc.push(...chunk)
    if (!data.next || !chunk.length) break
    page += 1
    if (page > 200) break
  }
  return acc
}

function applyFilters() {
  load()
}

async function load() {
  loading.value = true
  loadError.value = null
  try {
    await fetchTenantsMap()
    screens.value = await fetchAllScreens()
  } catch (e) {
    loadError.value = normalizeApiError(e).userMessage || 'Could not load screens'
    screens.value = []
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  load()
})
</script>
