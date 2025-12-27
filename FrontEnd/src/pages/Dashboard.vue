<template>
  <AppLayout>
    <div class="space-y-6">
      <!-- Status Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-zinc-600 dark:text-zinc-400">Online Screens</p>
              <p class="text-3xl font-semibold text-green-600 dark:text-green-500 mt-1">{{ dashboardStore.stats.online_screens }}</p>
            </div>
            <div class="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
              <TvIcon class="w-6 h-6 text-green-600" />
            </div>
          </div>
        </Card>
        
        <Card>
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-zinc-600 dark:text-zinc-400">Offline Screens</p>
              <p class="text-3xl font-semibold text-red-600 dark:text-red-500 mt-1">{{ dashboardStore.stats.offline_screens }}</p>
            </div>
            <div class="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
              <TvIcon class="w-6 h-6 text-red-600" />
            </div>
          </div>
        </Card>
        
        <Card>
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-zinc-600 dark:text-zinc-400">Commands in Queue</p>
              <p class="text-3xl font-semibold text-yellow-600 dark:text-yellow-500 mt-1">{{ dashboardStore.stats.commands_in_queue }}</p>
            </div>
            <div class="w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center">
              <CommandLineIcon class="w-6 h-6 text-yellow-600" />
            </div>
          </div>
        </Card>
        
        <Card>
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-zinc-600 dark:text-zinc-400">Content Downloading</p>
              <p class="text-3xl font-semibold text-blue-600 dark:text-blue-500 mt-1">{{ dashboardStore.stats.content_downloading }}</p>
            </div>
            <div class="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
              <ArrowDownTrayIcon class="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </Card>
      </div>
      
      <!-- Charts -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card title="CPU Usage" class="lg:col-span-1">
          <Chart
            type="line"
            :data="cpuChartData"
            :options="chartOptions"
          />
        </Card>
        
        <Card title="Memory Usage" class="lg:col-span-1">
          <Chart
            type="line"
            :data="memoryChartData"
            :options="chartOptions"
          />
        </Card>
        
        <Card title="Latency" class="lg:col-span-1">
          <Chart
            type="line"
            :data="latencyChartData"
            :options="chartOptions"
          />
        </Card>
      </div>
      
      <!-- Recent Activities & Quick Actions -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Recent Activities">
          <div v-if="dashboardStore.loading && (!dashboardStore.activities || dashboardStore.activities.length === 0)" class="text-center text-muted py-8">
            Loading activities...
          </div>
          <div v-else-if="dashboardStore.error && (!dashboardStore.activities || dashboardStore.activities.length === 0)" class="text-center text-error py-8">
            {{ dashboardStore.error }}
          </div>
          <div v-else-if="!dashboardStore.activities || dashboardStore.activities.length === 0" class="text-center text-muted py-8">
            No recent activities
          </div>
          <div v-else class="space-y-4 max-h-[600px] overflow-y-auto">
            <div
              v-for="activity in dashboardStore.activities.slice(0, 10)"
              :key="activity.id"
              class="flex items-start space-x-3 p-3 bg-slate-50 dark:bg-slate-800/50 rounded-xl transition-all duration-200 hover:bg-slate-100 dark:hover:bg-slate-800"
            >
              <div class="flex-shrink-0">
                <div
                  :class="[
                    'w-2 h-2 rounded-full mt-2',
                    activity.type === 'command' ? 'bg-blue-500' : '',
                    activity.type === 'content' ? 'bg-emerald-500' : '',
                    activity.type === 'screen' ? 'bg-purple-500' : '',
                    activity.type === 'template' ? 'bg-indigo-500' : '',
                  ]"
                ></div>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm text-primary">{{ activity.message }}</p>
                <p class="text-xs text-muted mt-1">
                  {{ formatDate(activity.timestamp) }}
                </p>
              </div>
            </div>
          </div>
        </Card>
        
        <Card title="Quick Actions">
          <div class="space-y-3">
            <router-link
              to="/screens"
              class="block w-full px-4 py-3 btn-primary rounded-xl text-center transition-all duration-200"
            >
              Manage Screens
            </router-link>
            <router-link
              to="/templates"
              class="block w-full px-4 py-3 bg-gradient-to-r from-purple-600 to-purple-500 dark:from-purple-500 dark:to-purple-400 text-white dark:text-slate-900 rounded-xl hover:from-purple-700 hover:to-purple-600 dark:hover:from-purple-400 dark:hover:to-purple-300 transition-all duration-200 text-center font-semibold shadow-lg hover:shadow-xl"
            >
              Create Template
            </router-link>
            <router-link
              to="/commands"
              class="block w-full px-4 py-3 btn-secondary rounded-xl text-center transition-all duration-200"
            >
              Send Command
            </router-link>
            <router-link
              to="/contents"
              class="block w-full px-4 py-3 btn-success rounded-xl text-center transition-all duration-200"
            >
              Upload Content
            </router-link>
          </div>
        </Card>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { computed, onMounted, onUnmounted } from 'vue'
import { useDashboardStore } from '@/stores/dashboard'
import AppLayout from '@/components/layout/AppLayout.vue'
import Card from '@/components/common/Card.vue'
import Chart from '@/components/common/Chart.vue'
import {
  TvIcon,
  CommandLineIcon,
  ArrowDownTrayIcon,
} from '@heroicons/vue/24/outline'

const dashboardStore = useDashboardStore()

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString()
}

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    y: {
      beginAtZero: true,
      max: 100,
    },
  },
}

const cpuChartData = computed(() => {
  const metrics = (dashboardStore.metrics?.cpu || []).slice(-20)
  return {
    labels: metrics.map(m => new Date(m.time).toLocaleTimeString()),
    datasets: [
      {
        label: 'CPU Usage (%)',
        data: metrics.map(m => m.value),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4,
      },
    ],
  }
})

const memoryChartData = computed(() => {
  const metrics = (dashboardStore.metrics?.memory || []).slice(-20)
  return {
    labels: metrics.map(m => new Date(m.time).toLocaleTimeString()),
    datasets: [
      {
        label: 'Memory Usage (%)',
        data: metrics.map(m => m.value),
        borderColor: 'rgb(16, 185, 129)',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        tension: 0.4,
      },
    ],
  }
})

const latencyChartData = computed(() => {
  const metrics = (dashboardStore.metrics?.latency || []).slice(-20)
  return {
    labels: metrics.map(m => new Date(m.time).toLocaleTimeString()),
    datasets: [
      {
        label: 'Latency (ms)',
        data: metrics.map(m => m.value),
        borderColor: 'rgb(245, 158, 11)',
        backgroundColor: 'rgba(245, 158, 11, 0.1)',
        tension: 0.4,
      },
    ],
  }
})

let refreshInterval = null

onMounted(async () => {
  // Initial load
  await Promise.all([
    dashboardStore.fetchStats(),
    dashboardStore.fetchMetrics(),
    dashboardStore.fetchActivities(),
  ])
  
  // Refresh stats every 30 seconds
  refreshInterval = setInterval(async () => {
    try {
      await Promise.all([
        dashboardStore.fetchStats(),
        dashboardStore.fetchMetrics(),
        dashboardStore.fetchActivities(),
      ])
    } catch (error) {
      console.error('Error refreshing dashboard data:', error)
    }
  }, 30000)
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script>
