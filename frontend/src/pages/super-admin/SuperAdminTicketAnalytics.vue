<template>
  <div class="space-y-6">
    <div v-if="loading" class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <div v-for="i in 4" :key="i" class="card-base rounded-2xl p-6 animate-pulse h-28" />
    </div>

    <div v-else-if="error" class="rounded-2xl border border-amber-500/40 bg-amber-500/10 px-4 py-3 text-sm text-amber-300">
      {{ error }}
    </div>

    <template v-else>
      <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <div class="card-base rounded-2xl p-5 border border-border-color/80">
          <p class="text-xs font-medium text-muted uppercase tracking-wide">Open Tickets</p>
          <p class="text-3xl font-bold text-primary mt-1">{{ stats.open_count }}</p>
        </div>
        <div class="card-base rounded-2xl p-5 border border-border-color/80">
          <p class="text-xs font-medium text-muted uppercase tracking-wide">Avg First Response</p>
          <p class="text-3xl font-bold text-primary mt-1">{{ formatDuration(stats.avg_first_response_min) }}</p>
        </div>
        <div class="card-base rounded-2xl p-5 border border-border-color/80">
          <p class="text-xs font-medium text-muted uppercase tracking-wide">Avg Resolution</p>
          <p class="text-3xl font-bold text-primary mt-1">{{ formatDuration(stats.avg_resolution_min) }}</p>
        </div>
        <div class="card-base rounded-2xl p-5 border border-border-color/80">
          <p class="text-xs font-medium text-muted uppercase tracking-wide">SLA Compliance</p>
          <p class="text-3xl font-bold text-primary mt-1">{{ stats.sla_compliance_pct }}%</p>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Tickets by Status">
          <div class="space-y-2">
            <div v-for="s in stats.by_status" :key="s.status" class="flex items-center justify-between text-sm">
              <span class="capitalize text-secondary">{{ s.status.replace('_', ' ') }}</span>
              <span class="font-semibold text-primary">{{ s.count }}</span>
            </div>
            <p v-if="!stats.by_status?.length" class="text-sm text-muted">No data</p>
          </div>
        </Card>
        <Card title="Tickets by Priority">
          <div class="space-y-2">
            <div v-for="p in stats.by_priority" :key="p.priority" class="flex items-center justify-between text-sm">
              <span class="capitalize text-secondary">{{ p.priority }}</span>
              <span class="font-semibold text-primary">{{ p.count }}</span>
            </div>
            <p v-if="!stats.by_priority?.length" class="text-sm text-muted">No data</p>
          </div>
        </Card>
      </div>

      <Card title="CSAT Distribution">
        <div class="flex items-center gap-4 text-sm">
          <div v-for="n in 5" :key="n" class="text-center">
            <p class="text-lg font-bold text-primary">{{ stats.csat_distribution?.[n] || 0 }}</p>
            <p class="text-muted">{{ n }} star{{ n > 1 ? 's' : '' }}</p>
          </div>
        </div>
        <p class="text-sm text-muted mt-2">Average: {{ stats.avg_csat?.toFixed(1) || '—' }}/5</p>
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
const stats = ref({
  open_count: 0,
  avg_first_response_min: null,
  avg_resolution_min: null,
  sla_compliance_pct: 0,
  by_status: [],
  by_priority: [],
  csat_distribution: {},
  avg_csat: null,
})

function formatDuration(minutes) {
  if (minutes == null) return '—'
  if (minutes < 60) return `${Math.round(minutes)}m`
  const h = Math.floor(minutes / 60)
  const m = Math.round(minutes % 60)
  return m > 0 ? `${h}h ${m}m` : `${h}h`
}

onMounted(async () => {
  loading.value = true
  try {
    const { data } = await platformTicketsAPI.list({ status: 'open' })
    stats.value.open_count = Array.isArray(data) ? data.length : 0
    const allRes = await platformTicketsAPI.list()
    const all = Array.isArray(allRes.data) ? allRes.data : []
    const statusCounts = {}
    const priorityCounts = {}
    for (const t of all) {
      statusCounts[t.status] = (statusCounts[t.status] || 0) + 1
      priorityCounts[t.priority] = (priorityCounts[t.priority] || 0) + 1
    }
    stats.value.by_status = Object.entries(statusCounts).map(([status, count]) => ({ status, count }))
    stats.value.by_priority = Object.entries(priorityCounts).map(([priority, count]) => ({ priority, count }))
  } catch (e) {
    error.value = normalizeApiError(e).userMessage || 'Could not load analytics'
  } finally {
    loading.value = false
  }
})
</script>
