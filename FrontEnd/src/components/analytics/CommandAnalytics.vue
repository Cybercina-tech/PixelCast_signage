<template>
  <div class="space-y-6">
    <!-- Overall Statistics -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <Card>
        <div class="text-center">
          <p class="text-sm text-gray-600 mb-2">Total Commands</p>
          <p class="text-3xl font-bold text-gray-900">
            {{ analyticsStore.commandStats?.overall?.total || 0 }}
          </p>
        </div>
      </Card>

      <Card>
        <div class="text-center">
          <p class="text-sm text-gray-600 mb-2">Success Rate</p>
          <p class="text-3xl font-bold text-green-600">
            {{ analyticsStore.commandStats?.overall?.success_rate?.toFixed(1) || 0 }}%
          </p>
        </div>
      </Card>

      <Card>
        <div class="text-center">
          <p class="text-sm text-gray-600 mb-2">Pending</p>
          <p class="text-3xl font-bold text-yellow-600">
            {{ analyticsStore.commandStats?.overall?.pending || 0 }}
          </p>
        </div>
      </Card>

      <Card>
        <div class="text-center">
          <p class="text-sm text-gray-600 mb-2">Failed</p>
          <p class="text-3xl font-bold text-red-600">
            {{ analyticsStore.commandStats?.overall?.failed || 0 }}
          </p>
        </div>
      </Card>
    </div>

    <!-- Statistics by Type -->
    <Card title="Commands by Type">
      <div v-if="analyticsStore.commandStats?.by_type?.length > 0" class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Pending</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Done</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Failed</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="stat in analyticsStore.commandStats.by_type" :key="stat.type">
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                {{ stat.type }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ stat.total }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-yellow-600">{{ stat.pending }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-green-600">{{ stat.done }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-red-600">{{ stat.failed }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else class="text-center text-gray-500 py-8">
        No command statistics available
      </div>
    </Card>

    <!-- Time Series Chart -->
    <Card title="Command Activity Over Time" v-if="analyticsStore.commandStats?.time_series?.length > 0">
      <Chart
        type="line"
        :data="timeSeriesChartData"
        :options="chartOptions"
      />
    </Card>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAnalyticsStore } from '@/stores/analytics'
import Card from '@/components/common/Card.vue'
import Chart from '@/components/common/Chart.vue'

const analyticsStore = useAnalyticsStore()

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    y: {
      beginAtZero: true,
    },
  },
}

const timeSeriesChartData = computed(() => {
  const timeSeries = analyticsStore.commandStats?.time_series || []
  return {
    labels: timeSeries.map(item => {
      if (!item.period) return ''
      const date = new Date(item.period)
      return date.toLocaleDateString()
    }),
    datasets: [
      {
        label: 'Total',
        data: timeSeries.map(item => item.total || 0),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
      },
      {
        label: 'Done',
        data: timeSeries.map(item => item.done || 0),
        borderColor: 'rgb(16, 185, 129)',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
      },
      {
        label: 'Failed',
        data: timeSeries.map(item => item.failed || 0),
        borderColor: 'rgb(239, 68, 68)',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
      },
    ],
  }
})
</script>
