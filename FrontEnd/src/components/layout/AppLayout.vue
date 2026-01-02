<template>
  <div class="flex h-screen starry-background relative">
    <!-- Animated Blob Background -->
    <div class="starry-blobs">
      <div class="starry-blob starry-blob-1"></div>
      <div class="starry-blob starry-blob-2"></div>
      <div class="starry-blob starry-blob-3"></div>
    </div>
    
    <Sidebar :is-open="sidebarOpen" @close="sidebarOpen = false" />
    <div class="flex-1 flex flex-col overflow-hidden lg:ml-0 relative z-10">
      <Navbar :title="title" @toggle-sidebar="sidebarOpen = !sidebarOpen" />
      <main :class="['flex-1 flex flex-col scroll-container', isEditorRoute ? 'overflow-hidden' : 'overflow-y-auto custom-scrollbar']">
        <div :class="[
          'flex-1 w-full main-content-wrapper',
          isEditorRoute ? 'p-0' : 'p-4 md:p-6 lg:p-8'
        ]">
          <slot />
        </div>
      </main>
      <Footer />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useScreensStore } from '@/stores/screens'
import { useWebSocket } from '@/composables/useWebSocket'
import Sidebar from './Sidebar.vue'
import Navbar from './Navbar.vue'
import Footer from './Footer.vue'

defineProps({
  title: {
    type: String,
    default: 'ScreenGram',
  },
})

const route = useRoute()
const sidebarOpen = ref(false)

// Check if we're on the template editor route to prevent main scroll
const isEditorRoute = computed(() => {
  return route.name === 'template-editor' || route.name === 'template-editor-new' || (route.path.includes('/templates/') && route.path.includes('/edit'))
})
const authStore = useAuthStore()
const screensStore = useScreensStore()
const { connect, disconnect, on, off, isConnected } = useWebSocket()

// Set up WebSocket listener for screen status updates
onMounted(() => {
  if (authStore.isAuthenticated && authStore.accessToken) {
    // Connect WebSocket
    connect(authStore.accessToken)
    
    // Listen for screen status updates
    on('screen_status_update', (data) => {
      if (data && data.screen) {
        screensStore.handleScreenStatusUpdate(data.screen)
      }
    })
    
    // Listen for screen heartbeat updates
    on('screen_heartbeat', (data) => {
      if (data && data.screen_id) {
        // Fetch updated status for this screen
        screensStore.fetchSingleScreenStatus(data.screen_id).catch(err => {
          console.warn('Failed to fetch screen status after heartbeat:', err)
        })
      }
    })
  }
})

onUnmounted(() => {
  // Clean up WebSocket listeners
  off('screen_status_update')
  off('screen_heartbeat')
  disconnect()
})
</script>

<style scoped>
/* Ensure content has space above footer when scrolling */
.main-content-wrapper:not(.p-0) {
  padding-bottom: calc(1.5rem + 30px);
}

.main-content-wrapper.p-0 {
  padding-bottom: 30px;
}
</style>
