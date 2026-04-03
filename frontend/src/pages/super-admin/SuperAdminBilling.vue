<template>
  <div class="space-y-8">
    <div class="flex flex-wrap justify-between items-center gap-4">
      <div>
        <h1 class="text-2xl font-bold text-primary">Billing center</h1>
        <p class="text-sm text-muted mt-1">Platform revenue, expenses, and Stripe shortcuts</p>
      </div>
      <div class="flex flex-wrap gap-2">
        <button type="button" class="btn-primary px-4 py-2 rounded-lg text-sm" :disabled="billingBusy" @click="openCheckout">
          {{ billingBusy ? 'Opening…' : 'Open checkout' }}
        </button>
        <button type="button" class="btn-outline px-4 py-2 rounded-lg text-sm" :disabled="billingBusy" @click="openPortal">
          Customer portal
        </button>
        <button type="button" class="btn-outline px-4 py-2 rounded-lg text-sm" :disabled="loading" @click="load">Refresh</button>
      </div>
    </div>

    <div
      v-if="loadError"
      class="rounded-2xl border border-amber-500/40 bg-amber-500/10 px-4 py-3 text-sm text-amber-900 dark:text-amber-100"
    >
      {{ loadError }}
    </div>

    <div v-if="loading" class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <div v-for="i in 4" :key="i" class="card-base rounded-2xl p-6 animate-pulse h-28" />
    </div>

    <template v-else-if="overview">
      <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <div class="card-base rounded-2xl p-5 border border-border-color/80">
          <p class="text-xs font-medium text-muted uppercase tracking-wide">MRR (est.)</p>
          <p class="text-3xl font-bold text-primary mt-1">{{ formatMoney(overview.revenue?.mrr_estimate_cents) }}</p>
          <p class="text-xs text-muted mt-1">Rolling 30d paid invoices</p>
        </div>
        <div class="card-base rounded-2xl p-5 border border-border-color/80">
          <p class="text-xs font-medium text-muted uppercase tracking-wide">ARR (est.)</p>
          <p class="text-3xl font-bold text-primary mt-1">{{ formatMoney(overview.revenue?.arr_estimate_cents) }}</p>
          <p class="text-xs text-muted mt-1">MRR × 12</p>
        </div>
        <div class="card-base rounded-2xl p-5 border border-border-color/80">
          <p class="text-xs font-medium text-muted uppercase tracking-wide">Net revenue 30d</p>
          <p class="text-3xl font-bold text-primary mt-1">{{ formatMoney(overview.revenue?.revenue_last_30d_cents) }}</p>
          <p class="text-xs text-muted mt-1">Paid invoices (gross)</p>
        </div>
        <div class="card-base rounded-2xl p-5 border border-border-color/80">
          <p class="text-xs font-medium text-muted uppercase tracking-wide">Expenses 30d</p>
          <p class="text-3xl font-bold text-primary mt-1">{{ formatMoney(overview.revenue?.expenses_last_30d_cents) }}</p>
          <p class="text-xs text-muted mt-1">Platform expense ledger</p>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Revenue by month">
          <Chart v-if="revenueChartData" type="line" :data="revenueChartData" :options="chartOptionsLine" />
          <p v-else class="text-sm text-muted">No revenue data</p>
        </Card>
        <Card title="Expenses by category">
          <Chart v-if="expenseDoughnutData" type="doughnut" :data="expenseDoughnutData" :options="chartOptionsDoughnut" />
          <p v-else class="text-sm text-muted">No expense categories</p>
        </Card>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Recent billing alert signals">
          <ul class="text-sm space-y-2">
            <li
              v-for="(n, key) in overview.billing_alerts_rollup || {}"
              :key="key"
              class="flex justify-between gap-2 border-b border-border-color/40 pb-2"
            >
              <span class="text-muted capitalize">{{ String(key).replace(/_/g, ' ') }}</span>
              <span class="font-medium text-primary">{{ n }}</span>
            </li>
            <li v-if="!billingAlertKeys.length" class="text-muted text-sm">No billing alerts across tenants</li>
          </ul>
        </Card>
        <Card title="License (server)">
          <div v-if="licenseError" class="text-sm text-amber-600">{{ licenseError }}</div>
          <dl v-else-if="licenseInfo" class="text-sm space-y-2">
            <div class="flex justify-between gap-2">
              <dt class="text-muted">Status</dt>
              <dd class="text-primary font-medium">{{ licenseInfo.status || '—' }}</dd>
            </div>
            <div class="flex justify-between gap-2">
              <dt class="text-muted">Product</dt>
              <dd class="text-secondary truncate max-w-[60%] text-right">{{ licenseInfo.product_id || '—' }}</dd>
            </div>
          </dl>
          <p v-else class="text-sm text-muted">No license payload</p>
        </Card>
      </div>
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

const chartOptionsLine = {
  plugins: { legend: { display: false } },
  scales: {
    x: { grid: { color: 'rgba(148,163,184,0.15)' }, ticks: { color: '#94a3b8', maxRotation: 45 } },
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

const revenueChartData = computed(() => {
  const rows = overview.value?.charts?.revenue_by_month
  if (!rows?.length) return null
  return {
    labels: rows.map((r) => r.month),
    datasets: [
      {
        label: 'Revenue',
        data: rows.map((r) => Number(r.amount_cents || 0) / 100),
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.12)',
        fill: true,
        tension: 0.3,
      },
    ],
  }
})

const expenseDoughnutData = computed(() => {
  const rows = overview.value?.charts?.expense_by_category
  if (!rows?.length) return null
  const palette = ['#06b6d4', '#8b5cf6', '#ec4899', '#f97316', '#22c55e', '#eab308']
  return {
    labels: rows.map((r) => r.category || 'unknown'),
    datasets: [
      {
        data: rows.map((r) => r.amount_cents),
        backgroundColor: rows.map((_, i) => palette[i % palette.length]),
      },
    ],
  }
})

const billingAlertKeys = computed(() => Object.keys(overview.value?.billing_alerts_rollup || {}))

async function load() {
  loading.value = true
  loadError.value = null
  licenseError.value = null
  try {
    const [{ data: ov }, lic] = await Promise.all([
      platformAPI.overview(),
      licenseAPI.status().catch((e) => ({ error: e })),
    ])
    overview.value = ov
    if (lic.error) {
      licenseInfo.value = null
      licenseError.value = normalizeApiError(lic.error).userMessage || 'License status unavailable'
    } else {
      licenseInfo.value = lic.data
    }
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
