<template>
  <div class="space-y-6">
    <div class="flex flex-wrap items-center justify-between gap-4">
      <p class="text-sm text-muted">Metrics from server aggregates (not full ticket list).</p>
      <label class="flex items-center gap-2 text-sm text-muted">
        <span>Period</span>
        <select v-model.number="days" class="select-base px-3 py-2 rounded-lg text-sm" @change="load">
          <option :value="7">7 days</option>
          <option :value="30">30 days</option>
          <option :value="90">90 days</option>
        </select>
      </label>
    </div>

    <div v-if="loading" class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <div v-for="i in 4" :key="i" class="card-base rounded-2xl p-6 animate-pulse h-28" />
    </div>

    <div v-else-if="error" class="rounded-2xl border border-amber-500/40 bg-amber-500/10 px-4 py-3 text-sm text-amber-300">
      {{ error }}
    </div>

    <template v-else>
      <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <div class="card-base rounded-2xl p-5 border border-border-color/80">
          <p class="text-xs font-medium text-muted uppercase tracking-wide">Total tickets</p>
          <p class="text-3xl font-bold text-primary mt-1">{{ stats.total }}</p>
        </div>
        <div class="card-base rounded-2xl p-5 border border-border-color/80">
          <p class="text-xs font-medium text-muted uppercase tracking-wide">Open tickets</p>
          <p class="text-3xl font-bold text-primary mt-1">{{ stats.open_count }}</p>
        </div>
        <div class="card-base rounded-2xl p-5 border border-border-color/80">
          <p class="text-xs font-medium text-muted uppercase tracking-wide">Avg first response</p>
          <p class="text-3xl font-bold text-primary mt-1">{{ formatDuration(stats.avg_first_response_min) }}</p>
        </div>
        <div class="card-base rounded-2xl p-5 border border-border-color/80">
          <p class="text-xs font-medium text-muted uppercase tracking-wide">Avg resolution</p>
          <p class="text-3xl font-bold text-primary mt-1">{{ formatDuration(stats.avg_resolution_min) }}</p>
        </div>
      </div>

      <div class="card-base rounded-2xl p-5 border border-border-color/80">
        <p class="text-xs font-medium text-muted uppercase tracking-wide">SLA compliance</p>
        <p class="text-3xl font-bold text-primary mt-1">{{ stats.sla_compliance_pct }}%</p>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Tickets by status">
          <div class="space-y-2">
            <div v-for="s in stats.by_status" :key="s.status" class="flex items-center justify-between text-sm">
              <span class="capitalize text-secondary">{{ (s.status || '').replace(/_/g, ' ') || '—' }}</span>
              <span class="font-semibold text-primary">{{ s.count }}</span>
            </div>
            <p v-if="!stats.by_status?.length" class="text-sm text-muted">No data</p>
          </div>
        </Card>
        <Card title="Tickets by priority">
          <div class="space-y-2">
            <div v-for="p in stats.by_priority" :key="p.priority" class="flex items-center justify-between text-sm">
              <span class="capitalize text-secondary">{{ p.priority || '—' }}</span>
              <span class="font-semibold text-primary">{{ p.count }}</span>
            </div>
            <p v-if="!stats.by_priority?.length" class="text-sm text-muted">No data</p>
          </div>
        </Card>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Tickets by category">
          <div class="space-y-2 max-h-64 overflow-y-auto">
            <div v-for="c in stats.by_category" :key="c.category || 'empty'" class="flex items-center justify-between text-sm">
              <span class="text-secondary truncate pr-2" :title="c.category || '(uncategorized)'">
                {{ c.category || '(uncategorized)' }}
              </span>
              <span class="font-semibold text-primary shrink-0">{{ c.count }}</span>
            </div>
            <p v-if="!stats.by_category?.length" class="text-sm text-muted">No data</p>
          </div>
        </Card>
        <Card title="Top tenants by volume">
          <div class="space-y-2 max-h-64 overflow-y-auto">
            <div v-for="t in stats.by_tenant" :key="t['tenant__name']" class="flex items-center justify-between text-sm">
              <span class="text-secondary truncate pr-2">{{ t['tenant__name'] || '—' }}</span>
              <span class="font-semibold text-primary shrink-0">{{ t.count }}</span>
            </div>
            <p v-if="!stats.by_tenant?.length" class="text-sm text-muted">No data</p>
          </div>
        </Card>
      </div>

      <Card v-if="stats.resolution_by_deployment?.length" title="Avg resolution by deployment context">
        <div class="space-y-2 max-h-48 overflow-y-auto text-sm">
          <div
            v-for="d in stats.resolution_by_deployment"
            :key="d.deployment_context || 'empty'"
            class="flex items-center justify-between gap-2"
          >
            <span class="text-secondary capitalize">{{ d.deployment_context || '—' }}</span>
            <span class="font-semibold text-primary">{{ formatDuration(d.avg_resolution_min) }}</span>
          </div>
        </div>
      </Card>

      <div v-if="stats.by_client_version?.length" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Tickets by reported app version">
          <div class="space-y-2 max-h-64 overflow-y-auto">
            <div v-for="v in stats.by_client_version" :key="v.client_version || 'empty'" class="flex items-center justify-between text-sm">
              <span class="font-mono text-xs text-secondary truncate pr-2">{{ v.client_version || '(unknown)' }}</span>
              <span class="font-semibold text-primary shrink-0">{{ v.count }}</span>
            </div>
          </div>
        </Card>
        <Card title="Avg resolution by reported version">
          <div class="space-y-2 max-h-64 overflow-y-auto">
            <div
              v-for="v in stats.resolution_by_client_version"
              :key="v.client_version || 'empty'"
              class="flex items-center justify-between text-sm"
            >
              <span class="font-mono text-xs text-secondary truncate pr-2">{{ v.client_version || '(unknown)' }}</span>
              <span class="font-semibold text-primary shrink-0">{{ formatDuration(v.avg_resolution_min) }}</span>
            </div>
            <p v-if="!stats.resolution_by_client_version?.length" class="text-sm text-muted">No resolved tickets with version</p>
          </div>
        </Card>
      </div>

      <Card title="CSAT distribution">
        <div class="flex items-center gap-4 text-sm flex-wrap">
          <div v-for="n in 5" :key="n" class="text-center">
            <p class="text-lg font-bold text-primary">{{ csatCount(n) }}</p>
            <p class="text-muted">{{ n }} star{{ n > 1 ? 's' : '' }}</p>
          </div>
        </div>
        <p class="text-sm text-muted mt-2">Average: {{ stats.avg_csat != null ? stats.avg_csat.toFixed(1) : '—' }}/5</p>
      </Card>
    </template>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import Card from '@/components/common/Card.vue'
