<template>
  <div class="space-y-8">
    <div class="flex flex-wrap justify-between items-center gap-4">
      <div>
        <h1 class="text-2xl font-bold text-primary">Reports</h1>
        <p class="text-sm text-muted mt-1">Cohorts, capacity, and plan mix</p>
      </div>
      <button type="button" class="btn-outline px-4 py-2 rounded-lg text-sm" :disabled="loading" @click="load">Refresh</button>
    </div>

    <div
      v-if="loadError"
      class="rounded-2xl border border-amber-500/40 bg-amber-500/10 px-4 py-3 text-sm text-amber-900 dark:text-amber-100"
    >
      {{ loadError }}
    </div>

    <div v-if="loading" class="grid gap-4 lg:grid-cols-2">
      <div v-for="i in 4" :key="i" class="card-base rounded-2xl p-6 animate-pulse h-40" />
    </div>

    <template v-else>
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Plan distribution">
          <Chart v-if="planChartData" type="doughnut" :data="planChartData" :options="chartOptionsDoughnut" />
          <p v-else class="text-sm text-muted">No plan data</p>
        </Card>
        <Card title="Platform snapshot">
          <dl v-if="overview" class="text-sm space-y-2">
            <div class="flex justify-between gap-2">
              <dt class="text-muted">Tenants (overview)</dt>
              <dd class="text-primary font-medium">{{ overview.counts?.tenants }}</dd>
            </div>
            <div v-if="tenantDirectoryCount != null" class="flex justify-between gap-2">
              <dt class="text-muted">Tenants (directory)</dt>
              <dd class="text-primary font-medium">{{ tenantDirectoryCount }}</dd>
            </div>
            <div class="flex justify-between gap-2">
              <dt class="text-muted">Paying w/ subscription</dt>
              <dd class="text-primary font-medium">{{ overview.counts?.paying_with_subscription }}</dd>
            </div>
            <div class="flex justify-between gap-2">
              <dt class="text-muted">Avg health</dt>
              <dd class="text-primary font-medium">{{ overview.health?.average_score }}</dd>
            </div>
          </dl>
          <p v-else class="text-sm text-muted">Overview unavailable</p>
        </Card>
      </div>

      <Card title="Cohorts (signup month)">
        <div class="overflow-x-auto">
          <table class="min-w-full text-sm">
            <thead>
              <tr class="border-b border-border-color text-left text-muted">
                <th class="py-2 pr-4">Month</th>
                <th class="py-2 pr-4">Signed up</th>
                <th class="py-2 pr-4">Still entitled</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in cohortRows" :key="row.month" class="border-b border-border-color/60">
                <td class="py-2 pr-4 text-primary font-medium">{{ row.month }}</td>
                <td class="py-2 pr-4">{{ row.signed_up }}</td>
                <td class="py-2 pr-4">{{ row.still_entitled }}</td>
              </tr>
              <tr v-if="!cohortRows.length">
                <td colspan="3" class="py-6 text-center text-muted">No cohort data</td>
              </tr>
            </tbody>
          </table>
        </div>
      </Card>

      <Card title="Capacity by tenant">
        <div class="overflow-x-auto">
          <table class="min-w-full text-sm">
            <thead>
              <tr class="border-b border-border-color text-left text-muted">
                <th class="py-2 pr-4">Tenant</th>
                <th class="py-2 pr-4">Screens</th>
                <th class="py-2 pr-4">Users</th>
                <th class="py-2 pr-4">Device limit</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in capacityRows" :key="row.id" class="border-b border-border-color/60">
                <td class="py-2 pr-4 text-primary font-medium">{{ row.name }}</td>
                <td class="py-2 pr-4">{{ row.screen_count }}</td>
                <td class="py-2 pr-4">{{ row.user_count }}</td>
                <td class="py-2 pr-4">{{ row.device_limit ?? '—' }}</td>
              </tr>
              <tr v-if="!capacityRows.length">
                <td colspan="4" class="py-6 text-center text-muted">No capacity rows</td>
              </tr>
            </tbody>
          </table>
        </div>
      </Card>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import Card from '@/components/common/Card.vue'
import Chart from '@/components/common/Chart.vue'
import api, { platformAPI } from '@/services/api'
import { normalizeApiError } from '@/utils/apiError'

const loading = ref(true)
const loadError = ref(null)
const overview = ref(null)
const cohortRows = ref([])
const capacityRows = ref([])
const tenantDirectoryCount = ref(null)

const chartOptionsDoughnut = {
  plugins: { legend: { position: 'bottom', labels: { color: '#94a3b8' } } },
}

const planChartData = computed(() => {
  const rows = overview.value?.charts?.plan_distribution
  if (!rows?.length) return null
  const palette = ['#06b6d4', '#8b5cf6', '#ec4899', '#f97316', '#22c55e', '#eab308']
  return {
    labels: rows.map((r) => r.plan),
    datasets: [
      {
        data: rows.map((r) => r.count),
        backgroundColor: rows.map((_, i) => palette[i % palette.length]),
      },
    ],
  }
})

async function load() {
  loading.value = true
  loadError.value = null
  try {
    const [ov, co, cap, tenants] = await Promise.all([
      platformAPI.overview(),
      api.get('/platform/cohorts/'),
      api.get('/platform/capacity/'),
      platformAPI.tenants.list({ page_size: 1 }),
    ])
    overview.value = ov.data
    cohortRows.value = co.data?.cohorts || []
    capacityRows.value = cap.data?.tenants || []
    const d = tenants.data
    tenantDirectoryCount.value = d?.count ?? (d?.results || []).length ?? null
  } catch (e) {
    loadError.value = normalizeApiError(e).userMessage || 'Could not load reports'
    overview.value = null
    cohortRows.value = []
    capacityRows.value = []
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>
