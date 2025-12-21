<template>
  <div class="space-y-6">
    <!-- Download Statistics -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <Card>
        <div class="text-center">
          <p class="text-sm text-gray-600 mb-2">Total Downloads</p>
          <p class="text-3xl font-bold text-gray-900">
            {{ analyticsStore.contentStats?.download_statistics?.total_downloads || 0 }}
          </p>
        </div>
      </Card>

      <Card>
        <div class="text-center">
          <p class="text-sm text-gray-600 mb-2">Successful</p>
          <p class="text-3xl font-bold text-green-600">
            {{ analyticsStore.contentStats?.download_statistics?.successful || 0 }}
          </p>
        </div>
      </Card>

      <Card>
        <div class="text-center">
          <p class="text-sm text-gray-600 mb-2">Failed</p>
          <p class="text-3xl font-bold text-red-600">
            {{ analyticsStore.contentStats?.download_statistics?.failed || 0 }}
          </p>
        </div>
      </Card>

      <Card>
        <div class="text-center">
          <p class="text-sm text-gray-600 mb-2">Error Rate</p>
          <p class="text-3xl font-bold text-red-600">
            {{ analyticsStore.contentStats?.download_statistics?.error_rate?.toFixed(1) || 0 }}%
          </p>
        </div>
      </Card>
    </div>

    <!-- Type Distribution -->
    <Card title="Content Type Distribution">
      <div v-if="analyticsStore.contentStats?.type_distribution?.length > 0" class="space-y-4">
        <div
          v-for="type in analyticsStore.contentStats.type_distribution"
          :key="type.type"
          class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
        >
          <div class="flex items-center space-x-3">
            <span class="font-medium text-gray-900">{{ type.type }}</span>
            <span class="text-sm text-gray-500">({{ type.count }} items)</span>
          </div>
          <div class="flex items-center space-x-2">
            <div class="w-32 bg-gray-200 rounded-full h-2">
              <div
                class="bg-indigo-600 h-2 rounded-full"
                :style="{ width: `${type.percentage}%` }"
              ></div>
            </div>
            <span class="text-sm font-medium text-gray-700 w-12 text-right">
              {{ type.percentage.toFixed(1) }}%
            </span>
          </div>
        </div>
      </div>
      <div v-else class="text-center text-gray-500 py-8">
        No content type distribution available
      </div>
    </Card>

    <!-- Downloads by Type -->
    <Card title="Downloads by Content Type">
      <div v-if="analyticsStore.contentStats?.downloads_by_type?.length > 0" class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Successful</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Failed</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="stat in analyticsStore.contentStats.downloads_by_type" :key="stat.type">
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                {{ stat.type }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ stat.total }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-green-600">{{ stat.successful }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-red-600">{{ stat.failed }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else class="text-center text-gray-500 py-8">
        No download statistics by type available
      </div>
    </Card>
  </div>
</template>

<script setup>
import { useAnalyticsStore } from '@/stores/analytics'
import Card from '@/components/common/Card.vue'

const analyticsStore = useAnalyticsStore()
</script>
