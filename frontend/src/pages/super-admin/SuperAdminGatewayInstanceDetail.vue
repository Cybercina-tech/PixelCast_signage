<template>
  <div class="space-y-6">
    <div class="flex flex-wrap justify-between items-center gap-4">
      <div>
        <router-link to="/super-admin/gateway-instances" class="btn-outline px-3 py-1 rounded-lg text-sm mb-2 inline-block">
          ← Instances
        </router-link>
        <h1 class="text-2xl font-bold text-primary">{{ detail?.domain || 'Gateway instance' }}</h1>
        <p v-if="detail" class="text-sm text-muted mt-1 font-mono text-xs">{{ detail.id }}</p>
      </div>
      <button type="button" class="btn-outline px-4 py-2 rounded-lg text-sm" :disabled="loading" @click="load">Refresh</button>
    </div>

    <p v-if="loadError" class="text-sm text-amber-300 rounded-xl border border-amber-500/40 bg-amber-500/10 px-4 py-3">{{ loadError }}</p>

    <div v-if="loading" class="card-base rounded-2xl p-8 animate-pulse h-40" />
    <template v-else-if="detail">
      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div class="card-base rounded-2xl p-4 border border-border-color/80">
          <p class="text-xs text-muted uppercase">Status</p>
          <p class="text-lg font-bold text-primary mt-1">{{ detail.license_status }}</p>
        </div>
        <div class="card-base rounded-2xl p-4 border border-border-color/80">
          <p class="text-xs text-muted uppercase">Online</p>
          <p class="text-lg font-bold mt-1" :class="detail.is_online ? 'text-emerald-500' : 'text-rose-500'">
            {{ detail.is_online ? 'Yes' : 'No' }}
          </p>
        </div>
        <div class="card-base rounded-2xl p-4 border border-border-color/80">
          <p class="text-xs text-muted uppercase">Screens</p>
          <p class="text-lg font-bold text-primary mt-1">{{ detail.active_screens ?? '—' }}</p>
        </div>
        <div class="card-base rounded-2xl p-4 border border-border-color/80">
          <p class="text-xs text-muted uppercase">Version</p>
          <p class="text-lg font-bold text-primary mt-1">{{ detail.version || '—' }}</p>
        </div>
      </div>

      <Card title="Usage history">
        <Chart v-if="usageChart" type="line" :data="usageChart" :options="chartOptions" class="h-64" />
        <p v-else class="text-sm text-muted py-8 text-center">No usage reports yet</p>
      </Card>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import Card from '@/components/common/Card.vue'
import Chart from '@/components/common/Chart.vue'
import { platformAPI } from '@/services/api'

const route = useRoute()
const loading = ref(false)
const loadError = ref('')
const detail = ref(null)
const usageRows = ref([])

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  scales: { x: { ticks: { maxTicksLimit: 8 } } },
}

const usageChart = computed(() => {
  const rows = [...usageRows.value].reverse()
  if (!rows.length) return null
  return {
    labels: rows.map((r) => {
      try {
        return new Date(r.reported_at).toLocaleDateString()
      } catch {
        return r.reported_at
      }
    }),
    datasets: [
      {
        label: 'Active screens',
        data: rows.map((r) => r.active_screens ?? 0),
        borderColor: 'rgb(6, 182, 212)',
        backgroundColor: 'rgba(6, 182, 212, 0.12)',
        fill: true,
        tension: 0.3,
      },
    ],
  }
})

async function load() {
  const id = route.params.id
  if (!id) return
  loading.value = true
  loadError.value = ''
  try {
    const [detailRes, usageRes] = await Promise.all([
      platformAPI.gatewayInstances.detail(id),
      platformAPI.gatewayInstances.usage(id, { limit: 100 }),
    ])
    detail.value = detailRes.data
    usageRows.value = usageRes.data?.results || []
  } catch (e) {
    loadError.value = e.response?.data?.detail || e.message || 'Failed to load instance'
    detail.value = null
    usageRows.value = []
  } finally {
    loading.value = false
  }
}

onMounted(load)
watch(() => route.params.id, load)
</script>
