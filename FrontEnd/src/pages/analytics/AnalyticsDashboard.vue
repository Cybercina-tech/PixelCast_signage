<template>
  <AppLayout>
    <div class="space-y-6">
      <!-- Header -->
      <div class="flex items-center justify-between">
        <h1 class="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
        <div class="flex items-center space-x-4">
          <!-- Date Range Filter -->
          <div class="flex items-center space-x-2">
            <input
              v-model="dateRange.start"
              type="date"
              class="px-3 py-2 border border-gray-300 rounded-lg text-sm"
            />
            <span class="text-gray-500">to</span>
            <input
              v-model="dateRange.end"
              type="date"
              class="px-3 py-2 border border-gray-300 rounded-lg text-sm"
            />
            <button
              @click="applyFilters"
              :disabled="analyticsStore.loading"
              class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 text-sm"
            >
              Apply
            </button>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="analyticsStore.loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        <p class="mt-2 text-gray-600">Loading analytics...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="analyticsStore.error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
        {{ analyticsStore.error }}
      </div>

      <!-- Analytics Content -->
      <div v-else class="space-y-6">
        <!-- Overview Cards -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm text-gray-600">Total Screens</p>
                <p class="text-3xl font-bold text-gray-900">
                  {{ analyticsStore.screenStats?.total_screens || 0 }}
                </p>
              </div>
              <TvIcon class="w-12 h-12 text-indigo-600" />
            </div>
          </Card>

          <Card>
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm text-gray-600">Health Score</p>
                <p class="text-3xl font-bold text-green-600">
                  {{ analyticsStore.screenStats?.health_score?.toFixed(1) || 0 }}%
                </p>
              </div>
              <ChartBarIcon class="w-12 h-12 text-green-600" />
            </div>
          </Card>

          <Card>
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm text-gray-600">Commands Success Rate</p>
                <p class="text-3xl font-bold text-blue-600">
                  {{ analyticsStore.commandStats?.overall?.success_rate?.toFixed(1) || 0 }}%
                </p>
              </div>
              <CheckCircleIcon class="w-12 h-12 text-blue-600" />
            </div>
          </Card>

          <Card>
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm text-gray-600">Content Error Rate</p>
                <p class="text-3xl font-bold text-red-600">
                  {{ analyticsStore.contentStats?.download_statistics?.error_rate?.toFixed(1) || 0 }}%
                </p>
              </div>
              <ExclamationTriangleIcon class="w-12 h-12 text-red-600" />
            </div>
          </Card>
        </div>

        <!-- Tabs -->
        <div class="border-b border-gray-200">
          <nav class="-mb-px flex space-x-8">
            <button
              v-for="tab in tabs"
              :key="tab.id"
              @click="activeTab = tab.id"
              :class="[
                'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm',
                activeTab === tab.id
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              ]"
            >
              {{ tab.label }}
            </button>
          </nav>
        </div>

        <!-- Screen Analytics Tab -->
        <div v-show="activeTab === 'screens'">
          <ScreenAnalytics />
        </div>

        <!-- Command Analytics Tab -->
        <div v-show="activeTab === 'commands'">
          <CommandAnalytics />
        </div>

        <!-- Content Analytics Tab -->
        <div v-show="activeTab === 'content'">
          <ContentAnalytics />
        </div>

        <!-- Template Analytics Tab -->
        <div v-show="activeTab === 'templates'">
          <TemplateAnalytics />
        </div>

        <!-- Activity Trends Tab -->
        <div v-show="activeTab === 'activity'">
          <ActivityTrends />
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAnalyticsStore } from '@/stores/analytics'
import AppLayout from '@/components/layout/AppLayout.vue'
import Card from '@/components/common/Card.vue'
import ScreenAnalytics from '@/components/analytics/ScreenAnalytics.vue'
import CommandAnalytics from '@/components/analytics/CommandAnalytics.vue'
import ContentAnalytics from '@/components/analytics/ContentAnalytics.vue'
import TemplateAnalytics from '@/components/analytics/TemplateAnalytics.vue'
import ActivityTrends from '@/components/analytics/ActivityTrends.vue'
import {
  TvIcon,
  ChartBarIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
} from '@heroicons/vue/24/outline'

const analyticsStore = useAnalyticsStore()

const activeTab = ref('screens')
const dateRange = ref({
  start: null,
  end: null,
})

const tabs = [
  { id: 'screens', label: 'Screens' },
  { id: 'commands', label: 'Commands' },
  { id: 'content', label: 'Content' },
  { id: 'templates', label: 'Templates' },
  { id: 'activity', label: 'Activity Trends' },
]

const applyFilters = async () => {
  const params = {}
  if (dateRange.value.start) {
    params.start_date = dateRange.value.start
  }
  if (dateRange.value.end) {
    params.end_date = dateRange.value.end
  }

  analyticsStore.setFilters(params)

  // Fetch all analytics data
  try {
    await Promise.all([
      analyticsStore.fetchScreenStatistics(params),
      analyticsStore.fetchCommandStatistics(params),
      analyticsStore.fetchContentStatistics(params),
      analyticsStore.fetchTemplateStatistics(params),
    ])
  } catch (error) {
    console.error('Failed to fetch analytics:', error)
  }
}

onMounted(async () => {
  // Set default date range (last 30 days)
  const end = new Date()
  const start = new Date()
  start.setDate(start.getDate() - 30)
  
  dateRange.value.end = end.toISOString().split('T')[0]
  dateRange.value.start = start.toISOString().split('T')[0]

  await applyFilters()
  
  // Also fetch activity trends
  try {
    await analyticsStore.fetchActivityTrends()
  } catch (error) {
    console.error('Failed to fetch activity trends:', error)
  }
})
</script>
