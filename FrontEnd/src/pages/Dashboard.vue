<template>
  <AppLayout>
    <!-- Animated Starry Background -->
    <div class="fixed inset-0 pointer-events-none overflow-hidden z-0">
      <!-- Animated Stars -->
      <div class="absolute inset-0" ref="starsContainer"></div>
      <!-- Gradient Glow -->
      <div class="absolute top-0 left-1/4 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl animate-pulse"></div>
      <div class="absolute bottom-0 right-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl animate-pulse" style="animation-delay: 1s;"></div>
      <div class="absolute top-1/2 left-1/2 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse" style="animation-delay: 2s;"></div>
    </div>

    <!-- Dashboard Content -->
    <div class="relative z-10 min-h-full space-y-6 md:space-y-8 pb-6 md:pb-8">
        <!-- Header with Live Clock -->
        <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 class="text-3xl md:text-4xl font-bold text-white mb-2">
              <span class="bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent animate-pulse">
                Command Center
              </span>
            </h1>
            <p class="text-slate-400">Real-time monitoring and control</p>
          </div>
          <!-- Live Clock Widget -->
          <div class="backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl p-4 md:p-6">
            <div class="text-center">
              <div class="text-2xl md:text-3xl font-mono font-bold text-white mb-1" style="text-shadow: 0 0 10px rgba(99, 102, 241, 0.5);">
                {{ currentTime }}
              </div>
              <div class="text-sm text-slate-400">{{ currentDate }}</div>
            </div>
          </div>
        </div>

        <!-- Loading Skeleton -->
        <div v-if="loading && !hasData" class="space-y-6 md:space-y-8">
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div v-for="i in 4" :key="i" class="backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl p-6 animate-pulse">
              <div class="h-4 bg-white/10 rounded w-24 mb-4"></div>
              <div class="h-8 bg-white/10 rounded w-16"></div>
            </div>
          </div>
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div class="backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl p-6 animate-pulse">
              <div class="h-6 bg-white/10 rounded w-32 mb-6"></div>
              <div class="h-48 bg-white/10 rounded"></div>
            </div>
            <div class="backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl p-6 animate-pulse">
              <div class="h-6 bg-white/10 rounded w-32 mb-6"></div>
              <div class="space-y-4">
                <div v-for="i in 5" :key="i" class="h-16 bg-white/10 rounded"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Main Dashboard Content -->
        <div v-else class="space-y-6 md:space-y-8">
          <!-- Hero Stat Cards -->
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <!-- Total Screens Card -->
            <div class="backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl p-6 hover:bg-white/10 transition-all duration-300 group relative overflow-hidden">
              <div class="absolute inset-0 bg-gradient-to-br from-indigo-500/0 to-indigo-500/10 opacity-0 group-hover:opacity-100 transition-opacity"></div>
              <div class="relative z-10">
                <div class="flex items-start justify-between mb-4">
                  <div>
                    <p class="text-sm font-medium text-slate-400 mb-1">Total Screens</p>
                    <p class="text-3xl font-bold text-white" style="text-shadow: 0 0 20px rgba(99, 102, 241, 0.5);">
                      {{ stats.totalScreens }}
                    </p>
                  </div>
                  <div class="w-12 h-12 rounded-xl bg-indigo-500/20 flex items-center justify-center group-hover:bg-indigo-500/30 transition-colors">
                    <TvIcon class="w-6 h-6 text-indigo-400" />
                  </div>
                </div>
                <!-- Sparkline Chart -->
                <div class="h-12 mt-4">
                  <svg class="w-full h-full" viewBox="0 0 100 40" preserveAspectRatio="none">
                    <polyline
                      :points="generateSparklinePoints(screenTrend)"
                      fill="none"
                      stroke="rgb(99, 102, 241)"
                      stroke-width="2"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      opacity="0.6"
                    />
                  </svg>
                </div>
              </div>
            </div>

            <!-- Online Now Card -->
            <div class="backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl p-6 hover:bg-white/10 transition-all duration-300 group relative overflow-hidden">
              <div class="absolute inset-0 bg-gradient-to-br from-emerald-500/0 to-emerald-500/10 opacity-0 group-hover:opacity-100 transition-opacity"></div>
              <div class="relative z-10">
                <div class="flex items-start justify-between mb-4">
                  <div>
                    <p class="text-sm font-medium text-slate-400 mb-1">Online Now</p>
                    <p class="text-3xl font-bold text-white" style="text-shadow: 0 0 20px rgba(16, 185, 129, 0.5);">
                      {{ stats.onlineScreens }}
                    </p>
                  </div>
                  <div class="w-12 h-12 rounded-xl bg-emerald-500/20 flex items-center justify-center group-hover:bg-emerald-500/30 transition-colors">
                    <CheckCircleIcon class="w-6 h-6 text-emerald-400" />
                  </div>
                </div>
                <!-- Sparkline Chart -->
                <div class="h-12 mt-4">
                  <svg class="w-full h-full" viewBox="0 0 100 40" preserveAspectRatio="none">
                    <polyline
                      :points="generateSparklinePoints(onlineTrend)"
                      fill="none"
                      stroke="rgb(16, 185, 129)"
                      stroke-width="2"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      opacity="0.6"
                    />
                  </svg>
                </div>
              </div>
            </div>

            <!-- Storage Used Card -->
            <div class="backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl p-6 hover:bg-white/10 transition-all duration-300 group relative overflow-hidden">
              <div class="absolute inset-0 bg-gradient-to-br from-blue-500/0 to-blue-500/10 opacity-0 group-hover:opacity-100 transition-opacity"></div>
              <div class="relative z-10">
                <div class="flex items-start justify-between mb-4">
                  <div class="flex-1">
                    <p class="text-sm font-medium text-slate-400 mb-1">Storage Used</p>
                    <p class="text-3xl font-bold text-white mb-2" style="text-shadow: 0 0 20px rgba(59, 130, 246, 0.5);">
                      {{ storageUsedFormatted }}
                    </p>
                    <!-- Animated Progress Bar -->
                    <div class="w-full h-2 bg-white/10 rounded-full overflow-hidden">
                      <div
                        class="h-full bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full transition-all duration-1000 ease-out"
                        :style="{ width: `${storagePercentage}%` }"
                        style="box-shadow: 0 0 10px rgba(59, 130, 246, 0.5);"
                      ></div>
                    </div>
                    <p class="text-xs text-slate-400 mt-1">{{ storageUsedMB }} MB / {{ storageLimitMB }} MB</p>
                  </div>
                  <div class="w-12 h-12 rounded-xl bg-blue-500/20 flex items-center justify-center group-hover:bg-blue-500/30 transition-colors ml-4">
                    <ServerIcon class="w-6 h-6 text-blue-400" />
                  </div>
                </div>
              </div>
            </div>

            <!-- Active Templates Card -->
            <div class="backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl p-6 hover:bg-white/10 transition-all duration-300 group relative overflow-hidden">
              <div class="absolute inset-0 bg-gradient-to-br from-purple-500/0 to-purple-500/10 opacity-0 group-hover:opacity-100 transition-opacity"></div>
              <div class="relative z-10">
                <div class="flex items-start justify-between mb-4">
                  <div>
                    <p class="text-sm font-medium text-slate-400 mb-1">Active Templates</p>
                    <p class="text-3xl font-bold text-white" style="text-shadow: 0 0 20px rgba(168, 85, 247, 0.5);">
                      {{ stats.activeTemplates }}
                    </p>
                  </div>
                  <div class="w-12 h-12 rounded-xl bg-purple-500/20 flex items-center justify-center group-hover:bg-purple-500/30 transition-colors">
                    <DocumentTextIcon class="w-6 h-6 text-purple-400" />
                  </div>
                </div>
                <!-- Sparkline Chart -->
                <div class="h-12 mt-4">
                  <svg class="w-full h-full" viewBox="0 0 100 40" preserveAspectRatio="none">
                    <polyline
                      :points="generateSparklinePoints(templateTrend)"
                      fill="none"
                      stroke="rgb(168, 85, 247)"
                      stroke-width="2"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      opacity="0.6"
                    />
                  </svg>
                </div>
              </div>
            </div>
          </div>

          <!-- System Health & Connectivity -->
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- Screen Status Chart -->
            <div class="backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl p-6">
              <h3 class="text-lg font-semibold text-white mb-6">Screen Status</h3>
              <div class="flex items-center justify-center mb-6">
                <div class="relative w-48 h-48">
                  <!-- Donut Chart -->
                  <Chart
                    v-if="chartData"
                    :data="chartData"
                    :options="chartOptions"
                    type="doughnut"
                  />
                  <!-- Fallback Circular Progress -->
                  <div v-else class="relative w-48 h-48">
                    <svg class="transform -rotate-90 w-48 h-48">
                      <circle
                        cx="96"
                        cy="96"
                        r="88"
                        stroke="rgba(255, 255, 255, 0.1)"
                        stroke-width="16"
                        fill="none"
                      />
                      <circle
                        cx="96"
                        cy="96"
                        r="88"
                        :stroke-dasharray="circumference"
                        :stroke-dashoffset="circumference - (onlinePercentage / 100) * circumference"
                        stroke="rgb(99, 102, 241)"
                        stroke-width="16"
                        fill="none"
                        stroke-linecap="round"
                        class="transition-all duration-500"
                      />
                    </svg>
                    <div class="absolute inset-0 flex flex-col items-center justify-center">
                      <p class="text-4xl font-bold text-white">{{ onlinePercentage }}%</p>
                      <p class="text-sm text-slate-400 mt-1">Online</p>
                    </div>
                  </div>
                </div>
              </div>
              <div class="space-y-2">
                <div class="flex items-center justify-between text-sm">
                  <div class="flex items-center gap-2">
                    <div class="w-3 h-3 rounded-full bg-emerald-500" style="box-shadow: 0 0 8px rgba(16, 185, 129, 0.5);"></div>
                    <span class="text-slate-400">Online Screens</span>
                  </div>
                  <span class="text-white font-semibold">{{ stats.onlineScreens }}</span>
                </div>
                <div class="flex items-center justify-between text-sm">
                  <div class="flex items-center gap-2">
                    <div class="w-3 h-3 rounded-full bg-slate-500" style="box-shadow: 0 0 8px rgba(100, 116, 139, 0.5);"></div>
                    <span class="text-slate-400">Offline Screens</span>
                  </div>
                  <span class="text-white font-semibold">{{ stats.offlineScreens }}</span>
                </div>
              </div>
            </div>

            <!-- Recent Activities Card -->
            <div class="backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl p-6 flex flex-col h-full">
              <div class="flex items-center justify-between mb-6 flex-shrink-0">
                <h3 class="text-lg font-semibold text-white">Recent Activities</h3>
                <button
                  @click="refreshActivities"
                  class="text-sm text-indigo-400 hover:text-indigo-300 transition-colors"
                  :disabled="loading"
                >
                  {{ loading ? 'Loading...' : 'Refresh' }}
                </button>
              </div>
              <div class="space-y-4 flex-1 overflow-y-auto custom-scrollbar min-h-0">
                <div v-if="activities.length === 0 && !loading" class="text-center py-8 text-slate-400">
                  No recent activities
                </div>
                <div
                  v-for="activity in activities"
                  :key="activity.id"
                  class="flex items-start space-x-3 p-3 bg-white/5 rounded-xl hover:bg-white/10 transition-all duration-200"
                >
                  <div class="flex-shrink-0 mt-1">
                    <div
                      :class="[
                        'w-2 h-2 rounded-full',
                        activity.type === 'template' ? 'bg-indigo-500' : '',
                        activity.type === 'screen' ? 'bg-emerald-500' : '',
                        activity.type === 'command' ? 'bg-blue-500' : '',
                        activity.type === 'content' ? 'bg-purple-500' : '',
                        activity.type === 'alert' ? 'bg-red-500' : '',
                        activity.type === 'update' ? 'bg-yellow-500' : '',
                      ]"
                      :style="`box-shadow: 0 0 8px ${getActivityColor(activity.type)};`"
                    ></div>
                  </div>
                  <div class="flex-1 min-w-0">
                    <p class="text-sm text-white">{{ activity.message }}</p>
                    <p class="text-xs text-slate-400 mt-1">{{ formatTime(activity.timestamp) }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Quick Actions Grid -->
          <div class="backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl p-6">
            <h3 class="text-lg font-semibold text-white mb-6">Quick Actions</h3>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <router-link
                to="/templates?action=create"
                class="group flex items-center space-x-4 p-4 bg-white/5 hover:bg-indigo-500/20 border border-white/10 hover:border-indigo-500/50 rounded-xl transition-all duration-300"
              >
                <div class="w-12 h-12 rounded-xl bg-indigo-500/20 group-hover:bg-indigo-500/30 flex items-center justify-center transition-colors">
                  <PlusIcon class="w-6 h-6 text-indigo-400" />
                </div>
                <div>
                  <p class="text-sm font-semibold text-white">Create New Template</p>
                  <p class="text-xs text-slate-400">Design a new display template</p>
                </div>
              </router-link>

              <router-link
                to="/screens/add"
                class="group flex items-center space-x-4 p-4 bg-white/5 hover:bg-blue-500/20 border border-white/10 hover:border-blue-500/50 rounded-xl transition-all duration-300"
              >
                <div class="w-12 h-12 rounded-xl bg-blue-500/20 group-hover:bg-blue-500/30 flex items-center justify-center transition-colors">
                  <TvIcon class="w-6 h-6 text-blue-400" />
                </div>
                <div>
                  <p class="text-sm font-semibold text-white">Pair New Screen</p>
                  <p class="text-xs text-slate-400">Register a new display screen</p>
                </div>
              </router-link>

              <button
                @click="showEmergencyAlert = true"
                class="group flex items-center space-x-4 p-4 bg-white/5 hover:bg-red-500/20 border border-white/10 hover:border-red-500/50 rounded-xl transition-all duration-300 text-left w-full"
              >
                <div class="w-12 h-12 rounded-xl bg-red-500/20 group-hover:bg-red-500/30 flex items-center justify-center transition-colors">
                  <ExclamationTriangleIcon class="w-6 h-6 text-red-400" />
                </div>
                <div>
                  <p class="text-sm font-semibold text-white">Emergency Alert</p>
                  <p class="text-xs text-slate-400">Clear all screens</p>
                </div>
              </button>
            </div>
          </div>

          <!-- Recent Templates -->
          <div class="backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl p-6">
            <div class="flex items-center justify-between mb-6">
              <h3 class="text-lg font-semibold text-white">Recent Templates</h3>
              <router-link
                to="/templates"
                class="text-sm text-indigo-400 hover:text-indigo-300 transition-colors"
              >
                View All →
              </router-link>
            </div>
            <div v-if="recentTemplates.length === 0" class="text-center py-8 text-slate-400">
              No templates yet. Create your first template!
            </div>
            <div v-else class="flex space-x-4 overflow-x-auto pb-4 custom-scrollbar">
              <div
                v-for="template in recentTemplates"
                :key="template.id"
                class="flex-shrink-0 group cursor-pointer"
                @click="$router.push(`/templates/${template.id}`)"
              >
                <div class="w-64 bg-white/5 border border-white/10 rounded-xl overflow-hidden hover:border-indigo-500/50 transition-all duration-300">
                  <!-- Template Preview (16:9 aspect ratio) -->
                  <div class="aspect-video bg-gradient-to-br from-indigo-500/20 to-blue-500/20 flex items-center justify-center relative overflow-hidden">
                    <div class="absolute inset-0 bg-grid-pattern opacity-10"></div>
                    <div class="relative z-10 text-center p-4">
                      <DocumentTextIcon class="w-12 h-12 text-indigo-400 mx-auto mb-2" />
                      <p class="text-xs text-slate-300 font-medium">{{ template.name }}</p>
                    </div>
                    <div class="absolute top-2 right-2">
                      <span
                        :class="[
                          'px-2 py-1 rounded text-xs font-medium',
                          template.is_active ? 'bg-emerald-500/20 text-emerald-400' : 'bg-slate-500/20 text-slate-400'
                        ]"
                      >
                        {{ template.is_active ? 'Active' : 'Draft' }}
                      </span>
                    </div>
                  </div>
                  <div class="p-4">
                    <p class="text-sm font-semibold text-white mb-1">{{ template.name }}</p>
                    <p class="text-xs text-slate-400">{{ formatTime(template.updated_at || template.created_at) }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
    </div>

    <!-- Emergency Alert Modal -->
    <div
      v-if="showEmergencyAlert"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm"
      @click.self="showEmergencyAlert = false"
    >
      <div class="backdrop-blur-md bg-slate-900/95 border border-white/10 rounded-2xl p-6 max-w-md w-full">
        <div class="flex items-center space-x-3 mb-4">
          <div class="w-12 h-12 rounded-xl bg-red-500/20 flex items-center justify-center">
            <ExclamationTriangleIcon class="w-6 h-6 text-red-400" />
          </div>
          <h3 class="text-lg font-semibold text-white">Emergency Alert</h3>
        </div>
        <p class="text-sm text-slate-400 mb-6">
          This will clear all screens and display an emergency message. Are you sure you want to proceed?
        </p>
        <div class="flex space-x-3">
          <button
            @click="showEmergencyAlert = false"
            class="flex-1 px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl text-white transition-colors"
          >
            Cancel
          </button>
          <button
            @click="handleEmergencyAlert"
            class="flex-1 px-4 py-2 bg-red-500/20 hover:bg-red-500/30 border border-red-500/50 rounded-xl text-red-400 transition-colors"
          >
            Clear All Screens
          </button>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useDashboardStore } from '@/stores/dashboard'
