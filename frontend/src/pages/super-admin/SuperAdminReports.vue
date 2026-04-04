<template>
  <div class="space-y-6">
    <div class="flex flex-wrap justify-between items-center gap-4">
      <div>
        <h1 class="text-2xl font-bold text-primary">Reports</h1>
        <p class="text-sm text-muted mt-1">Platform overview, registry, usage, and health</p>
      </div>
      <button type="button" class="btn-outline px-4 py-2 rounded-lg text-sm" :disabled="loading" @click="load">
        Refresh
      </button>
    </div>

    <div class="flex flex-wrap gap-2 border-b border-border-color/80 pb-2">
      <button
        v-for="t in tabs"
        :key="t.id"
        type="button"
        class="px-3 py-1.5 rounded-lg text-sm transition-colors"
        :class="
          activeTab === t.id
            ? 'bg-cyan-500/15 text-primary border border-cyan-500/30'
            : 'text-muted hover:text-primary border border-transparent'
        "
        @click="activeTab = t.id"
      >
        {{ t.label }}
      </button>
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
      <!-- Overview -->
      <div v-show="activeTab === 'overview'" class="space-y-6">
        <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
          <div class="card-base rounded-2xl p-5 border border-border-color/80">
            <p class="text-xs font-medium text-muted uppercase tracking-wide">Registry purchases</p>
            <p class="text-3xl font-bold text-primary mt-1">{{ summary?.self_hosted?.purchases_count ?? '—' }}</p>
          </div>
          <div class="card-base rounded-2xl p-5 border border-border-color/80">
            <p class="text-xs font-medium text-muted uppercase tracking-wide">Installs (heartbeat 30d)</p>
            <p class="text-3xl font-bold text-primary mt-1">{{ summary?.self_hosted?.heartbeats_last_30d_installs ?? '—' }}</p>
          </div>
          <div class="card-base rounded-2xl p-5 border border-border-color/80">
            <p class="text-xs font-medium text-muted uppercase tracking-wide">SaaS online users</p>
            <p class="text-3xl font-bold text-primary mt-1">{{ summary?.saas?.active_online_users_sum ?? '—' }}</p>
          </div>
          <div class="card-base rounded-2xl p-5 border border-border-color/80">
            <p class="text-xs font-medium text-muted uppercase tracking-wide">Installs online (~15m)</p>
            <p class="text-3xl font-bold text-primary mt-1">{{ summary?.self_hosted?.installations_online_recent_minutes_15 ?? '—' }}</p>
          </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card title="SaaS revenue (paid invoices, 12m)">
            <Chart v-if="revenueChartData" type="line" :data="revenueChartData" :options="chartOptionsLine" />
            <p v-else class="text-sm text-muted">No revenue data</p>
            <p class="text-xs text-muted mt-2">MRR est. from overview: {{ formatMoney(overview?.revenue?.mrr_estimate_cents) }}</p>
          </Card>
          <Card title="Self-hosted activations by month">
            <Chart v-if="activationChartData" type="line" :data="activationChartData" :options="chartOptionsLineAlt" />
            <p v-else class="text-sm text-muted">No activation data</p>
          </Card>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <router-link
            to="/super-admin/self-hosted-licenses"
            class="card-base rounded-2xl p-5 border border-border-color/80 hover:border-violet-500/30 block"
          >
            <h3 class="font-semibold text-primary">Self-hosted licenses</h3>
            <p class="text-sm text-muted mt-1">Installations, telemetry, actions</p>
          </router-link>
          <router-link
            to="/super-admin/tickets/analytics"
            class="card-base rounded-2xl p-5 border border-border-color/80 hover:border-violet-500/30 block"
          >
            <h3 class="font-semibold text-primary">Ticket analytics</h3>
            <p class="text-sm text-muted mt-1">SLA, CSAT, categories, versions</p>
          </router-link>
        </div>

        <p v-if="summary?.revenue?.license_estimate_note" class="text-xs text-muted">{{ summary.revenue.license_estimate_note }}</p>
        <p v-if="summary?.revenue?.license_estimate_cents != null" class="text-sm text-secondary">
          License revenue estimate: {{ formatMoney(summary.revenue.license_estimate_cents) }}
        </p>
      </div>

      <!-- SaaS cohorts & capacity (existing) -->
      <div v-show="activeTab === 'saas'" class="space-y-6">
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
                  <th class="py-2 pr-4">Active users</th>
                  <th class="py-2 pr-4">Device limit</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in capacityRows" :key="row.id" class="border-b border-border-color/60">
                  <td class="py-2 pr-4 text-primary font-medium">{{ row.name }}</td>
                  <td class="py-2 pr-4">{{ row.screen_count }}</td>
                  <td class="py-2 pr-4">{{ row.user_count }}</td>
                  <td class="py-2 pr-4">{{ row.active_user_count ?? '—' }}</td>
                  <td class="py-2 pr-4">{{ row.device_limit ?? '—' }}</td>
                </tr>
                <tr v-if="!capacityRows.length">
                  <td colspan="5" class="py-6 text-center text-muted">No capacity rows</td>
                </tr>
              </tbody>
            </table>
          </div>
        </Card>
      </div>

      <!-- Usage -->
      <div v-show="activeTab === 'usage'" class="space-y-6">
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <Card title="SaaS averages">
            <dl class="text-sm space-y-2">
              <div class="flex justify-between gap-2">
                <dt class="text-muted">Screens / tenant</dt>
                <dd class="text-primary font-medium">{{ summary?.saas?.avg_screens_per_tenant ?? '—' }}</dd>
              </div>
              <div class="flex justify-between gap-2">
                <dt class="text-muted">Templates / tenant</dt>
                <dd class="text-primary font-medium">{{ summary?.saas?.avg_templates_per_tenant ?? '—' }}</dd>
              </div>
            </dl>
          </Card>
          <Card title="Registry telemetry (reported)">
            <dl class="text-sm space-y-2">
              <div class="flex justify-between gap-2">
                <dt class="text-muted">Avg screens / install</dt>
                <dd class="text-primary font-medium">{{ summary?.self_hosted?.avg_reported_screens_per_install ?? '—' }}</dd>
              </div>
              <div class="flex justify-between gap-2">
                <dt class="text-muted">Avg users / install</dt>
                <dd class="text-primary font-medium">{{ summary?.self_hosted?.avg_reported_users_per_install ?? '—' }}</dd>
              </div>
            </dl>
          </Card>
          <Card title="SaaS vs self-hosted">
            <dl class="text-sm space-y-2">
              <div class="flex justify-between gap-2">
                <dt class="text-muted">Paying SaaS tenants</dt>
                <dd class="text-primary font-medium">{{ summary?.saas?.tenants_paying_with_subscription ?? '—' }}</dd>
              </div>
              <div class="flex justify-between gap-2">
                <dt class="text-muted">Active self-hosted (~heartbeat)</dt>
                <dd class="text-primary font-medium">{{ summary?.saas?.approx_active_self_hosted_installs ?? '—' }}</dd>
              </div>
            </dl>
            <p class="text-xs text-muted mt-2">{{ summary?.saas?.ratio_note }}</p>
          </Card>
        </div>
        <Card title="Usage proxies">
          <ul class="text-sm space-y-1 text-secondary">
            <li>Schedule rows (scheduling): {{ summary?.usage?.schedule_entities_total ?? '—' }}</li>
            <li>Tickets last 30d (helpdesk activity): {{ summary?.usage?.tickets_last_30d ?? '—' }}</li>
            <li>Screens (SaaS): {{ summary?.usage?.screens_total_saas ?? '—' }}</li>
            <li>Templates (SaaS): {{ summary?.usage?.templates_total_saas ?? '—' }}</li>
          </ul>
          <p class="text-xs text-muted mt-2">{{ summary?.usage?.note }}</p>
        </Card>
      </div>

      <!-- Versions -->
      <div v-show="activeTab === 'versions'" class="space-y-6">
        <Card title="Version distribution (self-hosted)">
          <Chart v-if="versionBarData" type="bar" :data="versionBarData" :options="chartOptionsBarH" />
          <p v-else class="text-sm text-muted">No version data</p>
          <p class="text-xs text-muted mt-2">
            Reference latest:
            <span class="font-mono text-primary">{{ summary?.self_hosted?.latest_version_reference || '—' }}</span>
            · On latest:
            {{ summary?.self_hosted?.on_latest_version_pct != null ? `${summary.self_hosted.on_latest_version_pct}%` : '—' }}
          </p>
        </Card>
        <Card title="Installations not on latest (sample)">
          <ul class="text-xs font-mono space-y-1 text-muted max-h-56 overflow-y-auto">
            <li v-for="r in summary?.self_hosted?.installations_behind_latest_sample || []" :key="r.id">
              {{ r.domain }} · {{ r.app_version }}
            </li>
            <li v-if="!(summary?.self_hosted?.installations_behind_latest_sample || []).length" class="text-muted">
              None or no latest version configured (set LICENSE_REGISTRY_LATEST_VERSION).
            </li>
          </ul>
        </Card>
      </div>

      <!-- Health -->
      <div v-show="activeTab === 'health'" class="space-y-6">
        <p class="text-sm text-muted">
          Inactive threshold: {{ summary?.self_hosted?.inactive_hours_threshold ?? '—' }}h · Sample inactive &gt;
          {{ inactiveDays }}d (query ?inactive_days= on API)
        </p>
        <Card title="Stale / missing heartbeat">
          <ul class="text-xs space-y-1 font-mono text-muted max-h-64 overflow-y-auto">
            <li v-for="r in summary?.self_hosted?.stale_heartbeat_installs || []" :key="r.id">
              {{ r.domain }} · {{ r.last_heartbeat_at || 'never' }}
            </li>
            <li v-if="!(summary?.self_hosted?.stale_heartbeat_installs || []).length">None in sample</li>
          </ul>
        </Card>
        <Card title="Inactive longer than sample window">
          <ul class="text-xs space-y-1 font-mono text-muted max-h-64 overflow-y-auto">
            <li v-for="r in summary?.self_hosted?.inactive_installs_sample || []" :key="r.id">
              {{ r.domain }} · {{ r.last_heartbeat_at || 'never' }}
            </li>
          </ul>
        </Card>
        <Card title="Purchase codes used on multiple domains">
          <ul class="text-xs space-y-1 text-muted max-h-48 overflow-y-auto">
            <li v-for="(p, i) in summary?.self_hosted?.purchases_with_multiple_domains || []" :key="i">
              {{ p.buyer_username || 'buyer' }} · {{ p.n }} installs
            </li>
            <li v-if="!(summary?.self_hosted?.purchases_with_multiple_domains || []).length">None detected</li>
          </ul>
        </Card>
      </div>

      <!-- Geography -->
      <div v-show="activeTab === 'geo'" class="space-y-6">
        <p class="text-sm text-muted">
          Country uses GeoIP when GEOIP2_COUNTRY_DATABASE is set; otherwise from reported telemetry only. Timezone comes from
          client heartbeat payload.
        </p>
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card title="Countries">
            <div class="space-y-2 max-h-72 overflow-y-auto text-sm">
              <div v-for="c in summary?.self_hosted?.country_distribution || []" :key="c.country" class="flex justify-between gap-2">
                <span class="text-secondary">{{ c.country }}</span>
                <span class="font-medium text-primary">{{ c.count }}</span>
              </div>
              <p v-if="!(summary?.self_hosted?.country_distribution || []).length" class="text-muted">No country data yet</p>
            </div>
          </Card>
          <Card title="Timezones">
            <div class="space-y-2 max-h-72 overflow-y-auto text-sm">
              <div v-for="z in summary?.self_hosted?.timezone_distribution || []" :key="z.timezone" class="flex justify-between gap-2">
                <span class="text-secondary font-mono text-xs truncate" :title="z.timezone">{{ z.timezone }}</span>
                <span class="font-medium text-primary shrink-0">{{ z.count }}</span>
              </div>
              <p v-if="!(summary?.self_hosted?.timezone_distribution || []).length" class="text-muted">No timezone data yet</p>
            </div>
          </Card>
        </div>
      </div>

      <!-- Support -->
      <div v-show="activeTab === 'support'" class="space-y-4">
        <p class="text-sm text-secondary">
          Open full analytics for charts and filters. Ticket fields <code class="text-xs">client_version</code> and
          <code class="text-xs">deployment_context</code> power version / deployment breakdowns when agents set them.
        </p>
        <router-link to="/super-admin/tickets/analytics" class="btn-primary inline-block px-4 py-2 rounded-lg text-sm">
          Open ticket analytics
        </router-link>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import Card from '@/components/common/Card.vue'
