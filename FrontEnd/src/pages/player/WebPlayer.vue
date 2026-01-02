<template>
  <div 
    ref="playerContainer"
    class="web-player"
    :style="containerStyle"
  >
    <!-- On-screen message overlay (display_message command) -->
    <div
      v-if="overlayVisible"
      class="message-overlay"
    >
      <div class="message-box">
        <div class="message-text">{{ overlayMessage }}</div>
      </div>
    </div>

    <!-- Black screen when no template -->
    <div v-if="status === 'no_template'" class="no-template-screen">
      <!-- Empty black screen -->
    </div>

    <!-- Unpaired state -->
    <UnpairMessage v-if="status === 'unpaired'" />

    <!-- Error state -->
    <div v-else-if="status === 'error'" class="error-screen">
      <div class="error-message">
        <p>Connection Error</p>
        <p class="error-detail">{{ errorMessage }}</p>
        <p class="retry-info">Retrying in {{ retryCountdown }}s...</p>
      </div>
    </div>

    <!-- Loading state -->
    <div v-else-if="status === 'loading'" class="loading-screen">
      <!-- Black screen while loading -->
    </div>

    <!-- Template rendering -->
    <div 
      v-else-if="status === 'success' && template" 
      ref="templateContainer"
      class="template-container"
      :style="templateContainerStyle"
    >
      <!-- Debug overlay (remove in production) -->
      <div v-if="false" class="debug-overlay" style="position: absolute; top: 0; left: 0; z-index: 99999; background: rgba(255,0,0,0.1); pointer-events: none; padding: 10px; color: white; font-size: 12px;">
        <div>Template: {{ template?.name }}</div>
        <div>Dimensions: {{ template?.width }}x{{ template?.height }}</div>
        <div>Layers: {{ sortedLayers.length }}</div>
        <div>Scale: {{ scaleFactor.toFixed(3) }}</div>
      </div>
      
      <LayerRenderer
        v-for="layer in sortedLayers"
        :key="layer.id"
        :layer="layer"
        :template-width="template.width || 1920"
        :template-height="template.height || 1080"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { usePlayerStore } from '@/stores/player'
import { useResponsiveScaling } from '@/composables/useResponsiveScaling'
import LayerRenderer from '@/components/player/LayerRenderer.vue'
import UnpairMessage from '@/components/player/UnpairMessage.vue'

const router = useRouter()
const playerStore = usePlayerStore()
const playerContainer = ref(null)
const templateContainer = ref(null)

// Reactive state from store
const status = computed(() => playerStore.status)
const template = computed(() => playerStore.template)
const errorMessage = computed(() => playerStore.errorMessage)
const retryCountdown = computed(() => playerStore.retryCountdown)
const overlayVisible = computed(() => playerStore.overlayVisible)
const overlayMessage = computed(() => playerStore.overlayMessage)

// Watch for unpair status and redirect to pairing page
// BUT: Don't redirect if screen_id exists (might be temporary error)
watch(status, (newStatus) => {
  // Check if screen_id exists before redirecting
  const storedScreenId = localStorage.getItem('player_screen_id')
  const isPaired = localStorage.getItem('player_is_paired') === 'true'
  const hasScreenId = storedScreenId && isPaired
  
  if (newStatus === 'unpaired') {
    // Only redirect if we don't have a valid screen_id
    if (!hasScreenId) {
      console.log('[WebPlayer] Status changed to unpaired, redirecting to pairing page')
      // Redirect to pairing page immediately (don't wait)
      router.push('/player/connect')
    } else {
      console.log('[WebPlayer] Status is unpaired but screen_id exists, not redirecting', {
        screenId: storedScreenId
      })
    }
  }
  
  // Also redirect on error if it's a credentials error
  if (newStatus === 'error') {
    const errorMsg = errorMessage.value || ''
    if ((errorMsg.includes('credentials') || 
         errorMsg.includes('pair') || 
         errorMsg.includes('auth_token and secret_key')) && !hasScreenId) {
      console.log('[WebPlayer] Credentials error detected, redirecting to pairing page')
      router.push('/player/connect')
    }
  }
}, { immediate: true })

