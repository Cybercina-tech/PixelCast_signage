<template>
  <AppLayout>
    <div class="space-y-6">
      <!-- Status Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-gray-600">Online Screens</p>
              <p class="text-3xl font-bold text-green-600">{{ dashboardStore.stats.online_screens }}</p>
            </div>
            <div class="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
              <TvIcon class="w-6 h-6 text-green-600" />
            </div>
          </div>
        </Card>
        
        <Card>
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-gray-600">Offline Screens</p>
              <p class="text-3xl font-bold text-red-600">{{ dashboardStore.stats.offline_screens }}</p>
            </div>
            <div class="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
              <TvIcon class="w-6 h-6 text-red-600" />
            </div>
          </div>
        </Card>
        
        <Card>
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-gray-600">Commands in Queue</p>
              <p class="text-3xl font-bold text-yellow-600">{{ dashboardStore.stats.commands_in_queue }}</p>
            </div>
            <div class="w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center">
              <CommandLineIcon class="w-6 h-6 text-yellow-600" />
            </div>
          </div>
        </Card>
        
        <Card>
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-gray-600">Content Downloading</p>
              <p class="text-3xl font-bold text-blue-600">{{ dashboardStore.stats.content_downloading }}</p>
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
          <div class="space-y-4">
            <div
              v-for="activity in dashboardStore.activities.slice(0, 10)"
              :key="activity.id"
              class="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg"
            >
              <div class="flex-shrink-0">
                <div
                  :class="[
                    'w-2 h-2 rounded-full mt-2',
                    activity.type === 'command' ? 'bg-blue-500' : '',
                    activity.type === 'content' ? 'bg-green-500' : '',
                    activity.type === 'template' ? 'bg-purple-500' : '',
                  ]"
                ></div>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm text-gray-900">{{ activity.message }}</p>
                <p class="text-xs text-gray-500 mt-1">
                  {{ formatDate(activity.timestamp) }}
                </p>
              </div>
            </div>
            <div v-if="dashboardStore.activities.length === 0" class="text-center text-gray-500 py-8">
              No recent activities
            </div>
          </div>
        </Card>
        
        <Card title="Quick Actions">
          <div class="space-y-3">
            <router-link
              to="/screens"
              class="block w-full px-4 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition text-center"
            >
              Manage Screens
            </router-link>
            <router-link
              to="/templates"
              class="block w-full px-4 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition text-center"
            >
              Create Template
            </router-link>
            <router-link
              to="/commands"
              class="block w-full px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition text-center"
            >
              Send Command
            </router-link>
            <router-link
              to="/contents"
              class="block w-full px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition text-center"
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
import { computed, onMounted } from 'vue'
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
  const metrics = dashboardStore.metrics.cpu.slice(-20) || []
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
  const metrics = dashboardStore.metrics.memory.slice(-20) || []
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
  const metrics = dashboardStore.metrics.latency.slice(-20) || []
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

onMounted(async () => {
  await dashboardStore.fetchStats()
  await dashboardStore.fetchMetrics()
  await dashboardStore.fetchActivities()
  
  // Refresh stats every 30 seconds
  setInterval(() => {
    dashboardStore.fetchStats()
    dashboardStore.fetchMetrics()
    dashboardStore.fetchActivities()
  }, 30000)
})
</script>
