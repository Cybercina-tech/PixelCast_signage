<template>
  <footer class="bg-secondary border-t border-border-color px-6 py-3 mt-auto">
    <div class="flex flex-col sm:flex-row items-center justify-between gap-2 text-xs">
      <!-- Left: System Info -->
      <div class="flex flex-wrap items-center gap-3 text-slate-900 dark:text-slate-50">
        <span class="font-medium text-slate-900 dark:text-slate-50">ScreenGram</span>
        <span class="text-slate-600 dark:text-slate-400">·</span>
        <span class="font-mono text-xs text-slate-900 dark:text-slate-50">v{{ appVersion }}</span>
        
        <!-- Environment Badge (optional) -->
          <span v-if="environment && environment !== 'production'" class="text-slate-600 dark:text-slate-400">·</span>
        <span 
          v-if="environment && environment !== 'production'" 
          :class="[
            'px-2 py-0.5 rounded text-xs font-medium',
            environment === 'staging' ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-200' : 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-200'
          ]"
        >
          {{ environment }}
        </span>
        
        <!-- API Status -->
        <span class="text-slate-600 dark:text-slate-400">·</span>
        <div class="flex items-center gap-1.5">
          <span 
            :class="[
              'w-1.5 h-1.5 rounded-full',
              apiStatus === 'connected' ? 'bg-green-500' : 'bg-red-500'
            ]"
          ></span>
          <span class="text-slate-900 dark:text-slate-50">API {{ apiStatus === 'connected' ? 'Connected' : 'Disconnected' }}</span>
        </div>
        
        <!-- WebSocket Status -->
        <span v-if="wsStatus" class="text-slate-600 dark:text-slate-400">·</span>
        <div v-if="wsStatus" class="flex items-center gap-1.5">
          <span 
            :class="[
              'w-1.5 h-1.5 rounded-full',
              wsStatus === 'online' ? 'bg-green-500' : 'bg-red-500'
            ]"
          ></span>
          <span class="text-slate-900 dark:text-slate-50">WebSocket {{ wsStatus === 'online' ? 'Online' : 'Offline' }}</span>
        </div>
      </div>
      
      <!-- Right: Legal Links -->
      <div class="flex items-center gap-4 text-slate-900 dark:text-slate-50">
        <router-link 
          to="/privacy"
          class="text-slate-900 dark:text-slate-50 hover:text-slate-700 dark:hover:text-slate-300 transition-colors"
        >
          Privacy
        </router-link>
        <router-link 
          to="/terms"
          class="text-slate-900 dark:text-slate-50 hover:text-slate-700 dark:hover:text-slate-300 transition-colors"
        >
          Terms
        </router-link>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

// App version from Git (set at build time)
// Format: commit hash (e.g., "e994370")
const appVersion = ref(typeof __APP_VERSION__ !== 'undefined' ? __APP_VERSION__ : 'dev')

// Environment - can be from env variable
const environment = ref(null) // 'production', 'staging', 'development', or null

// API Status
const apiStatus = ref('connected')

// WebSocket Status
const wsStatus = ref(null) // 'online', 'offline', or null

let wsCheckInterval = null
let apiCheckInterval = null

// Check API status
const checkApiStatus = async () => {
  try {
    // Simple health check - you can use your actual API endpoint
    const response = await fetch('/api/health', { 
      method: 'GET',
      signal: AbortSignal.timeout(3000) // 3 second timeout
    })
    apiStatus.value = response.ok ? 'connected' : 'disconnected'
  } catch (error) {
    apiStatus.value = 'disconnected'
  }
}

// Check WebSocket status (if WebSocket is used)
const checkWebSocketStatus = () => {
  // Check if WebSocket connection exists
  // This is a placeholder - adjust based on your WebSocket implementation
  if (window.WebSocket && authStore.isAuthenticated) {
    // You can check your actual WebSocket connection here
    // For now, we'll assume it's online if user is authenticated
    wsStatus.value = 'online'
  } else {
    wsStatus.value = 'offline'
  }
}


onMounted(() => {
  // Initial checks
  checkApiStatus()
  checkWebSocketStatus()
  
  // Check API status every 30 seconds
  apiCheckInterval = setInterval(checkApiStatus, 30000)
  
  // Check WebSocket status every 10 seconds
  wsCheckInterval = setInterval(checkWebSocketStatus, 10000)
  
  // Set environment from env or config
  // environment.value = import.meta.env.VITE_APP_ENV || null
})

onUnmounted(() => {
  if (apiCheckInterval) {
    clearInterval(apiCheckInterval)
  }
  if (wsCheckInterval) {
    clearInterval(wsCheckInterval)
  }
})
</script>

<style scoped>
/* Minimal styling - footer should be subtle */
footer {
  min-height: 40px;
  max-height: 56px;
}

/* Hide on mobile if needed */
@media (max-width: 640px) {
  footer {
    /* Optional: can be hidden on mobile */
    /* display: none; */
  }
}
</style>