// Sort layers by z_index to ensure correct rendering order
// Filter only active layers (safety check - backend should already filter)
const sortedLayers = computed(() => {
  if (!template.value || !template.value.layers) {
    console.warn('[WebPlayer] No template or layers found', { template: template.value })
    return []
  }
  
  // Filter active layers and sort by z_index
  const layers = [...template.value.layers]
    .filter(layer => layer.is_active !== false) // Only render active layers
    .sort((a, b) => {
      const zA = a.z_index || 0
      const zB = b.z_index || 0
      if (zA !== zB) return zA - zB
      // If z_index is same, sort by name for consistency
      return (a.name || '').localeCompare(b.name || '')
    })
  
  console.log(`[WebPlayer] Rendered ${layers.length} layers`, {
    totalLayers: template.value.layers.length,
    activeLayers: layers.length,
    layers: layers.map(l => ({ id: l.id, name: l.name, widgets: l.widgets?.length || 0 }))
  })
  
  return layers
})

// Use responsive scaling composable
const {
  scaleFactor,
  scaledWidth,
  scaledHeight,
  offsetX,
  offsetY,
  setupResizeListener,
  cleanupResizeListener
} = useResponsiveScaling(template)

// Container style - full viewport with black background
// CRITICAL FIX: No overflow clipping needed since container is exactly viewport size (no scaling)
const containerStyle = computed(() => ({
  position: 'fixed',
  top: 0,
  left: 0,
  width: '100vw',
  height: '100vh',
  // No overflow clipping - container is exactly viewport size, template-container fills it naturally
  overflow: 'visible',
  backgroundColor: '#000000'
  // Template container is relative positioned and fills 100vw x 100vh
}))

// Template container style - CRITICAL FIX: container must be 100vw x 100vh with no scale
// This ensures container fills entire viewport and content is not "shrunk" in the center
// Layers/Widgets inside will use their dimensions as percentages or pixel values relative to this container
const templateContainerStyle = computed(() => {
  // CRITICAL: Container must be exactly 100% viewport (100vw x 100vh)
  // No scaling - container fills entire screen naturally
  // This allows layers/widgets to fill the container properly without being "shrunk"
  return {
    width: '100vw',
    height: '100vh',
    position: 'relative',
    // No transform/scale needed - container is already full viewport
    // Ensure container is visible
    visibility: 'visible',
    opacity: 1,
    // Allow overflow for content that extends beyond (layers/widgets handle their own overflow)
    overflow: 'visible'
  }
})

// CRITICAL FIX: Removed scale transform watch
// Container is now 100vw x 100vh with no scaling
// All dimensions are handled via percentages in layers/widgets
// No transform/scale needed anymore

// Event handlers
let contextMenuHandler = null
let keydownHandler = null
let debugKeyHandler = null

// Full-screen management
const toggleFullscreen = async () => {
  const element = playerContainer.value
  if (!element) {
    console.warn('[WebPlayer] Cannot toggle fullscreen: playerContainer ref not available')
    return
  }

  try {
    if (!document.fullscreenElement && !document.webkitFullscreenElement && !document.mozFullScreenElement && !document.msFullscreenElement) {
      // Enter fullscreen
      if (element.requestFullscreen) {
        await element.requestFullscreen()
      } else if (element.webkitRequestFullscreen) {
        await element.webkitRequestFullscreen()
      } else if (element.mozRequestFullScreen) {
        await element.mozRequestFullScreen()
      } else if (element.msRequestFullscreen) {
        await element.msRequestFullscreen()
      }
      console.log('[WebPlayer] Entered fullscreen mode')
    } else {
      // Exit fullscreen
      if (document.exitFullscreen) {
        await document.exitFullscreen()
      } else if (document.webkitExitFullscreen) {
        await document.webkitExitFullscreen()
      } else if (document.mozCancelFullScreen) {
        await document.mozCancelFullScreen()
      } else if (document.msExitFullscreen) {
        await document.msExitFullscreen()
      }
      console.log('[WebPlayer] Exited fullscreen mode')
    }
  } catch (error) {
    console.error('[WebPlayer] Fullscreen toggle failed:', error)
  }
}