import Chart from '@/components/common/Chart.vue'
import api, { platformAPI } from '@/services/api'
import { normalizeApiError } from '@/utils/apiError'

const tabs = [
  { id: 'overview', label: 'Overview' },
  { id: 'saas', label: 'SaaS cohorts & capacity' },
  { id: 'usage', label: 'Usage' },
  { id: 'versions', label: 'Versions' },
  { id: 'health', label: 'Health' },
  { id: 'geo', label: 'Geography' },
  { id: 'support', label: 'Support' },
]

const activeTab = ref('overview')
const loading = ref(true)
const loadError = ref(null)
const overview = ref(null)
const summary = ref(null)
const cohortRows = ref([])
const capacityRows = ref([])
const tenantDirectoryCount = ref(null)
const inactiveDays = ref(14)

const chartOptionsDoughnut = {
  plugins: { legend: { position: 'bottom', labels: { color: '#94a3b8' } } },
}

const chartOptionsLine = {
  plugins: { legend: { display: false } },
  scales: {
    x: { grid: { color: 'rgba(148,163,184,0.15)' }, ticks: { color: '#94a3b8', maxRotation: 45 } },
    y: { beginAtZero: true, grid: { color: 'rgba(148,163,184,0.15)' }, ticks: { color: '#94a3b8' } },
  },
}