import { useTemplatesStore } from '@/stores/templates'
import { useScreensStore } from '@/stores/screens'
import { useNotification } from '@/composables/useNotification'
import { contentsAPI } from '@/services/api'
import AppLayout from '@/components/layout/AppLayout.vue'
import Chart from '@/components/common/Chart.vue'
import {
  TvIcon,
  CheckCircleIcon,
  ServerIcon,
  DocumentTextIcon,
  PlusIcon,
  ExclamationTriangleIcon,
} from '@heroicons/vue/24/outline'

const router = useRouter()
const dashboardStore = useDashboardStore()
const templatesStore = useTemplatesStore()
const screensStore = useScreensStore()
const notify = useNotification()

// State
const loading = ref(true)
const showEmergencyAlert = ref(false)
const currentTime = ref('')
const currentDate = ref('')
const starsContainer = ref(null)

// Stats
const stats = computed(() => ({
  totalScreens: (dashboardStore.stats?.online_screens || 0) + (dashboardStore.stats?.offline_screens || 0),
  onlineScreens: dashboardStore.stats?.online_screens || 0,
  offlineScreens: dashboardStore.stats?.offline_screens || 0,
  activeTemplates: templatesStore.activeTemplates?.length || 0,
}))

// Storage stats (mock for now - can be enhanced with real API)
const storageUsedMB = ref(0)
const storageLimitMB = ref(500) // 500 MB default
const storagePercentage = computed(() => {
  if (storageLimitMB.value === 0) return 0
  return Math.min(100, Math.round((storageUsedMB.value / storageLimitMB.value) * 100))
})
const storageUsedFormatted = computed(() => `${storagePercentage.value}%`)