// Debug helper: Log PlayerStore and activeLayers state
const logDebugState = () => {
  console.group('🔍 WebPlayer Debug State')
  
  // Log PlayerStore state
  console.log('📦 PlayerStore State:', {
    status: playerStore.status,
    template: playerStore.template ? {
      id: playerStore.template.id,
      name: playerStore.template.name,
      width: playerStore.template.width,
      height: playerStore.template.height,
      layersCount: playerStore.template.layers?.length || 0
    } : null,
    errorMessage: playerStore.errorMessage,
    retryCountdown: playerStore.retryCountdown,
    overlayVisible: playerStore.overlayVisible,
    overlayMessage: playerStore.overlayMessage
  })
  
  // Log active layers (sortedLayers)
  console.log('📋 Active Layers:', sortedLayers.value.map(layer => ({
    id: layer.id,
    name: layer.name,
    z_index: layer.z_index,
    is_active: layer.is_active,
    widgetsCount: layer.widgets?.length || 0,
    widgets: layer.widgets?.map(w => ({
      id: w.id,
      name: w.name,
      type: w.type,
      is_active: w.is_active,
      contentsCount: w.contents?.length || 0
    })) || []
  })))
  
  // Log full PlayerStore object (for deep inspection)
  console.log('📦 Full PlayerStore Object:', playerStore)
  
  console.groupEnd()
}

  // Initialize player on mount
  onMounted(async () => {
    console.log('[WebPlayer] Component mounted')
    
    // Disable scroll on html and body only for player page
    document.documentElement.style.overflow = 'hidden'
    document.body.style.overflow = 'hidden'
    
    // Prevent context menu
    contextMenuHandler = (e) => e.preventDefault()
    document.addEventListener('contextmenu', contextMenuHandler)
    
    // Prevent keyboard shortcuts that might interfere (allow F12, F key, and Ctrl+Shift+L for debugging)
    keydownHandler = (e) => {
      // Allow F12 for browser inspector
      if (e.key === 'F12') {
        return // Don't prevent default
      }
      
      // Allow F key for fullscreen toggle
      if (e.key === 'f' || e.key === 'F') {
        toggleFullscreen()
        e.preventDefault()
        return
      }
      
      // Allow Ctrl+Shift+L for debug logging (handled by debugKeyHandler)
      if (e.ctrlKey && e.shiftKey && (e.key === 'L' || e.key === 'l')) {
        return // Don't prevent default, let debugKeyHandler handle it
      }
      
      // Allow Ctrl/Cmd combinations (for browser shortcuts)
      if (e.ctrlKey || e.metaKey) {
        return // Don't prevent default
      }
      
      // Prevent all other keys
      e.preventDefault()
    }
    document.addEventListener('keydown', keydownHandler, true)
    
    // Separate handler for debug logging (Ctrl+Shift+L) - must be after keydownHandler
    debugKeyHandler = (e) => {
      if (e.ctrlKey && e.shiftKey && (e.key === 'L' || e.key === 'l')) {
        logDebugState()
        e.preventDefault()
      }
    }
    document.addEventListener('keydown', debugKeyHandler, true)

    // Prevent text selection
    document.addEventListener('selectstart', (e) => e.preventDefault())
    document.addEventListener('dragstart', (e) => e.preventDefault())

    // CRITICAL FIX: Removed scale transform application
    // Container is 100vw x 100vh with no scaling
    // No transform needed - container naturally fills viewport

    // Initialize player store
    try {
      await playerStore.initialize()
      console.log('[WebPlayer] Store initialized, status:', playerStore.status)
      
      // Check if initialization was successful (credentials loaded)
      if (playerStore.status === 'error') {
        const errorMsg = playerStore.errorMessage || ''
        console.error('[WebPlayer] Initialization failed with status error:', errorMsg)
        
        // If credentials are missing, redirect to pairing page immediately
        // BUT: Don't redirect if screen_id exists
        const storedScreenId = localStorage.getItem('player_screen_id')
        const isPaired = localStorage.getItem('player_is_paired') === 'true'
        const hasScreenId = storedScreenId && isPaired
        
        if ((errorMsg.includes('auth_token and secret_key are required') || 
             errorMsg.includes('credentials') ||
             errorMsg.includes('pair')) && !hasScreenId) {
          console.log('[WebPlayer] Credentials missing, redirecting to pairing page')
          playerStore.clearCredentials()
          router.push('/player/connect')
          return // Don't start polling
        }
      }
      
      // Only start polling if we have valid authentication (screen_id OR credentials)
      // Check if authentication is configured in localStorage
      const storedScreenId = localStorage.getItem('player_screen_id')
      const isPaired = localStorage.getItem('player_is_paired') === 'true'
      const storedToken = localStorage.getItem('player_auth_token')
      const storedSecret = localStorage.getItem('player_secret_key')
      
      const hasScreenId = storedScreenId && isPaired
      const hasCredentials = storedToken && storedSecret
      
      if (!hasScreenId && !hasCredentials) {
        console.warn('[WebPlayer] No authentication found, redirecting to pairing page')
        playerStore.clearCredentials()
        router.push('/player/connect')
        return // Don't start polling
      }
      
      console.log('[WebPlayer] Authentication verified, starting polling', {
        method: hasScreenId ? 'screen_id' : 'credentials'
      })
      
      // Log template data when received
      watch(() => playerStore.template, (newTemplate) => {
        if (newTemplate) {
          console.log('[WebPlayer] Template received:', {
            id: newTemplate.id,
            name: newTemplate.name,
            width: newTemplate.width,
            height: newTemplate.height,
            layersCount: newTemplate.layers?.length || 0,
            layers: newTemplate.layers?.map(l => ({
              id: l.id,
              name: l.name,
              is_active: l.is_active,
              widgetsCount: l.widgets?.length || 0,
              widgets: l.widgets?.map(w => ({
                id: w.id,
                name: w.name,
                type: w.type,
                is_active: w.is_active,
                contentsCount: w.contents?.length || 0
              }))
            }))
          })
        }
      }, { immediate: true })
      
      // Start polling only if we have credentials
      playerStore.startPolling()
      
      // Optionally enter fullscreen on successful initialization
      // Uncomment the next line to auto-enter fullscreen when player initializes
      // await nextTick(() => toggleFullscreen())
    } catch (error) {
      // If credentials are missing or invalid, redirect to pairing page
      console.error('[WebPlayer] Player initialization failed:', error)
      const errorMsg = error.message || ''
      
      if (errorMsg.includes('auth_token and secret_key are required') ||
          errorMsg.includes('Invalid credentials') ||
          errorMsg.includes('credentials')) {
        // Clear any invalid credentials
        playerStore.clearCredentials()
        // Redirect to pairing page immediately
        console.log('[WebPlayer] Redirecting to pairing page due to missing credentials')
        router.push('/player/connect')
        return // Don't start polling
      }
      
      // For other errors, set error status but don't redirect
      playerStore.status = 'error'
      playerStore.errorMessage = error.message || 'Initialization failed'
    }
  })

