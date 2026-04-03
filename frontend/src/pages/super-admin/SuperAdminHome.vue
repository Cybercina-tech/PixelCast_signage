<template>
  <div class="space-y-8">
    <section class="relative overflow-hidden rounded-3xl border border-border-color/80 bg-gradient-to-br from-cyan-500/10 via-violet-500/10 to-transparent p-5 md:p-7">
      <div class="absolute -right-12 -top-12 h-36 w-36 rounded-full bg-cyan-400/10 blur-2xl" />
      <div class="absolute -left-16 -bottom-16 h-40 w-40 rounded-full bg-violet-500/10 blur-2xl" />
      <p class="text-[11px] uppercase tracking-wider text-muted mb-2 relative z-10">Super Admin Overview</p>
      <h2 class="text-xl md:text-2xl font-bold text-primary relative z-10">Platform Control Center</h2>
      <p class="text-secondary text-sm mt-2 max-w-2xl relative z-10">
        Platform-wide SaaS health, revenue estimates, and tenant engagement in one responsive dashboard.
      </p>
      <div class="mt-4 flex flex-wrap gap-2 relative z-10">
        <router-link to="/super-admin/customers" class="btn-primary px-4 py-2 rounded-lg text-sm">
          Manage Tenants
        </router-link>
        <router-link to="/super-admin/reports" class="btn-outline px-4 py-2 rounded-lg text-sm">
          Open Reports
        </router-link>
      </div>
    </section>

    <div
      v-if="loadError"
      class="rounded-2xl border border-amber-500/40 bg-amber-500/10 px-4 py-3 text-sm text-amber-900 dark:text-amber-100"
    >
      {{ loadError }}
    </div>

    <div v-if="loading" class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <div v-for="i in 4" :key="i" class="card-base rounded-2xl p-6 animate-pulse h-28" />
    </div>

    <div v-else-if="overview" class="space-y-8">
      <!-- KPI cards -->
      <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <div class="card-base rounded-2xl p-5 border border-border-color/80 hover:border-cyan-500/30 transition-colors">
          <p class="text-xs font-medium text-muted uppercase tracking-wide">Tenants</p>
          <p class="text-3xl font-bold text-primary mt-1">{{ overview.counts.tenants }}</p>
          <p class="text-xs text-muted mt-1">Paying: {{ overview.counts.paying_with_subscription }}</p>
        </div>
        <div class="card-base rounded-2xl p-5 border border-border-color/80 hover:border-cyan-500/30 transition-colors">
          <p class="text-xs font-medium text-muted uppercase tracking-wide">MRR (est.)</p>
          <p class="text-3xl font-bold text-primary mt-1">{{ formatMoney(overview.revenue.mrr_estimate_cents) }}</p>
          <p class="text-xs text-muted mt-1">Rolling 30d paid invoices</p>
        </div>
        <div class="card-base rounded-2xl p-5 border border-border-color/80 hover:border-cyan-500/30 transition-colors">
          <p class="text-xs font-medium text-muted uppercase tracking-wide">ARR (est.)</p>
          <p class="text-3xl font-bold text-primary mt-1">{{ formatMoney(overview.revenue.arr_estimate_cents) }}</p>
          <p class="text-xs text-muted mt-1">MRR × 12</p>
        </div>
        <div class="card-base rounded-2xl p-5 border border-border-color/80 hover:border-cyan-500/30 transition-colors">
          <p class="text-xs font-medium text-muted uppercase tracking-wide">Avg health</p>
          <p class="text-3xl font-bold text-primary mt-1">{{ overview.health.average_score }}</p>
          <p class="text-xs text-muted mt-1">High churn risk: {{ overview.counts.churn_risk_high }}</p>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card class="lg:col-span-2" title="New tenants by month">
          <Chart v-if="signupChartData" type="line" :data="signupChartData" :options="chartOptionsLine" />
          <p v-else class="text-sm text-muted">No signup data</p>
        </Card>
        <Card title="Health score distribution">
          <Chart v-if="healthChartData" type="bar" :data="healthChartData" :options="chartOptionsBar" />
        </Card>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Plans">
          <Chart v-if="planChartData" type="doughnut" :data="planChartData" :options="chartOptionsDoughnut" />
          <p v-else class="text-sm text-muted">No plan labels</p>
        </Card>
        <Card title="Billing alert signals">
          <ul class="text-sm space-y-2">
            <li
              v-for="(n, key) in overview.billing_alerts_rollup"
              :key="key"
              class="flex justify-between gap-2 border-b border-border-color/40 pb-2"
            >
              <span class="text-muted capitalize">{{ key.replace(/_/g, ' ') }}</span>
              <span class="font-medium text-primary">{{ n }}</span>
            </li>
            <li v-if="!Object.keys(overview.billing_alerts_rollup || {}).length" class="text-muted text-sm">
              No billing alerts across tenants
            </li>
          </ul>
        </Card>
      </div>

      <div class="grid gap-4 sm:grid-cols-2">
        <router-link
          to="/super-admin/customers"
          class="card-base rounded-2xl p-6 hover:border-accent-color/40 hover:-translate-y-0.5 border border-transparent transition-all block"
        >
          <h2 class="font-semibold text-primary mb-1">Tenants</h2>
          <p class="text-sm text-muted">Search, filters, health, billing, impersonation</p>
        </router-link>
        <router-link
          to="/super-admin/reports"
          class="card-base rounded-2xl p-6 hover:border-accent-color/40 hover:-translate-y-0.5 border border-transparent transition-all block"
        >
          <h2 class="font-semibold text-primary mb-1">Reports &amp; cohorts</h2>
          <p class="text-sm text-muted">Retention and revenue analytics</p>
        </router-link>
        <router-link
          to="/super-admin/smtp"
          class="card-base rounded-2xl p-6 hover:border-accent-color/40 hover:-translate-y-0.5 border border-transparent transition-all block"
        >
          <h2 class="font-semibold text-primary mb-1">Email / SMTP</h2>
          <p class="text-sm text-muted">Transactional email and test send</p>
        </router-link>
        <router-link
          to="/super-admin/recovery"
          class="card-base rounded-2xl p-6 hover:border-accent-color/40 hover:-translate-y-0.5 border border-transparent transition-all block"
        >
          <h2 class="font-semibold text-primary mb-1">Recovery &amp; dunning</h2>
          <p class="text-sm text-muted">Failed payments and reminders</p>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import Card from '@/components/common/Card.vue'
