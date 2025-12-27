<template>
  <div
    :class="[
      'fixed right-0 top-0 h-full bg-secondary/95 dark:bg-slate-900/95 backdrop-blur-lg border-l border-border-color transition-transform duration-300 z-50',
      isOpen ? 'translate-x-0' : 'translate-x-full',
    ]"
    class="w-96 max-w-[90vw] flex flex-col"
  >
    <!-- Header -->
    <div class="p-4 border-b border-border-color flex items-center justify-between bg-card dark:bg-slate-800">
      <div class="flex items-center gap-2">
        <ExclamationTriangleIcon class="w-6 h-6 text-red-500 dark:text-red-400" />
        <h3 class="text-lg font-semibold text-primary">Error Dashboard</h3>
        <span
          v-if="unresolvedCount > 0"
          class="ml-2 px-2 py-0.5 text-xs font-bold rounded-full bg-red-500 text-white"
        >
          {{ unresolvedCount }}
        </span>
      </div>
      <button
        @click="$emit('close')"
        class="p-1 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
        aria-label="Close error dashboard"
      >
        <XMarkIcon class="w-5 h-5 text-secondary" />
      </button>
    </div>

    <!-- Filters -->
    <div class="p-4 border-b border-border-color bg-card/30 space-y-3">
      <div class="flex gap-2">
        <select
          v-model="filters.level"
          class="select-base flex-1 px-3 py-2 text-sm rounded-lg"
        >
          <option value="">All Levels</option>
          <option value="CRITICAL">Critical</option>
          <option value="ERROR">Error</option>
          <option value="WARNING">Warning</option>
          <option value="INFO">Info</option>
          <option value="DEBUG">Debug</option>
        </select>
        <select
          v-model="filters.isResolved"
          class="select-base flex-1 px-3 py-2 text-sm rounded-lg"
        >
          <option value="">All</option>
          <option value="false">Unresolved</option>
          <option value="true">Resolved</option>
        </select>
      </div>
      <input
        v-model="filters.endpoint"
        type="text"
        placeholder="Filter by endpoint..."
        class="input-base w-full px-3 py-2 text-sm rounded-lg"
      />
      <div class="flex gap-2">
        <input
          v-model="filters.startDate"
          type="date"
          class="input-base flex-1 px-3 py-2 text-sm rounded-lg"
        />
        <input
          v-model="filters.endDate"
          type="date"
          class="input-base flex-1 px-3 py-2 text-sm rounded-lg"
        />
      </div>
    </div>

    <!-- Error List -->
    <div class="flex-1 overflow-y-auto p-4 space-y-2">
      <div v-if="loading" class="text-center py-8 text-slate-600 dark:text-slate-400">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-500"></div>
        <p class="mt-2">Loading errors...</p>
      </div>
      <div v-else-if="errors.length === 0" class="text-center py-8 text-slate-600 dark:text-slate-400">
        <CheckCircleIcon class="w-12 h-12 mx-auto mb-2 text-green-500" />
        <p>No errors found</p>
      </div>
      <div
        v-else
        v-for="error in errors"
        :key="error.id"
        @click="selectError(error)"
        :class="[
          'p-3 rounded-lg border cursor-pointer transition-all hover:shadow-md',
          selectedError?.id === error.id
            ? 'border-emerald-500 bg-emerald-50 dark:bg-emerald-900/20'
            : 'border-border-color bg-card hover:bg-slate-100 dark:hover:bg-slate-800',
          error.is_resolved
            ? 'opacity-60'
            : '',
        ]"
      >
        <div class="flex items-start justify-between gap-2">
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 mb-1">
              <span
                :class="[
                  'px-2 py-0.5 text-xs font-semibold rounded',
                  getLevelColor(error.level),
                ]"
              >
                {{ error.level }}
              </span>
              <span
                v-if="error.is_resolved"
                class="px-2 py-0.5 text-xs font-semibold rounded bg-green-500 text-white"
              >
                Resolved
              </span>
            </div>
            <p class="text-sm font-medium text-slate-900 dark:text-slate-50 truncate">
              {{ error.message.substring(0, 60) }}{{ error.message.length > 60 ? '...' : '' }}
            </p>
            <p v-if="error.endpoint" class="text-xs text-slate-600 dark:text-slate-400 mt-1 truncate">
              {{ error.endpoint }}
            </p>
            <p class="text-xs text-slate-500 dark:text-slate-500 mt-1">
              {{ formatTimestamp(error.timestamp) }}
            </p>
            <p v-if="error.user_username" class="text-xs text-slate-500 dark:text-slate-500">
              User: {{ error.user_username }}
            </p>
          </div>
        </div>
      </div>
      <div v-if="hasMore" class="text-center py-4">
        <button
          @click="loadMore"
          class="px-4 py-2 text-sm rounded-lg bg-emerald-500 text-white hover:bg-emerald-600 transition-colors"
        >
          Load More
        </button>
      </div>
    </div>

    <!-- Error Detail Modal -->
    <div
      v-if="selectedError"
      class="absolute inset-0 bg-black/50 dark:bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      @click.self="selectedError = null"
    >
      <div
        class="bg-card rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-hidden flex flex-col border border-border-color"
        @click.stop
      >
        <div class="p-4 border-b border-border-color flex items-center justify-between">
          <h4 class="text-lg font-semibold text-slate-900 dark:text-slate-50">Error Details</h4>
          <button
            @click="selectedError = null"
            class="p-1 rounded-lg hover:bg-card transition-colors"
          >
            <XMarkIcon class="w-5 h-5 text-slate-600 dark:text-slate-400" />
          </button>
        </div>
        <div class="flex-1 overflow-y-auto p-4 space-y-4">
          <div>
            <label class="text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase">Level</label>
            <span
              :class="[
                'ml-2 px-2 py-1 text-sm font-semibold rounded',
                getLevelColor(selectedError.level),
              ]"
            >
              {{ selectedError.level }}
            </span>
          </div>
          <div>
            <label class="text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase">Message</label>
            <p class="mt-1 text-sm text-slate-900 dark:text-slate-50">{{ selectedError.message }}</p>
          </div>
          <div v-if="selectedError.endpoint">
            <label class="text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase">Endpoint</label>
            <p class="mt-1 text-sm text-slate-900 dark:text-slate-50">{{ selectedError.endpoint }}</p>
          </div>
          <div v-if="selectedError.user_username">
            <label class="text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase">User</label>
            <p class="mt-1 text-sm text-slate-900 dark:text-slate-50">
              {{ selectedError.user_username }} ({{ selectedError.user_email }})
            </p>
          </div>
          <div>
            <label class="text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase">Timestamp</label>
            <p class="mt-1 text-sm text-slate-900 dark:text-slate-50">
              {{ formatTimestamp(selectedError.timestamp) }}
            </p>
          </div>
          <div v-if="selectedError.exception_type">
            <label class="text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase">Exception Type</label>
            <p class="mt-1 text-sm text-slate-900 dark:text-slate-50 font-mono">
              {{ selectedError.exception_type }}
            </p>
          </div>
          <div v-if="selectedError.stack_trace">
            <label class="text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase">Stack Trace</label>
            <pre
              class="mt-1 p-3 text-xs bg-slate-100 dark:bg-slate-800 rounded-lg overflow-x-auto text-slate-900 dark:text-slate-50 font-mono"
            >{{ selectedError.stack_trace }}</pre>
          </div>
          <div v-if="selectedError.metadata && Object.keys(selectedError.metadata).length > 0">
            <label class="text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase">Metadata</label>
            <pre
              class="mt-1 p-3 text-xs bg-slate-100 dark:bg-slate-800 rounded-lg overflow-x-auto text-slate-900 dark:text-slate-50 font-mono"
            >{{ JSON.stringify(selectedError.metadata, null, 2) }}</pre>
          </div>
        </div>
        <div class="p-4 border-t border-border-color flex justify-end gap-2">
          <button
            v-if="!selectedError.is_resolved"
            @click="resolveError(selectedError.id)"
            class="px-4 py-2 text-sm rounded-lg bg-green-500 text-white hover:bg-green-600 transition-colors"
          >
            Mark as Resolved
          </button>
          <button
            @click="selectedError = null"
            class="px-4 py-2 text-sm rounded-lg bg-slate-200 dark:bg-slate-700 text-slate-900 dark:text-slate-50 hover:bg-slate-300 dark:hover:bg-slate-600 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>

    <!-- Overlay for mobile -->
    <div
      v-if="isOpen"
      class="fixed inset-0 bg-black/50 dark:bg-black/70 backdrop-blur-sm z-40 md:hidden"
      @click="$emit('close')"
    ></div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import {
  ExclamationTriangleIcon,
  XMarkIcon,
  CheckCircleIcon,
} from '@heroicons/vue/24/outline'
import { adminAPI } from '@/services/api'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['close'])

