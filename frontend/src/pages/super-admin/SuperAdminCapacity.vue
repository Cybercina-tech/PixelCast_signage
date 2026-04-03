<template>
  <div class="space-y-6">
    <div class="flex flex-wrap justify-between items-center gap-4">
      <div>
        <h1 class="text-2xl font-bold text-primary">Capacity planning</h1>
        <p class="text-sm text-muted mt-1">Per-tenant usage vs device limits</p>
      </div>
      <button type="button" class="btn-outline px-4 py-2 rounded-lg text-sm" :disabled="loading" @click="load">Refresh</button>
    </div>

    <div
      v-if="loadError"
      class="rounded-2xl border border-amber-500/40 bg-amber-500/10 px-4 py-3 text-sm text-amber-900 dark:text-amber-100"
    >
      {{ loadError }}
    </div>

    <Card>
      <div v-if="loading" class="text-center py-10 text-muted">Loading…</div>
      <div v-else-if="!sortedRows.length" class="text-center py-12 text-muted">No tenants</div>
      <div v-else class="space-y-4">
        <div class="grid gap-3 lg:hidden">
          <article
            v-for="row in sortedRows"
            :key="`m-${row.id}`"
            class="rounded-xl border border-border-color/70 bg-card/50 p-4 space-y-2"
          >
            <div class="flex justify-between gap-2">
              <h3 class="font-semibold text-primary">{{ row.name }}</h3>
              <span class="text-[11px] px-2 py-1 rounded-full border border-border-color/60 capitalize">{{ row.subscription_status }}</span>
            </div>
            <div class="grid grid-cols-2 gap-2 text-xs text-secondary">
              <p>Screens: <span class="text-primary font-medium">{{ row.screen_count }}</span></p>
              <p>Users: <span class="text-primary font-medium">{{ row.user_count }}</span></p>
              <p>Active users: <span class="text-primary font-medium">{{ row.active_user_count }}</span></p>
              <p>Sessions: <span class="text-primary font-medium">{{ row.active_session_count }}</span></p>
              <p class="col-span-2">Device limit: {{ row.device_limit ?? '—' }}</p>
            </div>
          </article>
        </div>

        <div class="hidden lg:block overflow-x-auto">
          <table class="min-w-full text-sm">
            <thead>
              <tr class="border-b border-border-color text-left text-muted">
                <th class="py-2 pr-4">Tenant</th>
                <th class="py-2 pr-4">Screens</th>
                <th class="py-2 pr-4">Users</th>
                <th class="py-2 pr-4">Active users</th>
                <th class="py-2 pr-4">Active sessions</th>
                <th class="py-2 pr-4">Device limit</th>
                <th class="py-2 pr-4">Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in sortedRows" :key="row.id" class="border-b border-border-color/60">
                <td class="py-2 pr-4 font-medium text-primary">{{ row.name }}</td>
                <td class="py-2 pr-4">{{ row.screen_count }}</td>
                <td class="py-2 pr-4">{{ row.user_count }}</td>
                <td class="py-2 pr-4">{{ row.active_user_count }}</td>
                <td class="py-2 pr-4">{{ row.active_session_count }}</td>
                <td class="py-2 pr-4">{{ row.device_limit ?? '—' }}</td>
                <td class="py-2 pr-4">
                  <span class="text-[11px] px-2 py-1 rounded-full border capitalize">{{ row.subscription_status }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </Card>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import Card from '@/components/common/Card.vue'
import api from '@/services/api'
import { normalizeApiError } from '@/utils/apiError'

const loading = ref(true)
const loadError = ref(null)
const rows = ref([])

const sortedRows = computed(() => {
  const list = [...rows.value]
  list.sort((a, b) => Number(b.screen_count || 0) - Number(a.screen_count || 0))
  return list
})

async function load() {
  loading.value = true
  loadError.value = null
  try {
    const { data } = await api.get('/platform/capacity/')
    rows.value = data?.tenants || []
  } catch (e) {
    loadError.value = normalizeApiError(e).userMessage || 'Could not load capacity'
    rows.value = []
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>