// Activities
const activities = computed(() => {
  return dashboardStore.activities || []
})

// Recent Templates
const recentTemplates = computed(() => {
  return templatesStore.templates
    .sort((a, b) => {
      const dateA = new Date(a.updated_at || a.created_at)
      const dateB = new Date(b.updated_at || b.created_at)
      return dateB - dateA
    })
    .slice(0, 4)
})

// Chart Data
const chartData = computed(() => {
  if (stats.value.totalScreens === 0) return null
  
  return {
    labels: ['Online', 'Offline'],
    datasets: [{
      data: [stats.value.onlineScreens, stats.value.offlineScreens],
      backgroundColor: [
        'rgba(16, 185, 129, 0.8)',
        'rgba(100, 116, 139, 0.8)',
      ],
      borderColor: [
        'rgba(16, 185, 129, 1)',
        'rgba(100, 116, 139, 1)',
      ],
      borderWidth: 2,
    }],
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false,
    },
    tooltip: {
      backgroundColor: 'rgba(15, 23, 42, 0.9)',
      titleColor: 'rgb(255, 255, 255)',
      bodyColor: 'rgb(255, 255, 255)',
      borderColor: 'rgba(255, 255, 255, 0.1)',
      borderWidth: 1,
    },
  },
  cutout: '70%',
}

