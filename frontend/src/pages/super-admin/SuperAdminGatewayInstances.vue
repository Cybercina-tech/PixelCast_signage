<template>
  <div class="space-y-6">
    <div class="flex flex-wrap justify-between items-center gap-4">
      <div>
        <h1 class="text-2xl font-bold text-primary">CodeCanyon gateway instances</h1>
        <p class="text-sm text-muted mt-1">
          Self-hosted installs registered via <code class="text-xs">/api/gateway/</code> (X-Instance-Key), separate from
          the license registry
        </p>
      </div>
      <button type="button" class="btn-outline px-4 py-2 rounded-lg text-sm" :disabled="loading" @click="load">
        Refresh
      </button>
    </div>

    <div
      v-if="loadError"
      class="rounded-2xl border border-amber-500/40 bg-amber-500/10 px-4 py-3 text-sm text-amber-900 dark:text-amber-100"
    >
      {{ loadError }}
    </div>

    <div v-if="loading" class="card-base rounded-2xl p-8 animate-pulse h-32" />
    <Card v-else title="Instances">
      <div v-if="!rows.length" class="text-center py-10 text-muted text-sm">No gateway instances yet</div>
      <div v-else class="overflow-x-auto">
        <table class="min-w-full text-sm">
          <thead>
            <tr class="border-b border-border-color text-left text-muted">
              <th class="py-2 pr-4">Domain</th>
              <th class="py-2 pr-4">Status</th>
              <th class="py-2 pr-4">Online</th>
              <th class="py-2 pr-4">Version</th>
              <th class="py-2 pr-4">Screens</th>
              <th class="py-2 pr-4">Users</th>
              <th class="py-2 pr-4">Last heartbeat</th>
              <th class="py-2 pr-4">Usage at</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="row in rows"
              :key="row.id"
              class="border-b border-border-color/60 hover:bg-slate-50/50 dark:hover:bg-slate-800/30 align-top"
            >
              <td class="py-2 pr-4 font-mono text-xs text-primary">{{ row.domain }}</td>
              <td class="py-2 pr-4 text-xs">{{ row.license_status }}</td>
              <td class="py-2 pr-4">
                <span v-if="row.is_online" class="text-emerald-600 font-medium">Online</span>
                <span v-else class="text-rose-600 font-medium">Offline</span>
              </td>
              <td class="py-2 pr-4 text-xs">{{ row.version || '—' }}</td>
              <td class="py-2 pr-4 text-xs tabular-nums">{{ row.active_screens ?? '—' }}</td>
              <td class="py-2 pr-4 text-xs tabular-nums">{{ row.users_count ?? '—' }}</td>
              <td class="py-2 pr-4 text-xs text-muted">{{ formatDate(row.last_heartbeat_at) }}</td>
              <td class="py-2 pr-4 text-xs text-muted">{{ formatDate(row.usage_reported_at) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div
        v-if="rows.length"
        class="flex flex-wrap items-center justify-between gap-3 mt-4 pt-4 border-t border-border-color/60"
      >
        <span class="text-xs text-muted">{{ totalCount }} total · page {{ page }} / {{ totalPages || 1 }}</span>
        <div class="flex gap-2">
          <button
            type="button"
            class="btn-outline px-3 py-1.5 rounded-lg text-xs"
            :disabled="page <= 1 || loading"
            @click="prevPage"
          >
            Previous
          </button>
          <button
            type="button"
            class="btn-outline px-3 py-1.5 rounded-lg text-xs"
            :disabled="page >= totalPages || loading"
            @click="nextPage"
          >
            Next
          </button>
        </div>
      </div>
    </Card>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import Card from '@/components/common/Card.vue'
import { platformAPI } from '@/services/api'

const loading = ref(false)
const loadError = ref('')
const rows = ref([])
const totalCount = ref(0)
const page = ref(1)
const pageSize = ref(50)

const totalPages = computed(() => Math.max(1, Math.ceil(totalCount.value / pageSize.value)))

function formatDate(iso) {
  if (!iso) return '—'
  try {
    return new Date(iso).toLocaleString()
  } catch {
    return iso
  }
}

async function load() {
  loading.value = true
  loadError.value = ''
  try {
    const { data } = await platformAPI.gatewayInstances.list({
      page: page.value,
      page_size: pageSize.value,
    })
    rows.value = data.results || []
    totalCount.value = data.count ?? 0
  } catch (e) {
    loadError.value = e.response?.data?.detail || e.message || 'Failed to load gateway instances'
    rows.value = []
  } finally {
    loading.value = false
  }
}

function prevPage() {
  if (page.value > 1) {
    page.value -= 1
    load()
  }
}

function nextPage() {
  if (page.value < totalPages.value) {
    page.value += 1
    load()
  }
}

onMounted(() => load())
</script>
