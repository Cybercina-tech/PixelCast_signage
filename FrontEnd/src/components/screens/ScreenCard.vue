<template>
  <div
    class="group relative bg-gray-800 border border-gray-700 rounded-xl overflow-hidden hover:ring-2 hover:ring-blue-500 transition-all"
  >
    <!-- Status Indicator -->
    <div class="absolute top-4 right-4 z-10">
      <StatusIndicator :status="status" />
    </div>

    <!-- Monitor Preview -->
    <div class="relative bg-gray-900 border-b border-gray-700 p-4">
      <div class="aspect-video bg-black rounded-lg overflow-hidden relative">
        <!-- Monitor Frame Effect -->
        <div class="absolute inset-0 border-2 border-gray-700 rounded-lg pointer-events-none"></div>
        
        <!-- Template Preview -->
        <div v-if="screen.active_template" class="w-full h-full flex items-center justify-center bg-gradient-to-br from-indigo-500/20 to-blue-500/20">
          <div class="text-center p-4">
            <DocumentTextIcon class="w-12 h-12 text-indigo-400 mx-auto mb-2" />
            <p class="text-xs text-gray-300 font-medium truncate max-w-[200px]">
              {{ screen.active_template.name }}
            </p>
          </div>
        </div>
        
        <!-- No Template State -->
        <div v-else class="w-full h-full flex items-center justify-center bg-gray-800">
          <div class="text-center">
            <TvIcon class="w-8 h-8 text-gray-600 mx-auto mb-2" />
            <p class="text-xs text-gray-500">No Template</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Card Content -->
    <div class="p-4 space-y-3">
      <!-- Header -->
      <div>
        <h3 class="text-lg font-semibold text-white mb-1 truncate">
          {{ screen.name || 'Unnamed Screen' }}
        </h3>
        <div class="flex items-center gap-2 text-sm text-gray-400">
          <span class="font-mono">{{ screen.pairing_code || 'N/A' }}</span>
        </div>
      </div>

      <!-- Metadata -->
      <div class="space-y-2 text-sm">
        <div class="flex items-center justify-between">
          <span class="text-gray-400">Last Seen</span>
          <span class="text-gray-300">{{ formatLastSeen(screen.last_heartbeat_at) }}</span>
        </div>
        <div class="flex items-center justify-between">
          <span class="text-gray-400">IP Address</span>
          <span class="text-gray-300 font-mono text-xs">{{ screen.current_ip || 'N/A' }}</span>
        </div>
        <div class="flex items-center justify-between">
          <span class="text-gray-400">Player Version</span>
          <span class="text-gray-300 text-xs">{{ screen.player_version || 'Unknown' }}</span>
        </div>
      </div>
    </div>

    <!-- Hover Overlay with Actions -->
    <div class="absolute inset-0 bg-black/80 backdrop-blur-sm opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-3 z-20">
      <button
        @click="$emit('refresh', screen)"
        class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-all flex items-center gap-2"
        title="Refresh Screen"
      >
        <ArrowPathIcon class="w-4 h-4" />
        Refresh
      </button>
      <button
        @click="$emit('identify', screen)"
        class="px-4 py-2 bg-yellow-600 hover:bg-yellow-700 text-white rounded-lg font-medium transition-all flex items-center gap-2"
        title="Identify Screen"
      >
        <FingerPrintIcon class="w-4 h-4" />
        Identify
      </button>
      <button
        @click="$emit('edit', screen)"
        class="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium transition-all flex items-center gap-2"
        title="Edit Screen"
      >
        <PencilIcon class="w-4 h-4" />
        Edit
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useScreensStore } from '@/stores/screens'
import {
  TvIcon,
  DocumentTextIcon,
  ArrowPathIcon,
  FingerPrintIcon,
  PencilIcon,
} from '@heroicons/vue/24/outline'
import StatusIndicator from './StatusIndicator.vue'

const props = defineProps({
  screen: {
    type: Object,
    required: true,
  },
})

defineEmits(['refresh', 'identify', 'edit'])

const screensStore = useScreensStore()

const status = computed(() => {
  return screensStore.getScreenStatus(props.screen)
})

const formatLastSeen = (timestamp) => {
  if (!timestamp) return 'Never'
  const now = new Date()
  const lastSeen = new Date(timestamp)
  const diffMs = now - lastSeen
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMins / 60)
  const diffDays = Math.floor(diffHours / 24)
  
  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`
  return lastSeen.toLocaleDateString()
}
</script>