// Computed properties
const onlinePercentage = computed(() => {
  if (stats.value.totalScreens === 0) return 0
  return Math.round((stats.value.onlineScreens / stats.value.totalScreens) * 100)
})

const circumference = computed(() => {
  return 2 * Math.PI * 88 // radius = 88
})

const hasData = computed(() => {
  return stats.value.totalScreens > 0 || activities.value.length > 0 || recentTemplates.value.length > 0
})

// Trend data (simplified - can be enhanced with real historical data)
const screenTrend = computed(() => {
  const base = stats.value.totalScreens
  return [base - 2, base - 1, base, base, base, base, base]
})

const onlineTrend = computed(() => {
  const base = stats.value.onlineScreens
  return [base - 2, base - 1, base, base, base, base, base]
})

const templateTrend = computed(() => {
  const base = stats.value.activeTemplates
  return [base - 1, base, base, base, base, base, base]
})

// Helper functions
const generateSparklinePoints = (data) => {
  if (!data || data.length === 0) return ''
  const max = Math.max(...data)
  const min = Math.min(...data)
  const range = max - min || 1
  const width = 100
  const height = 40
  const stepX = width / (data.length - 1)
  
  return data.map((value, index) => {
    const x = index * stepX
    const y = height - ((value - min) / range) * height
    return `${x},${y}`
  }).join(' ')
}

