<template>
  <div
    v-if="warnings.length"
    class="rounded-xl border border-amber-500/40 bg-amber-500/10 px-4 py-3 text-sm text-amber-900 dark:text-amber-100 space-y-2"
    role="status"
  >
    <p v-for="(w, i) in warnings" :key="i">{{ w }}</p>
    <router-link
      v-if="showSystemLink"
      to="/super-admin/system"
      class="inline-block text-xs font-medium text-indigo-600 dark:text-indigo-400 hover:underline"
    >
      Open System health →
    </router-link>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { publicAPI } from '@/services/api'

defineProps({
  showSystemLink: { type: Boolean, default: true },
})

const route = useRoute()
const deployment = ref(null)
const loadFailed = ref(false)

const warnings = computed(() => {
  const list = []
  if (loadFailed.value) return list
  const d = deployment.value
  if (!d) return list
  if (!d.platform_saas_enabled) {
    list.push(
      'Platform SaaS is disabled (PLATFORM_SAAS_ENABLED / deployment mode). Most Super Admin APIs will return 403 until enabled.'
    )
  }
  const onGateway =
    route.path.includes('/gateway-instances') || route.name === 'super-admin-gateway-instance-detail'
  if (onGateway && !d.platform_gateway_enabled) {
    list.push(
      'Gateway admin API is disabled. Set PLATFORM_GATEWAY_ENABLED=true on the backend and restart to list CodeCanyon instances.'
    )
  }
  if (route.path.includes('/billing') && !d.stripe_publishable_key_configured) {
    list.push('Stripe is not configured. Checkout and Customer Portal actions will fail until STRIPE_* keys are set.')
  }
  return list
})

onMounted(async () => {
  try {
    const { data } = await publicAPI.deployment()
    deployment.value = data
  } catch {
    loadFailed.value = true
  }
})
</script>