import Chart from '@/components/common/Chart.vue'
import { platformAPI } from '@/services/api'
import { normalizeApiError } from '@/utils/apiError'

const loading = ref(true)
const loadError = ref(null)
const overview = ref(null)

const chartOptionsLine = {
  plugins: { legend: { display: false } },
  scales: {
    x: { grid: { color: 'rgba(148,163,184,0.15)' }, ticks: { color: '#94a3b8', maxRotation: 45 } },
    y: { beginAtZero: true, grid: { color: 'rgba(148,163,184,0.15)' }, ticks: { color: '#94a3b8' } },
  },
}

const chartOptionsBar = {
  plugins: { legend: { display: false } },
  scales: {
    x: { grid: { display: false }, ticks: { color: '#94a3b8' } },
    y: { beginAtZero: true, grid: { color: 'rgba(148,163,184,0.15)' }, ticks: { color: '#94a3b8' } },
  },
}

const chartOptionsDoughnut = {
  plugins: { legend: { position: 'bottom', labels: { color: '#94a3b8' } } },
}

function formatMoney(cents) {
  if (cents == null) return '—'
  const n = Number(cents) / 100
  return n.toLocaleString(undefined, { style: 'currency', currency: 'USD', maximumFractionDigits: 0 })
}

const signupChartData = computed(() => {
  const rows = overview.value?.charts?.signups_by_month
  if (!rows?.length) return null
  return {
    labels: rows.map((r) => r.month),
    datasets: [
      {
        label: 'Signups',
        data: rows.map((r) => r.count),
        borderColor: 'rgb(6, 182, 212)',
        backgroundColor: 'rgba(6, 182, 212, 0.15)',
        fill: true,
        tension: 0.3,
      },
    ],
  }
})

const healthChartData = computed(() => {
  const o = overview.value?.charts
  if (!o?.health_histogram_labels?.length) return null
  return {
    labels: o.health_histogram_labels,
    datasets: [
      {
        label: 'Tenants',
        data: o.health_histogram_values,
        backgroundColor: [
          'rgba(239,68,68,0.55)',
          'rgba(249,115,22,0.55)',
          'rgba(234,179,8,0.55)',
          'rgba(34,197,94,0.45)',
          'rgba(6,182,212,0.55)',
        ],
      },
    ],
  }
})

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

onMounted(async () => {
  loading.value = true
  loadError.value = null
  try {
    const { data } = await platformAPI.overview()
    overview.value = data
  } catch (e) {
    loadError.value = normalizeApiError(e).userMessage || 'Could not load platform overview'
  } finally {
    loading.value = false
  }
})
</script>