const formatTime = (date) => {
  if (!date) return ''
  const now = new Date()
  const diff = now - new Date(date)
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)
  
  if (minutes < 1) return 'Just now'
  if (minutes < 60) return `${minutes}m ago`
  if (hours < 24) return `${hours}h ago`
  return `${days}d ago`
}

const getActivityColor = (type) => {
  const colors = {
    template: 'rgba(99, 102, 241, 0.5)',
    screen: 'rgba(16, 185, 129, 0.5)',
    command: 'rgba(59, 130, 246, 0.5)',
    content: 'rgba(168, 85, 247, 0.5)',
    alert: 'rgba(239, 68, 68, 0.5)',
    update: 'rgba(234, 179, 8, 0.5)',
  }
  return colors[type] || 'rgba(255, 255, 255, 0.5)'
}

const updateClock = () => {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('en-US', { 
    hour12: false,
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
  currentDate.value = now.toLocaleDateString('en-US', { 
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const refreshActivities = async () => {
  await dashboardStore.fetchActivities()
}

const handleEmergencyAlert = async () => {
  // TODO: Implement emergency alert API call
  try {
    // This would call an API to send emergency command to all screens
    notify.success('Emergency alert sent to all screens')
    showEmergencyAlert.value = false
  } catch (error) {
    notify.error('Failed to send emergency alert')
  }
}

// Create animated stars
const createStars = () => {
  if (!starsContainer.value) return
  
  const starsCount = 50
  for (let i = 0; i < starsCount; i++) {
    const star = document.createElement('div')
    star.className = 'absolute rounded-full bg-white'
    star.style.width = `${Math.random() * 2 + 1}px`
    star.style.height = star.style.width
    star.style.left = `${Math.random() * 100}%`
    star.style.top = `${Math.random() * 100}%`
    star.style.opacity = Math.random() * 0.5 + 0.2
    star.style.animation = `starry-twinkle ${Math.random() * 3 + 2}s ease-in-out infinite`
    star.style.animationDelay = `${Math.random() * 2}s`
    starsContainer.value.appendChild(star)
  }
}

let clockInterval = null
let refreshInterval = null

onMounted(async () => {
  // Initialize clock
  updateClock()
  clockInterval = setInterval(updateClock, 1000)
  
  // Create animated stars
  createStars()
  
  // Fetch initial data - only use global/aggregated endpoints
  loading.value = true
  try {
    // Fetch data in parallel, but handle errors gracefully
    const results = await Promise.allSettled([
      dashboardStore.fetchStats(),
      dashboardStore.fetchActivities(),
      templatesStore.fetchTemplates(),
      screensStore.fetchScreens(), // This is a global list, not screen-specific
    ])
    
    // Check for errors and log them (but don't fail the whole dashboard)
    results.forEach((result, index) => {
      if (result.status === 'rejected') {
        const error = result.reason
        // Suppress screen_id errors - these are expected if no screen is selected
        if (error?.response?.data?.message?.includes('screen_id') || 
            error?.response?.data?.error?.includes('screen_id')) {
          console.debug('Suppressed screen_id error (expected for global dashboard):', error.message)
          return
        }
        console.warn(`Dashboard data fetch ${index} failed:`, error)
      }
    })
    
    // Calculate storage from content files (global endpoint)
    try {
      const contentsResponse = await contentsAPI.list({ page_size: 1000 })
      const contents = contentsResponse.data?.results || contentsResponse.data || []
      // Sum up file sizes from contents
      const totalBytes = contents.reduce((sum, content) => {
        return sum + (content.file_size || 0)
      }, 0)
      storageUsedMB.value = Math.round(totalBytes / (1024 * 1024))
    } catch (error) {
      // Suppress screen_id errors
      if (error?.response?.data?.message?.includes('screen_id') || 
          error?.response?.data?.error?.includes('screen_id')) {
        console.debug('Suppressed screen_id error in storage calculation')
      } else {
        console.warn('Could not fetch storage data:', error)
      }
      // Keep default value
    }
  } catch (error) {
    // Suppress screen_id errors
    if (error?.response?.data?.message?.includes('screen_id') || 
        error?.response?.data?.error?.includes('screen_id')) {
      console.debug('Suppressed screen_id error (expected for global dashboard)')
    } else {
      console.error('Error loading dashboard data:', error)
      notify.error('Failed to load dashboard data')
    }
  } finally {
    loading.value = false
  }
  
  // Refresh stats every 30 seconds - only global endpoints
  refreshInterval = setInterval(async () => {
    try {
      await Promise.allSettled([
        dashboardStore.fetchStats(),
        dashboardStore.fetchActivities(),
      ])
    } catch (error) {
      // Suppress screen_id errors and network errors
      if (error?.response?.data?.message?.includes('screen_id') || 
          error?.response?.data?.error?.includes('screen_id')) {
        console.debug('Suppressed screen_id error during refresh')
        return
      }
      if (error.message && !error.message.includes('Broken pipe')) {
        console.error('Error refreshing dashboard data:', error)
      }
    }
  }, 30000)
})

onUnmounted(() => {
  if (clockInterval) {
    clearInterval(clockInterval)
  }
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 3px;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}

.bg-grid-pattern {
  background-image: 
    linear-gradient(rgba(255, 255, 255, 0.1) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.1) 1px, transparent 1px);
  background-size: 20px 20px;
}
</style>