const chartOptionsLineAlt = {
  ...chartOptionsLine,
  plugins: {
    ...chartOptionsLine.plugins,
    legend: { display: true, labels: { color: '#94a3b8' } },
  },
}

const chartOptionsBarH = {
  indexAxis: 'y',
  plugins: { legend: { display: false } },
  scales: {
    x: { beginAtZero: true, grid: { color: 'rgba(148,163,184,0.15)' }, ticks: { color: '#94a3b8' } },
    y: { grid: { display: false }, ticks: { color: '#94a3b8' } },
  },
}

function formatMoney(cents) {
  if (cents == null) return '—'
  const n = Number(cents) / 100
  return n.toLocaleString(undefined, { style: 'currency', currency: 'USD', maximumFractionDigits: 0 })
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

const revenueChartData = computed(() => {
  const rows = overview.value?.charts?.revenue_by_month
  if (!rows?.length) return null
  return {
    labels: rows.map((r) => r.month),
    datasets: [
      {
        label: 'Paid invoices',
        data: rows.map((r) => r.amount_cents),
        borderColor: 'rgb(139, 92, 246)',
        backgroundColor: 'rgba(139, 92, 246, 0.12)',
        fill: true,
        tension: 0.3,
      },
    ],
  }
})

const activationChartData = computed(() => {
  const rows = summary.value?.self_hosted?.activations_by_month
  if (!rows?.length) return null
  return {
    labels: rows.map((r) => r.month),
    datasets: [
      {
        label: 'Activations',
        data: rows.map((r) => r.count),
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.12)',
        fill: true,
        tension: 0.3,
      },
    ],
  }
})

