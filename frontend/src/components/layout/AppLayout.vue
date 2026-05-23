<template>
  <div :class="['flex h-screen starry-background relative', { 'editor-layout': isEditorRoute }]">
    <!-- Animated Blob Background -->
    <div class="starry-blobs">
      <div class="starry-blob starry-blob-1"></div>
      <div class="starry-blob starry-blob-2"></div>
      <div class="starry-blob starry-blob-3"></div>
    </div>
    
    <Sidebar :is-open="sidebarOpen" @close="sidebarOpen = false" />
    <div class="flex-1 flex flex-col overflow-hidden lg:ml-0 relative z-10">
      <Navbar :title="title" @toggle-sidebar="sidebarOpen = !sidebarOpen" />
      <div
        v-if="showWsBanner"
        class="shrink-0 border-b border-amber-500/30 bg-amber-500/10 px-4 py-2.5 flex items-center gap-3 text-sm text-amber-200"
      >
        <svg class="w-5 h-5 shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M8.288 15.038a5.25 5.25 0 017.424 0M5.106 11.856c3.807-3.808 9.98-3.808 13.788 0M2.924 8.674c5.565-5.565 14.587-5.565 20.152 0M12 18.75h.008v.008H12v-.008z" />
        </svg>
        <span class="flex-1">{{ wsBannerMessage }}</span>
        <button
          type="button"
          class="shrink-0 rounded-lg border border-amber-500/40 px-3 py-1 text-xs font-medium text-amber-100 hover:bg-amber-500/20"
          @click="handleWsReconnect"
        >
          Reconnect
        </button>
      </div>
      <div
        v-if="authStore.isRestrictedMode"
        class="shrink-0 border-b border-rose-500/30 bg-rose-500/10 px-4 py-2.5 flex items-center gap-3 text-sm text-rose-300"
      >
        <svg class="w-5 h-5 shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
        </svg>
        <span class="flex-1">{{ restrictionBannerText }}</span>
      </div>
      <main :class="['flex-1 flex flex-col scroll-container', isEditorRoute ? 'overflow-hidden' : 'overflow-y-auto custom-scrollbar']">
        <div :class="[
          'flex-1 min-h-0 w-full main-content-wrapper',
          isEditorRoute ? 'p-0' : 'p-4 md:p-6 lg:p-8'
        ]">
          <slot />
        </div>
      </main>
      <Footer :class="{ 'hidden lg:block': isEditorRoute }" />
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
    default: 'PixelCast Signage',
  },
})

const route = useRoute()
const sidebarOpen = ref(false)

// Check if we're on the template editor route to prevent main scroll
const isEditorRoute = computed(() => {
  return route.name === 'template-editor' || route.name === 'template-editor-new' || (route.path.includes('/templates/') && route.path.includes('/edit'))
})
const authStore = useAuthStore()
const restrictionBannerText = computed(() => {
  const info = authStore.restrictionInfo
  if (!info) return 'Your access is currently restricted. Only limited pages are available.'
  const msg = info.reason || info.message || 'Your access is currently restricted.'
  const untilStr = info.until ? ` Until: ${new Date(info.until).toLocaleString()}` : ''
  return `${msg}${untilStr}`
})
const screensStore = useScreensStore()
const {
  connect,
  disconnect,
  reconnect,
  on,
  off,
  isConnected,
  reconnectExhausted,
  lastCloseReason,
} = useWebSocket()

const wsBannerMessage = ref('')

const showWsBanner = computed(
  () => authStore.isAuthenticated && Boolean(wsBannerMessage.value)
)

function handleWsReconnect() {
  wsBannerMessage.value = 'Reconnecting live updates…'
  reconnect()
}

function onReconnectExhausted(data) {
  wsBannerMessage.value =
    data?.message ||
    'Live updates could not be restored. Try Reconnect or refresh the page.'
}

const onScreenStatusUpdate = (data) => {
  if (data?.screen) {
    screensStore.handleScreenStatusUpdate(data.screen)
  }
}

const onScreenHeartbeat = (data) => {
  if (data?.screen_id) {
    screensStore.fetchSingleScreenStatus(data.screen_id).catch((err) => {
      if (import.meta.env.DEV) {
        console.warn('Failed to fetch screen status after heartbeat:', err)
      }
    })
  }
}

// Set up WebSocket listener for screen status updates
onMounted(() => {
  if (authStore.isAuthenticated && authStore.token) {
    connect(authStore.token)
    on('screen_status_update', onScreenStatusUpdate)
    on('screen_heartbeat', onScreenHeartbeat)
    on('reconnect_exhausted', onReconnectExhausted)
    on('connected', () => {
      wsBannerMessage.value = ''
    })
    on('disconnected', (data) => {
      if (data?.code !== 1000 && !reconnectExhausted.value) {
        wsBannerMessage.value =
          lastCloseReason.value || 'Live updates disconnected. Reconnecting…'
      }
    })
  }
})

onUnmounted(() => {
  off('screen_status_update', onScreenStatusUpdate)
  off('screen_heartbeat', onScreenHeartbeat)
  off('reconnect_exhausted', onReconnectExhausted)
  off('connected')
  off('disconnected')
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

/* Keep global navigation visible but compact in editor mode. */
.editor-layout :deep(.space-sidebar) {
  width: 5rem !important;
}

.editor-layout :deep(.logo-text),
.editor-layout :deep(.menu-text),
.editor-layout :deep(.error-dashboard-text),
.editor-layout :deep(.submenu-list),
.editor-layout :deep(.chevron-icon),
.editor-layout :deep(.menu-badge),
.editor-layout :deep(.submenu-badge) {
  display: none !important;
}

.editor-layout :deep(.menu-item) {
  justify-content: center;
  padding: 0.875rem 0.5rem;
}

.editor-layout :deep(.nav-content) {
  padding: 0 0.4rem;
}
</style>
