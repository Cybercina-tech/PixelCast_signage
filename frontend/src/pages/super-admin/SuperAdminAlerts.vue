<template>
  <div class="space-y-6">
    <div class="flex flex-wrap justify-between items-center gap-4">
      <div>
        <h1 class="text-2xl font-bold text-primary">Notifications &amp; communications</h1>
        <p class="text-sm text-muted mt-1">Delivery attempts across channels</p>
      </div>
      <div class="flex flex-wrap gap-2 items-center">
        <router-link to="/super-admin/smtp" class="btn-primary px-4 py-2 rounded-lg text-sm"> SMTP settings </router-link>
        <router-link to="/super-admin/tickets" class="btn-outline px-4 py-2 rounded-lg text-sm"> Ticket queue </router-link>
        <button type="button" class="btn-outline px-4 py-2 rounded-lg text-sm" :disabled="loading" @click="load">Refresh</button>
      </div>
    </div>

    <div class="card-base rounded-2xl p-4 border border-border-color/70 flex flex-wrap gap-4 justify-between items-center">
      <p v-if="ticketHint" class="text-xs text-muted">{{ ticketHint }}</p>
      <p v-else class="text-xs text-muted">Platform ticket tools available from the queue.</p>
    </div>

    <div
      v-if="loadError"
      class="rounded-2xl border border-amber-500/40 bg-amber-500/10 px-4 py-3 text-sm text-amber-900 dark:text-amber-100"
    >
      {{ loadError }}
    </div>

    <Card>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-4">
        <div>
          <label class="label-base block text-sm mb-1">Status</label>
          <select v-model="filters.status" class="select-base w-full px-3 py-2 rounded-lg">
            <option value="all">All</option>
            <option value="sent">Sent</option>
            <option value="failed">Failed</option>
            <option value="pending">Pending</option>
          </select>
        </div>
        <div>
          <label class="label-base block text-sm mb-1">Channel</label>
          <select v-model="filters.channel" class="select-base w-full px-3 py-2 rounded-lg">
            <option value="all">All</option>
            <option v-for="c in channelOptions" :key="c" :value="c">{{ c }}</option>
          </select>
        </div>
      </div>

      <div v-if="loading" class="text-center py-10 text-muted">Loading…</div>
      <div v-else-if="!filteredRows.length" class="text-center py-12 text-muted">No delivery logs match</div>
      <div v-else class="overflow-x-auto">
        <table class="min-w-full text-sm">
          <thead>
            <tr class="border-b border-border-color text-left text-muted">
              <th class="py-2 pr-4">Event</th>
              <th class="py-2 pr-4">Channel</th>
              <th class="py-2 pr-4">Status</th>
              <th class="py-2 pr-4">Sent at</th>
              <th class="py-2 pr-4">Error</th>
              <th class="py-2 pr-4">Retries</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in filteredRows" :key="row.id" class="border-b border-border-color/60">
              <td class="py-2 pr-4 font-mono text-xs text-primary">{{ row.event_key }}</td>
              <td class="py-2 pr-4 text-secondary">{{ row.channel_type || '—' }}</td>
              <td class="py-2 pr-4">
                <span class="text-[11px] px-2 py-1 rounded-full border">{{ row.status }}</span>
              </td>
              <td class="py-2 pr-4 text-muted whitespace-nowrap text-xs">{{ formatDate(row.sent_at || row.created_at) }}</td>
              <td class="py-2 pr-4 text-xs text-red-500/90 max-w-xs truncate" :title="row.error_message">
                {{ row.error_message || '—' }}
              </td>
              <td class="py-2 pr-4">{{ row.retry_count ?? 0 }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </Card>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import Card from '@/components/common/Card.vue'
import api, { platformTicketsAPI } from '@/services/api'
import { normalizeApiError } from '@/utils/apiError'

const loading = ref(true)
const loadError = ref(null)
const rows = ref([])
const ticketHint = ref('')
const filters = ref({ status: 'all', channel: 'all' })

const channelOptions = computed(() => {
  const s = new Set()
  for (const r of rows.value) {
    if (r.channel_type) s.add(r.channel_type)
  }
  return Array.from(s).sort()
})

const filteredRows = computed(() => {
  let list = rows.value
  if (filters.value.status !== 'all') {
    const want = filters.value.status.toLowerCase()
    list = list.filter((r) => String(r.status || '').toLowerCase().includes(want))
  }
  if (filters.value.channel !== 'all') {
    list = list.filter((r) => (r.channel_type || '') === filters.value.channel)
  }
  return list
})

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
  loadError.value = null
  try {
    const [feed, tix] = await Promise.all([
      api.get('/platform/communications/'),
      platformTicketsAPI.list({ page_size: 1 }).catch(() => null),
    ])
    rows.value = feed.data?.results || []
    if (tix?.data?.count != null) {
      ticketHint.value = `Open ticket queue: ${tix.data.count} item(s) (approx).`
    } else {
      ticketHint.value = ''
    }
  } catch (e) {
    loadError.value = normalizeApiError(e).userMessage || 'Could not load communications'
    rows.value = []
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>