const versionBarData = computed(() => {
  const rows = summary.value?.self_hosted?.version_distribution
  if (!rows?.length) return null
  const top = rows.slice(0, 15)
  return {
    labels: top.map((r) => r.version || '—'),
    datasets: [
      {
        label: 'Installations',
        data: top.map((r) => r.count),
        backgroundColor: 'rgba(6, 182, 212, 0.55)',
      },
    ],
  }
})

async function load() {
  loading.value = true
  loadError.value = null
  try {
    const [ov, co, cap, tenants, rep] = await Promise.all([
      platformAPI.overview(),
      api.get('/platform/cohorts/'),
      api.get('/platform/capacity/'),
      platformAPI.tenants.list({ page_size: 1 }),
      platformAPI.reportsSummary({ inactive_days: inactiveDays.value }),
    ])
    overview.value = ov.data
    cohortRows.value = co.data?.cohorts || []
    capacityRows.value = cap.data?.tenants || []
    summary.value = rep.data
    const d = tenants.data
    tenantDirectoryCount.value = d?.count ?? (d?.results || []).length ?? null
  } catch (e) {
    loadError.value = normalizeApiError(e).userMessage || 'Could not load reports'
    overview.value = null
    summary.value = null
    cohortRows.value = []
    capacityRows.value = []
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>