const errors = ref([])
const selectedError = ref(null)
const loading = ref(false)
const unresolvedCount = ref(0)
const hasMore = ref(false)
const currentPage = ref(1)
const refreshInterval = ref(null)

const filters = ref({
  level: '',
  isResolved: '',
  endpoint: '',
  startDate: '',
  endDate: '',
})

const loadErrors = async (page = 1, reset = false) => {
  if (loading.value) return
  
  loading.value = true
  try {
    const params = {
      page,
      page_size: 20,
    }
    
    if (filters.value.level) {
      params.level = filters.value.level
    }
    if (filters.value.isResolved !== '') {
      params.is_resolved = filters.value.isResolved
    }
    if (filters.value.endpoint) {
      params.endpoint = filters.value.endpoint
    }
    if (filters.value.startDate) {
      params.start_date = filters.value.startDate
    }
    if (filters.value.endDate) {
      params.end_date = filters.value.endDate
    }
    
    const response = await adminAPI.errors.list(params)
    const data = response.data
    
    if (reset) {
      errors.value = data.results || []
    } else {
      errors.value = [...errors.value, ...(data.results || [])]
    }
    
    hasMore.value = !!data.next
    currentPage.value = page
    
    // Update unresolved count
    await updateUnresolvedCount()
  } catch (error) {
    console.error('Failed to load errors:', error)
  } finally {
    loading.value = false
  }
}

