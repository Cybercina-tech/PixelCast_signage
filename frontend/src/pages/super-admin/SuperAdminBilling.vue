<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-wrap justify-between items-center gap-4">
      <div>
        <h1 class="text-2xl font-bold text-primary">Billing Center</h1>
        <p class="text-sm text-muted mt-1">Revenue analytics, expense tracking, subscription health</p>
      </div>
      <div class="flex flex-wrap gap-2">
        <router-link to="/super-admin/pricing" class="btn-outline px-4 py-2 rounded-lg text-sm inline-flex items-center">
          Pricing catalog
        </router-link>
        <button type="button" class="btn-primary px-4 py-2 rounded-lg text-sm" :disabled="billingBusy" @click="openCheckout">
          {{ billingBusy ? 'Opening...' : 'Stripe Checkout' }}
        </button>
        <button type="button" class="btn-outline px-4 py-2 rounded-lg text-sm" :disabled="billingBusy" @click="openPortal">
          Customer Portal
        </button>
        <button type="button" class="btn-outline px-4 py-2 rounded-lg text-sm" :disabled="loading" @click="load">
          Refresh
        </button>
      </div>
    </div>

    <!-- Error -->
    <div
      v-if="loadError"
      class="rounded-xl border border-amber-500/40 bg-amber-500/10 px-4 py-3 text-sm text-amber-900 dark:text-amber-100"
    >
      {{ loadError }}
    </div>

    <!-- Loading skeleton -->
    <div v-if="loading" class="space-y-4">
      <div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <div v-for="i in 8" :key="i" class="card-base rounded-2xl p-6 animate-pulse h-28" />
      </div>
    </div>

    <template v-else-if="overview">
      <!-- ══════════════════════════════════════════════════════════ -->
      <!--  ROW 1: Primary Revenue KPIs                              -->
      <!-- ══════════════════════════════════════════════════════════ -->
      <div class="grid grid-cols-2 sm:grid-cols-4 xl:grid-cols-8 gap-3">
        <div class="card-base rounded-2xl p-4 border border-border-color/80 hover:border-emerald-500/30 transition-colors">
          <p class="text-[10px] font-semibold text-muted uppercase tracking-wider">MRR</p>
          <p class="text-2xl font-bold text-emerald-400 mt-1">{{ formatMoney(overview.revenue?.mrr_estimate_cents) }}</p>
        </div>
        <div class="card-base rounded-2xl p-4 border border-border-color/80 hover:border-emerald-500/30 transition-colors">
          <p class="text-[10px] font-semibold text-muted uppercase tracking-wider">ARR</p>
          <p class="text-2xl font-bold text-emerald-400 mt-1">{{ formatMoney(overview.revenue?.arr_estimate_cents) }}</p>
        </div>
        <div class="card-base rounded-2xl p-4 border border-border-color/80 hover:border-cyan-500/30 transition-colors">
          <p class="text-[10px] font-semibold text-muted uppercase tracking-wider">Revenue 30d</p>
          <p class="text-2xl font-bold text-cyan-400 mt-1">{{ formatMoney(overview.revenue?.revenue_last_30d_cents) }}</p>
        </div>
        <div class="card-base rounded-2xl p-4 border border-border-color/80 hover:border-rose-500/30 transition-colors">
          <p class="text-[10px] font-semibold text-muted uppercase tracking-wider">Expenses 30d</p>
          <p class="text-2xl font-bold text-rose-400 mt-1">{{ formatMoney(overview.revenue?.expenses_last_30d_cents) }}</p>
        </div>
        <div class="card-base rounded-2xl p-4 border border-border-color/80 hover:border-violet-500/30 transition-colors">
          <p class="text-[10px] font-semibold text-muted uppercase tracking-wider">Net 30d</p>
          <p class="text-2xl font-bold mt-1" :class="(overview.revenue?.net_last_30d_cents ?? 0) >= 0 ? 'text-emerald-400' : 'text-rose-400'">
            {{ formatMoney(overview.revenue?.net_last_30d_cents) }}
          </p>
        </div>
        <div class="card-base rounded-2xl p-4 border border-border-color/80">
          <p class="text-[10px] font-semibold text-muted uppercase tracking-wider">Paying</p>
          <p class="text-2xl font-bold text-primary mt-1">{{ overview.counts?.paying_with_subscription ?? 0 }}</p>
        </div>
        <div class="card-base rounded-2xl p-4 border border-border-color/80">
          <p class="text-[10px] font-semibold text-muted uppercase tracking-wider">Trialing</p>
          <p class="text-2xl font-bold text-cyan-400 mt-1">{{ overview.counts?.trialing ?? 0 }}</p>
        </div>
        <div class="card-base rounded-2xl p-4 border border-border-color/80">
          <p class="text-[10px] font-semibold text-muted uppercase tracking-wider">Payment failed</p>
          <p class="text-2xl font-bold text-amber-400 mt-1">{{ overview.counts?.with_payment_failure_flag ?? 0 }}</p>
        </div>
      </div>

      <!-- ══════════════════════════════════════════════════════════ -->
      <!--  ROW 2: Revenue vs Expenses (main chart)                  -->
      <!-- ══════════════════════════════════════════════════════════ -->
      <Card title="Revenue vs Expenses — Monthly (12 months)">
        <div v-if="revenueVsExpenseData" class="h-64 sm:h-72">
          <Chart type="bar" :data="revenueVsExpenseData" :options="chartOptionsStacked" />
        </div>
        <p v-else class="text-sm text-muted py-8 text-center">No monthly financial data yet</p>
      </Card>

      <!-- ══════════════════════════════════════════════════════════ -->
      <!--  ROW 3: Revenue trend + Net margin                       -->
      <!-- ══════════════════════════════════════════════════════════ -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Revenue Trend">
          <Chart v-if="revenueTrendData" type="line" :data="revenueTrendData" :options="chartOptionsLine" />
          <p v-else class="text-sm text-muted py-8 text-center">No revenue data</p>
        </Card>
        <Card title="Net Margin by Month">
          <Chart v-if="netMarginData" type="bar" :data="netMarginData" :options="chartOptionsNetMargin" />
          <p v-else class="text-sm text-muted py-8 text-center">No margin data</p>
        </Card>
      </div>

      <!-- ══════════════════════════════════════════════════════════ -->
      <!--  ROW 4: Subscription Status + Plan Distribution           -->
      <!-- ══════════════════════════════════════════════════════════ -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Subscription Status Breakdown">
          <Chart v-if="subscriptionStatusData" type="doughnut" :data="subscriptionStatusData" :options="chartOptionsDoughnut" />
          <p v-else class="text-sm text-muted py-8 text-center">No subscription data</p>
        </Card>
        <Card title="Plan Distribution">
          <Chart v-if="planDistData" type="doughnut" :data="planDistData" :options="chartOptionsDoughnut" />
          <p v-else class="text-sm text-muted py-8 text-center">No plan data</p>
        </Card>
      </div>

      <!-- ══════════════════════════════════════════════════════════ -->
      <!--  ROW 5: Expenses by Category + New Signups                -->
      <!-- ══════════════════════════════════════════════════════════ -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Expenses by Category">
          <Chart v-if="expenseCategoryData" type="doughnut" :data="expenseCategoryData" :options="chartOptionsDoughnut" />
          <p v-else class="text-sm text-muted py-8 text-center">No expense categories</p>
        </Card>
        <Card title="New Tenant Signups — Monthly">
          <Chart v-if="signupChartData" type="line" :data="signupChartData" :options="chartOptionsLine" />
          <p v-else class="text-sm text-muted py-8 text-center">No signup data</p>
        </Card>
      </div>

      <!-- ══════════════════════════════════════════════════════════ -->
      <!--  ROW 6: Health Distribution + Billing Alerts              -->
      <!-- ══════════════════════════════════════════════════════════ -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Tenant Health Score Distribution">
          <Chart v-if="healthChartData" type="bar" :data="healthChartData" :options="chartOptionsBar" />
          <p v-else class="text-sm text-muted py-8 text-center">No health data</p>
        </Card>
        <Card title="Billing Alerts Across Tenants">
          <div v-if="billingAlertChartData">
            <Chart type="bar" :data="billingAlertChartData" :options="chartOptionsHorizontalBar" />
          </div>
          <div v-else class="py-4">
            <p class="text-sm text-muted text-center">No billing alerts</p>
          </div>
        </Card>
      </div>

      <!-- ══════════════════════════════════════════════════════════ -->
      <!--  ROW 7: Churn Risk + License Status                      -->
      <!-- ══════════════════════════════════════════════════════════ -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Churn Risk Summary">
          <div class="grid grid-cols-2 gap-3 py-2">
            <div class="rounded-xl border border-border-color/60 bg-card/60 p-4 text-center">
              <p class="text-3xl font-bold text-emerald-400">{{ overview.counts?.tenants ?? 0 }}</p>
              <p class="text-xs text-muted mt-1">Total tenants</p>
            </div>
            <div class="rounded-xl border border-border-color/60 bg-card/60 p-4 text-center">
              <p class="text-3xl font-bold text-rose-400">{{ overview.counts?.churn_risk_high ?? 0 }}</p>
              <p class="text-xs text-muted mt-1">High churn risk</p>
            </div>
            <div class="rounded-xl border border-border-color/60 bg-card/60 p-4 text-center">
              <p class="text-3xl font-bold text-primary">{{ overview.health?.average_score ?? 0 }}</p>
              <p class="text-xs text-muted mt-1">Avg health score</p>
            </div>
            <div class="rounded-xl border border-border-color/60 bg-card/60 p-4 text-center">
              <p class="text-3xl font-bold text-amber-400">{{ overview.counts?.with_payment_failure_flag ?? 0 }}</p>
              <p class="text-xs text-muted mt-1">Payment failures</p>
            </div>
          </div>
        </Card>

        <Card title="License Status">
          <div v-if="licenseError" class="text-sm text-amber-600 py-4">{{ licenseError }}</div>
          <dl v-else-if="licenseInfo" class="text-sm space-y-3 py-2">
            <div class="flex justify-between items-center gap-2 border-b border-border-color/40 pb-2">
              <dt class="text-muted">Status</dt>
              <dd>
                <span
                  class="text-xs px-2.5 py-1 rounded-full border font-medium"
                  :class="licenseInfo.license_status === 'active' ? 'border-emerald-500/40 text-emerald-400 bg-emerald-500/10' : 'border-amber-500/40 text-amber-400 bg-amber-500/10'"
                >
                  {{ licenseInfo.license_status || licenseInfo.status || '---' }}
                </span>
              </dd>
            </div>
            <div class="flex justify-between gap-2 border-b border-border-color/40 pb-2">
              <dt class="text-muted">Domain</dt>
              <dd class="text-primary text-xs font-mono truncate max-w-[55%] text-right">{{ licenseInfo.activated_domain || licenseInfo.domain || '---' }}</dd>
            </div>
            <div class="flex justify-between gap-2 border-b border-border-color/40 pb-2">
              <dt class="text-muted">Purchase code</dt>
              <dd class="text-primary text-xs font-mono">{{ licenseInfo.masked_purchase_code || licenseInfo.purchase_code || '---' }}</dd>
            </div>
            <div class="flex justify-between gap-2">
              <dt class="text-muted">Last validation</dt>
              <dd class="text-primary text-xs">{{ licenseInfo.last_validation_at ? new Date(licenseInfo.last_validation_at).toLocaleString() : '---' }}</dd>
            </div>
          </dl>
          <p v-else class="text-sm text-muted py-4 text-center">Loading license info...</p>
        </Card>
      </div>

      <!-- ══════════════════════════════════════════════════════════ -->
      <!--  ROW 8: Expense Ledger                                    -->
      <!-- ══════════════════════════════════════════════════════════ -->
      <Card title="Recent Expenses">
        <div v-if="expenses.length" class="overflow-x-auto">
          <table class="min-w-full text-sm">
            <thead>
              <tr class="border-b border-border-color text-left text-muted">
                <th class="py-2 pr-3">Date</th>
                <th class="py-2 pr-3">Title</th>
                <th class="py-2 pr-3">Category</th>
                <th class="py-2 pr-3 text-right">Amount</th>
                <th class="py-2 pr-3">Recurring</th>
                <th class="py-2">Tenant</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="exp in expenses" :key="exp.id" class="border-b border-border-color/40">
                <td class="py-2 pr-3 text-xs text-muted whitespace-nowrap">{{ exp.spent_on }}</td>
                <td class="py-2 pr-3 text-primary">{{ exp.title }}</td>
                <td class="py-2 pr-3">
                  <span class="text-[11px] px-2 py-0.5 rounded-full border border-border-color/60 capitalize">{{ exp.category }}</span>
                </td>
                <td class="py-2 pr-3 text-right font-mono">{{ formatMoney(exp.amount_cents) }}</td>
                <td class="py-2 pr-3 text-xs">{{ exp.is_recurring ? 'Yes' : 'No' }}</td>
                <td class="py-2 text-xs text-muted">{{ exp.tenant_name || '---' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p v-else class="text-sm text-muted py-6 text-center">No expenses recorded yet</p>
      </Card>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import Card from '@/components/common/Card.vue'
import Chart from '@/components/common/Chart.vue'
import { licenseAPI, platformAPI } from '@/services/api'
import { normalizeApiError } from '@/utils/apiError'

const loading = ref(true)
const loadError = ref(null)
const overview = ref(null)
const licenseInfo = ref(null)
const licenseError = ref(null)
const billingBusy = ref(false)
const expenses = ref([])

const PALETTE = ['#06b6d4', '#8b5cf6', '#ec4899', '#f97316', '#22c55e', '#eab308', '#ef4444', '#3b82f6', '#14b8a6']

function formatMoney(cents) {
  if (cents == null) return '---'
  const n = Number(cents) / 100
  return n.toLocaleString(undefined, { style: 'currency', currency: 'USD', maximumFractionDigits: 0 })
}

// ── Chart options ──────────────────────────────────────────────

const chartOptionsLine = {
  plugins: { legend: { display: false } },
  scales: {
    x: { grid: { color: 'rgba(148,163,184,0.12)' }, ticks: { color: '#94a3b8', maxRotation: 45, font: { size: 10 } } },
    y: { beginAtZero: true, grid: { color: 'rgba(148,163,184,0.12)' }, ticks: { color: '#94a3b8', font: { size: 10 } } },
  },
}

const chartOptionsBar = {
  plugins: { legend: { display: false } },
  scales: {
    x: { grid: { display: false }, ticks: { color: '#94a3b8', font: { size: 10 } } },
    y: { beginAtZero: true, grid: { color: 'rgba(148,163,184,0.12)' }, ticks: { color: '#94a3b8', font: { size: 10 } } },
  },
}

const chartOptionsStacked = {
  plugins: {
    legend: { position: 'top', labels: { color: '#94a3b8', usePointStyle: true, padding: 16, font: { size: 11 } } },
  },
  scales: {
    x: { stacked: true, grid: { display: false }, ticks: { color: '#94a3b8', maxRotation: 45, font: { size: 10 } } },
    y: { stacked: true, beginAtZero: true, grid: { color: 'rgba(148,163,184,0.12)' }, ticks: { color: '#94a3b8', font: { size: 10 },
      callback(v) { return '$' + (v / 100).toLocaleString() },
    } },
  },
}

const chartOptionsNetMargin = {
  plugins: { legend: { display: false } },
  scales: {
    x: { grid: { display: false }, ticks: { color: '#94a3b8', maxRotation: 45, font: { size: 10 } } },
    y: { grid: { color: 'rgba(148,163,184,0.12)' }, ticks: { color: '#94a3b8', font: { size: 10 },
      callback(v) { return '$' + (v / 100).toLocaleString() },
    } },
  },
}

const chartOptionsDoughnut = {
  plugins: { legend: { position: 'bottom', labels: { color: '#94a3b8', usePointStyle: true, padding: 12, font: { size: 11 } } } },
}

const chartOptionsHorizontalBar = {
  indexAxis: 'y',
  plugins: { legend: { display: false } },
  scales: {
    x: { beginAtZero: true, grid: { color: 'rgba(148,163,184,0.12)' }, ticks: { color: '#94a3b8', font: { size: 10 } } },
    y: { grid: { display: false }, ticks: { color: '#94a3b8', font: { size: 10 } } },
  },
}

// ── Computed chart data ────────────────────────────────────────

const revenueVsExpenseData = computed(() => {
  const rev = overview.value?.charts?.revenue_by_month || []
  const exp = overview.value?.charts?.expenses_by_month || []
  const allMonths = [...new Set([...rev.map(r => r.month), ...exp.map(r => r.month)])].sort()
  if (!allMonths.length) return null
  const revMap = Object.fromEntries(rev.map(r => [r.month, r.amount_cents || 0]))
  const expMap = Object.fromEntries(exp.map(r => [r.month, r.amount_cents || 0]))
  return {
    labels: allMonths,
    datasets: [
      {
        label: 'Revenue',
        data: allMonths.map(m => revMap[m] || 0),
        backgroundColor: 'rgba(34, 197, 94, 0.6)',
        borderColor: 'rgb(34, 197, 94)',
        borderWidth: 1,
        borderRadius: 4,
      },
      {
        label: 'Expenses',
        data: allMonths.map(m => expMap[m] || 0),
        backgroundColor: 'rgba(239, 68, 68, 0.5)',
        borderColor: 'rgb(239, 68, 68)',
        borderWidth: 1,
        borderRadius: 4,
      },
    ],
  }
})

const revenueTrendData = computed(() => {
  const rows = overview.value?.charts?.revenue_by_month
  if (!rows?.length) return null
  return {
    labels: rows.map(r => r.month),
    datasets: [{
      label: 'Revenue',
      data: rows.map(r => Number(r.amount_cents || 0) / 100),
      borderColor: 'rgb(34, 197, 94)',
      backgroundColor: 'rgba(34, 197, 94, 0.1)',
      fill: true,
      tension: 0.35,
      pointRadius: 3,
      pointHoverRadius: 6,
    }],
  }
})

const netMarginData = computed(() => {
  const rev = overview.value?.charts?.revenue_by_month || []
  const exp = overview.value?.charts?.expenses_by_month || []
  const allMonths = [...new Set([...rev.map(r => r.month), ...exp.map(r => r.month)])].sort()
  if (!allMonths.length) return null
  const revMap = Object.fromEntries(rev.map(r => [r.month, r.amount_cents || 0]))
  const expMap = Object.fromEntries(exp.map(r => [r.month, r.amount_cents || 0]))
  const margins = allMonths.map(m => (revMap[m] || 0) - (expMap[m] || 0))
  return {
    labels: allMonths,
    datasets: [{
      label: 'Net margin',
      data: margins,
      backgroundColor: margins.map(v => v >= 0 ? 'rgba(34, 197, 94, 0.55)' : 'rgba(239, 68, 68, 0.55)'),
      borderColor: margins.map(v => v >= 0 ? 'rgb(34, 197, 94)' : 'rgb(239, 68, 68)'),
      borderWidth: 1,
      borderRadius: 4,
    }],
  }
})

const subscriptionStatusData = computed(() => {
  const map = overview.value?.counts?.by_subscription_status
  if (!map || !Object.keys(map).length) return null
  const labels = Object.keys(map)
  return {
    labels: labels.map(l => l.replace(/_/g, ' ')),
    datasets: [{
      data: labels.map(l => map[l]),
      backgroundColor: labels.map((_, i) => PALETTE[i % PALETTE.length]),
    }],
  }
})

const planDistData = computed(() => {
  const rows = overview.value?.charts?.plan_distribution
  if (!rows?.length) return null
  return {
    labels: rows.map(r => r.plan),
    datasets: [{
      data: rows.map(r => r.count),
      backgroundColor: rows.map((_, i) => PALETTE[i % PALETTE.length]),
    }],
  }
})

const expenseCategoryData = computed(() => {
  const rows = overview.value?.charts?.expense_by_category
  if (!rows?.length) return null
  return {
    labels: rows.map(r => (r.category || 'unknown').replace(/_/g, ' ')),
    datasets: [{
      data: rows.map(r => r.amount_cents),
      backgroundColor: rows.map((_, i) => PALETTE[i % PALETTE.length]),
    }],
  }
})

const signupChartData = computed(() => {
  const rows = overview.value?.charts?.signups_by_month
  if (!rows?.length) return null
  return {
    labels: rows.map(r => r.month),
    datasets: [{
      label: 'New tenants',
      data: rows.map(r => r.count),
      borderColor: 'rgb(6, 182, 212)',
      backgroundColor: 'rgba(6, 182, 212, 0.12)',
      fill: true,
      tension: 0.35,
      pointRadius: 3,
      pointHoverRadius: 6,
    }],
  }
})

const healthChartData = computed(() => {
  const c = overview.value?.charts
  if (!c?.health_histogram_labels?.length) return null
  return {
    labels: c.health_histogram_labels,
    datasets: [{
      label: 'Tenants',
      data: c.health_histogram_values,
      backgroundColor: [
        'rgba(239,68,68,0.55)',
        'rgba(249,115,22,0.55)',
        'rgba(234,179,8,0.55)',
        'rgba(34,197,94,0.45)',
        'rgba(6,182,212,0.55)',
      ],
      borderRadius: 4,
    }],
  }
})

const billingAlertChartData = computed(() => {
  const rollup = overview.value?.billing_alerts_rollup
  if (!rollup || !Object.keys(rollup).length) return null
  const labels = Object.keys(rollup).map(k => k.replace(/_/g, ' '))
  return {
    labels,
    datasets: [{
      label: 'Count',
      data: Object.values(rollup),
      backgroundColor: 'rgba(249, 115, 22, 0.55)',
      borderColor: 'rgb(249, 115, 22)',
      borderWidth: 1,
      borderRadius: 4,
    }],
  }
})

// ── Data loading ───────────────────────────────────────────────

async function load() {
  loading.value = true
  loadError.value = null
  licenseError.value = null
  try {
    const [{ data: ov }, licResult, expResult] = await Promise.all([
      platformAPI.overview(),
      licenseAPI.status().catch(e => ({ error: e })),
      platformAPI.expenses.list({ page_size: 25 }).catch(() => ({ data: { results: [] } })),
    ])
    overview.value = ov
    if (licResult.error) {
      licenseInfo.value = null
      licenseError.value = normalizeApiError(licResult.error).userMessage || 'License info unavailable'
    } else {
      licenseInfo.value = licResult.data
    }
    expenses.value = expResult.data?.results || expResult.data || []
  } catch (e) {
    loadError.value = normalizeApiError(e).userMessage || 'Could not load billing data'
    overview.value = null
  } finally {
    loading.value = false
  }
}

async function openCheckout() {
  billingBusy.value = true
  try {
    const { data } = await platformAPI.billingCheckout({})
    if (data?.url) window.location.href = data.url
  } catch (e) {
    loadError.value = normalizeApiError(e).userMessage || 'Checkout failed'
  } finally {
    billingBusy.value = false
  }
}

async function openPortal() {
  billingBusy.value = true
  try {
    const { data } = await platformAPI.billingPortal({})
    if (data?.url) window.location.href = data.url
  } catch (e) {
    loadError.value = normalizeApiError(e).userMessage || 'Portal failed'
  } finally {
    billingBusy.value = false
  }
}

onMounted(load)
</script>
