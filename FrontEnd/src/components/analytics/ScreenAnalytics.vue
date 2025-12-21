<template>
  <div class="space-y-6">
    <!-- Screen Statistics Summary -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <Card title="Screen Status Overview">
        <div v-if="analyticsStore.screenStats" class="space-y-4">
          <div class="flex items-center justify-between">
            <span class="text-gray-600">Online Screens</span>
            <span class="text-2xl font-bold text-green-600">
              {{ analyticsStore.screenStats.status_breakdown?.online || 0 }}
            </span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-gray-600">Offline Screens</span>
            <span class="text-2xl font-bold text-red-600">
              {{ analyticsStore.screenStats.status_breakdown?.offline || 0 }}
            </span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-gray-600">Total Screens</span>
            <span class="text-2xl font-bold text-gray-900">
              {{ analyticsStore.screenStats.status_breakdown?.total || 0 }}
            </span>
          </div>
        </div>
        <div v-else class="text-center text-gray-500 py-8">
          No screen statistics available
        </div>
      </Card>

      <Card title="Health Metrics">
        <div v-if="analyticsStore.screenStats?.health_metrics" class="space-y-4">
          <div class="flex items-center justify-between">
            <span class="text-gray-600">Avg CPU Usage</span>
            <span class="text-lg font-semibold">
              {{ analyticsStore.screenStats.health_metrics.avg_cpu_usage?.toFixed(1) || 'N/A' }}%
            </span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-gray-600">Avg Memory Usage</span>
            <span class="text-lg font-semibold">
              {{ analyticsStore.screenStats.health_metrics.avg_memory_usage?.toFixed(1) || 'N/A' }}%
            </span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-gray-600">Avg Latency</span>
            <span class="text-lg font-semibold">
              {{ analyticsStore.screenStats.health_metrics.avg_latency_ms?.toFixed(1) || 'N/A' }} ms
            </span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-gray-600">Max CPU Usage</span>
            <span class="text-lg font-semibold text-red-600">
              {{ analyticsStore.screenStats.health_metrics.max_cpu_usage?.toFixed(1) || 'N/A' }}%
            </span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-gray-600">Max Memory Usage</span>
            <span class="text-lg font-semibold text-red-600">
              {{ analyticsStore.screenStats.health_metrics.max_memory_usage?.toFixed(1) || 'N/A' }}%
            </span>
          </div>
        </div>
        <div v-else class="text-center text-gray-500 py-8">
          No health metrics available
        </div>
      </Card>
    </div>

    <!-- Screen List with Details Link -->
    <Card title="Screens">
      <div class="overflow-x-auto">
        <Table
          :columns="screenTableHeaders"
          :data="screenTableData"
        >
          <template #cell-is_online="{ value }">
            <span
              :class="[
                'px-2 py-1 rounded-full text-xs font-medium',
                value
                  ? 'bg-green-100 text-green-800'
                  : 'bg-red-100 text-red-800'
              ]"
            >
              {{ value ? 'Online' : 'Offline' }}
            </span>
          </template>
          <template #actions="{ row }">
            <button
              @click="viewScreenDetails(row.id)"
              class="text-indigo-600 hover:text-indigo-900 text-sm font-medium"
            >
              View Details
            </button>
          </template>
        </Table>
      </div>
    </Card>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAnalyticsStore } from '@/stores/analytics'
import { useScreensStore } from '@/stores/screens'
import Card from '@/components/common/Card.vue'
import Table from '@/components/common/Table.vue'

const router = useRouter()
const analyticsStore = useAnalyticsStore()
const screensStore = useScreensStore()

const screenTableHeaders = [
  { key: 'name', label: 'Name' },
  { key: 'device_id', label: 'Device ID' },
  { key: 'location', label: 'Location' },
  { key: 'status', label: 'Status' },
  { key: 'actions', label: 'Actions' },
]

const screenTableData = computed(() => {
  return screensStore.screens.map(screen => ({
    id: screen.id,
    name: screen.name,
    device_id: screen.device_id,
    location: screen.location || 'N/A',
    is_online: screen.is_online,
  }))
})

const viewScreenDetails = async (screenId) => {
  try {
    await analyticsStore.fetchScreenDetail(screenId)
    router.push(`/analytics/screens/${screenId}`)
  } catch (error) {
    console.error('Failed to fetch screen details:', error)
  }
}
</script>
