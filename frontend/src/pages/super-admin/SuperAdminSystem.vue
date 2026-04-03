<template>
  <div class="space-y-8">
    <div class="flex flex-wrap justify-between items-center gap-4">
      <div>
        <h1 class="text-2xl font-bold text-primary">System health</h1>
        <p class="text-sm text-muted mt-1">Dependencies, deployment mode, and installation state</p>
      </div>
      <button type="button" class="btn-outline px-4 py-2 rounded-lg text-sm" :disabled="loading" @click="load">Refresh</button>
    </div>

    <div
      v-if="loadError"
      class="rounded-2xl border border-amber-500/40 bg-amber-500/10 px-4 py-3 text-sm text-amber-900 dark:text-amber-100"
    >
      {{ loadError }}
    </div>

    <div v-if="loading" class="grid gap-4 md:grid-cols-2">
      <div v-for="i in 4" :key="i" class="card-base rounded-2xl p-6 animate-pulse h-32" />
    </div>

    <template v-else>
      <div class="card-base rounded-2xl p-6 border border-border-color/80">
        <p class="text-xs uppercase tracking-wide text-muted mb-1">Application</p>
        <p class="text-lg font-semibold text-primary">ScreenGram {{ appVersion }}</p>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div class="card-base rounded-2xl p-5 border border-border-color/80">
          <p class="text-xs font-medium text-muted uppercase tracking-wide">DEPLOYMENT_MODE</p>
          <p class="text-xl font-bold text-primary mt-1">{{ deployment?.deployment_mode ?? '—' }}</p>
        </div>
        <div class="card-base rounded-2xl p-5 border border-border-color/80">
          <p class="text-xs font-medium text-muted uppercase tracking-wide">PLATFORM_SAAS_ENABLED (effective)</p>
          <p class="text-xl font-bold text-primary mt-1">
            {{ deployment?.platform_saas_enabled === true ? 'true' : deployment?.platform_saas_enabled === false ? 'false' : '—' }}
          </p>
        </div>
      </div>

      <Card title="Dependency checks">
        <div class="grid gap-3 sm:grid-cols-2">
          <div
            v-for="(check, key) in healthChecks"
            :key="key"
            class="rounded-xl border border-border-color/70 p-4 flex items-start justify-between gap-3"
          >
            <div>
              <p class="text-sm font-medium text-primary capitalize">{{ key }}</p>
              <p v-if="check?.error" class="text-xs text-red-500 mt-1">{{ check.error }}</p>
            </div>
            <span
              class="text-xs px-2 py-1 rounded-full border shrink-0"
              :class="check?.ok ? 'border-emerald-500/50 text-emerald-700 dark:text-emerald-200' : 'border-red-500/50 text-red-600'"
            >
              {{ check?.ok ? 'OK' : 'Error' }}
            </span>
          </div>
          <p v-if="!Object.keys(healthChecks).length" class="text-sm text-muted col-span-full">No checks returned</p>
        </div>
      </Card>

      <Card title="Deployment (public)">
        <dl class="text-sm space-y-2">
          <div class="flex justify-between gap-2">
            <dt class="text-muted">Stripe publishable key configured</dt>
            <dd class="text-primary">{{ deployment?.stripe_publishable_key_configured ? 'yes' : 'no' }}</dd>
          </div>
        </dl>
      </Card>

      <Card title="Installation (setup API)">
        <p v-if="setupMessage" class="text-sm text-secondary">{{ setupMessage }}</p>
        <pre v-else-if="setupPayload" class="text-xs bg-black/20 rounded-lg p-3 overflow-auto text-muted">{{ setupJson }}</pre>
        <p v-else class="text-sm text-muted">No setup payload</p>
      </Card>

      <Card title="License">
        <p v-if="licenseError" class="text-sm text-amber-600">{{ licenseError }}</p>
        <p v-else-if="licenseSnippet" class="text-xs text-muted font-mono break-all">{{ JSON.stringify(licenseSnippet).slice(0, 400) }}</p>
        <p v-else class="text-sm text-muted">No license data</p>
      </Card>

      <Card title="Error logs (admin)">
        <div v-if="adminErrorStatsError" class="text-sm text-amber-600">{{ adminErrorStatsError }}</div>
        <p v-else-if="errorStats" class="text-sm text-secondary">Admin error stats loaded — open the error dashboard from the sidebar for details.</p>
        <p v-else class="text-sm text-muted">No stats</p>
      </Card>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import Card from '@/components/common/Card.vue'
import api, { adminAPI, licenseAPI, publicAPI, setupAPI } from '@/services/api'
import { normalizeApiError } from '@/utils/apiError'

const appVersion = 'v1.0.1'
const loading = ref(true)
const loadError = ref(null)
const healthChecks = ref({})
const deployment = ref(null)
const setupPayload = ref(null)
const setupMessage = ref(null)
const errorStats = ref(null)
const adminErrorStatsError = ref(null)
const licenseSnippet = ref(null)
const licenseError = ref(null)

const setupJson = computed(() => {
  try {
    return JSON.stringify(setupPayload.value, null, 2)
  } catch {
    return ''
  }
})

async function load() {
  loading.value = true
  loadError.value = null
  adminErrorStatsError.value = null
  try {
    const [health, dep, setup, stats, lic] = await Promise.all([
      api.get('/platform/system-health/'),
      publicAPI.deployment(),
      setupAPI.status().catch((e) => ({ error: e })),
      adminAPI.errors.stats().catch((e) => ({ error: e })),
      licenseAPI.status().catch((e) => ({ error: e })),
    ])
    healthChecks.value = health.data?.checks || {}
    deployment.value = dep.data
    if (setup.error) {
      setupPayload.value = null
      setupMessage.value = normalizeApiError(setup.error).userMessage || 'Setup status not available (installed systems return 403).'
    } else {
      setupPayload.value = setup.data
      setupMessage.value = null
    }
    if (stats.error) {
      errorStats.value = null
      adminErrorStatsError.value = normalizeApiError(stats.error).userMessage || 'Admin stats unavailable'
    } else {
      errorStats.value = stats.data
    }
    if (lic.error) {
      licenseSnippet.value = null
      licenseError.value = normalizeApiError(lic.error).userMessage || 'License status unavailable'
    } else {
      licenseSnippet.value = lic.data
      licenseError.value = null
    }
  } catch (e) {
    loadError.value = normalizeApiError(e).userMessage || 'Could not load system health'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>