const loadMore = () => {
  if (hasMore.value && !loading.value) {
    loadErrors(currentPage.value + 1, false)
  }
}

const updateUnresolvedCount = async () => {
  try {
    const response = await adminAPI.errors.stats()
    unresolvedCount.value = response.data.stats.unresolved_count || 0
  } catch (error) {
    console.error('Failed to load error stats:', error)
  }
}

const resolveError = async (errorId) => {
  try {
    await adminAPI.errors.resolve(errorId)
    // Reload errors
    await loadErrors(1, true)
    selectedError.value = null
  } catch (error) {
    console.error('Failed to resolve error:', error)
    alert('Failed to resolve error. Please try again.')
  }
}

const selectError = async (error) => {
  try {
    const response = await adminAPI.errors.detail(error.id)
    selectedError.value = response.data
  } catch (error) {
    console.error('Failed to load error details:', error)
    selectedError.value = error
  }
}

const formatTimestamp = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleString()
}

const getLevelColor = (level) => {
  const colors = {
    CRITICAL: 'bg-red-600 text-white',
    ERROR: 'bg-red-500 text-white',
    WARNING: 'bg-yellow-500 text-white',
    INFO: 'bg-blue-500 text-white',
    DEBUG: 'bg-gray-500 text-white',
  }
  return colors[level] || 'bg-gray-500 text-white'
}

// Watch for filter changes
watch(filters, () => {
  loadErrors(1, true)
}, { deep: true })

// Watch for sidebar open/close
watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    loadErrors(1, true)
    // Start auto-refresh every 30 seconds
    refreshInterval.value = setInterval(() => {
      loadErrors(1, true)
    }, 30000)
  } else {
    // Stop auto-refresh
    if (refreshInterval.value) {
      clearInterval(refreshInterval.value)
      refreshInterval.value = null
    }
  }
})

onMounted(() => {
  if (props.isOpen) {
    loadErrors(1, true)
    refreshInterval.value = setInterval(() => {
      loadErrors(1, true)
    }, 30000)
  }
  // Initial unresolved count
  updateUnresolvedCount()
})

onUnmounted(() => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
  }
})
</script>

