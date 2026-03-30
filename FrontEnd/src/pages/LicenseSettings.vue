<template>
  <AppLayout>
    <div class="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 class="text-2xl font-bold text-primary">License Settings</h1>
        <p class="text-muted mt-1">Manage activation and revalidation for your installation.</p>
      </div>

      <Card title="Current License Status">
        <div class="grid gap-3 sm:grid-cols-2">
          <div>
            <p class="text-xs text-muted">Status</p>
            <p class="text-sm font-semibold text-primary">{{ statusData.license_status || "unknown" }}</p>
          </div>
          <div>
            <p class="text-xs text-muted">Domain</p>
            <p class="text-sm text-primary">{{ statusData.activated_domain || "-" }}</p>
          </div>
          <div>
            <p class="text-xs text-muted">Product ID Source</p>
            <p class="text-sm text-primary">{{ statusData.product_id_source || "-" }}</p>
          </div>
          <div>
            <p class="text-xs text-muted">Grace Until</p>
            <p class="text-sm text-primary">{{ formatDate(statusData.grace_until) }}</p>
          </div>
        </div>

        <div class="mt-4 flex gap-2">
          <button type="button" class="btn-outline px-4 py-2 rounded-lg text-sm" @click="loadStatus" :disabled="loading">
            Refresh Status
          </button>
          <button type="button" class="btn-primary px-4 py-2 rounded-lg text-sm" @click="revalidate" :disabled="loading">
            Revalidate Now
          </button>
        </div>
      </Card>

      <Card title="Activate License">
        <div class="space-y-3">
          <div>
            <label class="label-base block text-sm mb-1">Purchase Code</label>
            <input v-model="form.purchase_code" type="text" class="input-base w-full px-3 py-2 rounded-lg" />
          </div>
          <div>
            <label class="label-base block text-sm mb-1">Domain (optional)</label>
            <input v-model="form.domain" type="text" class="input-base w-full px-3 py-2 rounded-lg" />
          </div>
          <div>
            <label class="label-base block text-sm mb-1">CodeCanyon Product ID Override (optional)</label>
            <input v-model="form.codecanyon_product_id_override" type="text" class="input-base w-full px-3 py-2 rounded-lg" />
          </div>
          <button type="button" class="btn-primary px-4 py-2 rounded-lg text-sm" @click="activate" :disabled="loading">
            Activate
          </button>
        </div>
      </Card>
    </div>
  </AppLayout>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import AppLayout from '@/components/layout/AppLayout.vue'
import Card from '@/components/common/Card.vue'
import { useNotification } from '@/composables/useNotification'
import { licenseAPI } from '@/services/api'

const notify = useNotification()
const loading = ref(false)
const statusData = ref({})
const form = ref({
  purchase_code: '',
  domain: '',
  codecanyon_product_id_override: '',
})

function formatDate(value) {
  if (!value) return '-'
  try {
    return new Date(value).toLocaleString()
  } catch {
    return String(value)
  }
}

async function loadStatus() {
  loading.value = true
  try {
    const { data } = await licenseAPI.status()
    statusData.value = data || {}
  } catch (error) {
    notify.error(error?.response?.data?.message || 'Failed to load license status')
  } finally {
    loading.value = false
  }
}

async function revalidate() {
  loading.value = true
  try {
    const { data } = await licenseAPI.revalidate({ force: true })
    notify.success(data?.message || 'License revalidated')
    await loadStatus()
  } catch (error) {
    notify.error(error?.response?.data?.message || 'Revalidation failed')
  } finally {
    loading.value = false
  }
}

async function activate() {
  if (!form.value.purchase_code?.trim()) {
    notify.error('Purchase code is required')
    return
  }
  loading.value = true
  try {
    const payload = {
      purchase_code: form.value.purchase_code.trim(),
      domain: form.value.domain.trim(),
      codecanyon_product_id_override: form.value.codecanyon_product_id_override.trim(),
    }
    const { data } = await licenseAPI.activate(payload)
    notify.success(data?.message || 'License activated')
    await loadStatus()
  } catch (error) {
    notify.error(error?.response?.data?.message || 'Activation failed')
  } finally {
    loading.value = false
  }
}

onMounted(loadStatus)
</script>
