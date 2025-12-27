<template>
  <div 
    ref="playerContainer"
    class="web-player"
    :style="containerStyle"
  >
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

// Watch for unpair status and redirect to pairing page
watch(status, (newStatus) => {
  if (newStatus === 'unpaired') {
    console.log('[WebPlayer] Status changed to unpaired, redirecting to pairing page')
    // Redirect to pairing page immediately (don't wait)
    router.push('/player/connect')
  }
  
  // Also redirect on error if it's a credentials error
  if (newStatus === 'error') {
    const errorMsg = errorMessage.value || ''
    if (errorMsg.includes('credentials') || 
        errorMsg.includes('pair') || 
        errorMsg.includes('auth_token and secret_key')) {
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
const containerStyle = computed(() => ({
  position: 'fixed',
  top: 0,
  left: 0,
  width: '100vw',
  height: '100vh',
  overflow: 'hidden',
  backgroundColor: '#000000',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center'
}))

// Template container style - actual template dimensions with scaling transform
const templateContainerStyle = computed(() => {
  if (!template.value) {
    return {
      width: '100%',
      height: '100%',
      position: 'relative'
    }
  }

  const templateWidth = template.value.width || 1920
  const templateHeight = template.value.height || 1080
  const scale = scaleFactor.value

  // Safety check: ensure dimensions are valid
  if (templateWidth <= 0 || templateHeight <= 0) {
    console.error('[WebPlayer] Invalid template dimensions:', { templateWidth, templateHeight })
    return {
      width: '1920px',
      height: '1080px',
      position: 'relative',
      transform: `scale(${scale})`,
      transformOrigin: 'center center',
      willChange: 'transform',
      backfaceVisibility: 'hidden',
      WebkitTransform: `scale(${scale})`,
      WebkitTransformOrigin: 'center center',
      margin: '0 auto',
      visibility: 'visible',
      opacity: 1
    }
  }

  // Safety check: ensure scale is valid
  if (scale <= 0 || !isFinite(scale)) {
    console.error('[WebPlayer] Invalid scale factor:', scale)
    return {
      width: `${templateWidth}px`,
      height: `${templateHeight}px`,
      position: 'relative',
      transform: 'scale(1)',
      transformOrigin: 'center center',
      willChange: 'transform',
      backfaceVisibility: 'hidden',
      WebkitTransform: 'scale(1)',
      WebkitTransformOrigin: 'center center',
      margin: '0 auto',
      visibility: 'visible',
      opacity: 1
    }
  }

  return {
    width: `${templateWidth}px`,
    height: `${templateHeight}px`,
    position: 'relative',
    transform: `scale(${scale})`,
    transformOrigin: 'center center',
    willChange: 'transform',
    backfaceVisibility: 'hidden',
    // Use hardware acceleration
    WebkitTransform: `scale(${scale})`,
    WebkitTransformOrigin: 'center center',
    // Center the template
    margin: '0 auto',
    // Ensure container is visible
    visibility: 'visible',
    opacity: 1,
    // Ensure container is not clipped
    overflow: 'visible'
  }
})

// Update transform when template or scale changes
// This ensures all nested elements (layers → widgets → content) scale proportionally
watch([template, scaleFactor], () => {
  nextTick(() => {
    if (templateContainer.value && template.value) {
      const scale = scaleFactor.value
      // Apply scale transform - all child elements scale proportionally
      templateContainer.value.style.transform = `scale(${scale})`
      templateContainer.value.style.WebkitTransform = `scale(${scale})`
      // Force hardware acceleration
      templateContainer.value.style.willChange = 'transform'
    }
  })
}, { immediate: true })

// Event handlers
let contextMenuHandler = null
let keydownHandler = null

  // Initialize player on mount
  onMounted(async () => {
    console.log('[WebPlayer] Component mounted')
    
    // Disable scroll on html and body only for player page
    document.documentElement.style.overflow = 'hidden'
    document.body.style.overflow = 'hidden'
    
    // Prevent context menu
    contextMenuHandler = (e) => e.preventDefault()
    document.addEventListener('contextmenu', contextMenuHandler)
    
    // Prevent keyboard shortcuts that might interfere (allow F12 for debugging)
    keydownHandler = (e) => {
      if (e.key !== 'F12' && !e.ctrlKey && !e.metaKey) {
        e.preventDefault()
      }
    }
    document.addEventListener('keydown', keydownHandler, true)

    // Prevent text selection
    document.addEventListener('selectstart', (e) => e.preventDefault())
    document.addEventListener('dragstart', (e) => e.preventDefault())

    // Setup responsive scaling resize listener
    setupResizeListener()

    // Initial transform application
    await nextTick()
    if (templateContainer.value && template.value) {
      const scale = scaleFactor.value
      templateContainer.value.style.transform = `scale(${scale})`
      templateContainer.value.style.WebkitTransform = `scale(${scale})`
      console.log('[WebPlayer] Applied initial transform', { scale })
    }

    // Initialize player store
    try {
      await playerStore.initialize()
      console.log('[WebPlayer] Store initialized, status:', playerStore.status)
      
      // Check if initialization was successful (credentials loaded)
      if (playerStore.status === 'error') {
        const errorMsg = playerStore.errorMessage || ''
        console.error('[WebPlayer] Initialization failed with status error:', errorMsg)
        
        // If credentials are missing, redirect to pairing page immediately
        if (errorMsg.includes('auth_token and secret_key are required') || 
            errorMsg.includes('credentials') ||
            errorMsg.includes('pair')) {
          console.log('[WebPlayer] Credentials missing, redirecting to pairing page')
          playerStore.clearCredentials()
          router.push('/player/connect')
          return // Don't start polling
        }
      }
      
      // Only start polling if we have valid credentials
      // Check if credentials are actually set in playerAPI
      const storedToken = localStorage.getItem('player_auth_token')
      const storedSecret = localStorage.getItem('player_secret_key')
      
      if (!storedToken || !storedSecret) {
        console.warn('[WebPlayer] No credentials found, redirecting to pairing page')
        playerStore.clearCredentials()
        router.push('/player/connect')
        return // Don't start polling
      }
      
      console.log('[WebPlayer] Credentials verified, starting polling')
      
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
  position: relative;
  overflow: hidden;
  /* Ensure proper rendering with hardware acceleration */
  transform: translateZ(0);
  -webkit-transform: translateZ(0);
  /* Prevent any layout shifts */
  contain: layout style paint;
}
</style>