// Cleanup on unmount
onUnmounted(() => {
  // Re-enable scroll when leaving player page
  document.documentElement.style.overflow = ''
  document.body.style.overflow = ''
  
  if (contextMenuHandler) {
    document.removeEventListener('contextmenu', contextMenuHandler)
  }
  if (keydownHandler) {
    document.removeEventListener('keydown', keydownHandler, true)
  }
  if (debugKeyHandler) {
    document.removeEventListener('keydown', debugKeyHandler, true)
  }
  cleanupResizeListener()
  playerStore.stopPolling()
})
</script>

<style scoped>
.web-player {
  margin: 0;
  padding: 0;
  position: fixed;
  top: 0;
  left: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
}

.no-template-screen,
.loading-screen {
  width: 100%;
  height: 100%;
  background-color: #000000;
}

.message-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.35);
  z-index: 99999;
  /* CRITICAL: pointer-events: none ensures overlay doesn't block mouse interactions
     This allows right-click "Inspect Element" to work properly */
  pointer-events: none;
}

.message-box {
  max-width: 70vw;
  padding: 18px 22px;
  background: rgba(0, 0, 0, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
  /* Ensure message box itself doesn't block pointer events (child of pointer-events: none parent) */
  pointer-events: auto;
}

.message-text {
  font-size: 20px;
  color: #ffffff;
  text-align: center;
  line-height: 1.5;
  word-break: break-word;
}

.error-screen {
  width: 100%;
  height: 100%;
  background-color: #000000;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  font-family: 'Inter', sans-serif;
}

.error-message {
  text-align: center;
  /* Responsive font sizing - scales with viewport */
  font-size: clamp(14px, 2vw, 24px);
}

.error-message p {
  margin: 10px 0;
}

.error-detail {
  font-size: clamp(12px, 1.5vw, 16px);
  color: #888888;
}

.retry-info {
  font-size: clamp(10px, 1.2vw, 14px);
  color: #666666;
}

.template-container {
  /* CRITICAL FIX: Position relative (not absolute)
     Container is 100vw x 100vh, fills parent naturally
     No scaling, no transform - container fills entire viewport */
  position: relative;
  overflow: visible;
  /* Ensure proper rendering with hardware acceleration */
  transform: translateZ(0);
  -webkit-transform: translateZ(0);
  /* Prevent layout shifts but allow content overflow for images */
  contain: layout style;
}
</style>