import { platformTicketsAPI } from '@/services/api'
import { normalizeApiError } from '@/utils/apiError'

const loading = ref(true)
const error = ref(null)
const days = ref(30)
const stats = ref({
  total: 0,
  open_count: 0,
  avg_first_response_min: null,
  avg_resolution_min: null,
  sla_compliance_pct: 0,
  by_status: [],
  by_priority: [],
  by_category: [],
  by_tenant: [],
  by_client_version: [],
  resolution_by_client_version: [],
  resolution_by_deployment: [],
  csat_distribution: {},
  avg_csat: null,
})

function csatCount(n) {
  const d = stats.value.csat_distribution || {}
  return d[n] ?? d[String(n)] ?? 0
}

function formatDuration(minutes) {
  if (minutes == null) return '—'
  if (minutes < 60) return `${Math.round(minutes)}m`
  const h = Math.floor(minutes / 60)
  const m = Math.round(minutes % 60)
  return m > 0 ? `${h}h ${m}m` : `${h}h`
}

async function load() {
  loading.value = true
  error.value = null
  try {
    const { data } = await platformTicketsAPI.analytics({ days: days.value })
    stats.value = {
      total: data.total ?? 0,
      open_count: data.open_count ?? 0,
      avg_first_response_min: data.avg_first_response_min ?? null,
      avg_resolution_min: data.avg_resolution_min ?? null,
      sla_compliance_pct: data.sla_compliance_pct ?? 0,
      by_status: data.by_status || [],
      by_priority: data.by_priority || [],
      by_category: data.by_category || [],
      by_tenant: data.by_tenant || [],
      by_client_version: data.by_client_version || [],
      resolution_by_client_version: data.resolution_by_client_version || [],
      resolution_by_deployment: data.resolution_by_deployment || [],
      csat_distribution: data.csat_distribution || {},
      avg_csat: data.avg_csat ?? null,
    }
  } catch (e) {
    error.value = normalizeApiError(e).userMessage || 'Could not load analytics'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>
