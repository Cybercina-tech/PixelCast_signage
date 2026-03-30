<template>
  <div
    ref="playerContainer"
    class="web-player"
    :style="containerStyle"
  >
    <!-- Pairing flow (embedded — no redirect needed) -->
    <PairingFlow
      v-if="showPairing"
      @paired="handlePaired"
    />

    <!-- On-screen message overlay (display_message command) -->
    <div v-if="overlayVisible" class="message-overlay">
      <div class="message-box">
        <div class="message-text">{{ overlayMessage }}</div>
      </div>
    </div>

    <!-- Black screen when no template -->
    <div v-if="!showPairing && status === 'no_template'" class="no-template-screen" />

    <!-- Unpaired / revoked state -->
    <UnpairMessage v-if="!showPairing && status === 'unpaired'" @return-to-pairing="enterPairing" />

    <!-- Error state -->
    <div v-else-if="!showPairing && status === 'error'" class="error-screen">
      <div class="error-message">
        <p>Connection Error</p>
        <p class="error-detail">{{ errorMessage }}</p>
        <p class="retry-info">Retrying in {{ retryCountdown }}s...</p>
      </div>
    </div>

    <!-- Loading state -->
    <div v-else-if="!showPairing && status === 'loading'" class="loading-screen" />

    <!-- Template rendering -->
    <div
      v-else-if="!showPairing && status === 'success' && template"
      ref="templateContainer"
      class="template-container"
      :style="templateContainerStyle"
    >
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
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { usePlayerStore } from '@/stores/player'
import { useResponsiveScaling } from '@/composables/useResponsiveScaling'
import LayerRenderer from '@/components/player/LayerRenderer.vue'
import UnpairMessage from '@/components/player/UnpairMessage.vue'
import PairingFlow from '@/components/player/PairingFlow.vue'

const playerStore = usePlayerStore()
const route = useRoute()
const playerContainer = ref(null)
const templateContainer = ref(null)

const showPairing = ref(false)
const routeScreenId = computed(() => {
  const raw = route.params.screenId
  return raw ? String(raw).trim() : null
})
const forcePairing = computed(() => route.query.pair === '1')

const status = computed(() => playerStore.status)
const template = computed(() => playerStore.template)
const errorMessage = computed(() => playerStore.errorMessage)
const retryCountdown = computed(() => playerStore.retryCountdown)
const overlayVisible = computed(() => playerStore.overlayVisible)
const overlayMessage = computed(() => playerStore.overlayMessage)

// When status becomes 'unpaired' and we have no device identity, show pairing
watch(status, (s) => {
  if (s === 'unpaired' && !playerStore.hasDeviceIdentity(routeScreenId.value)) {
    showPairing.value = true
  }
})

watch(routeScreenId, async (newScreenId, oldScreenId) => {
  if (newScreenId === oldScreenId) return
  playerStore.stopPolling()
  playerStore.setActiveScreen(newScreenId)

  if (!playerStore.hasDeviceIdentity(newScreenId)) {
    showPairing.value = true
    return
  }

  showPairing.value = false
  try {
    await playerStore.initialize(newScreenId)
    if (playerStore.status !== 'unpaired') {
      playerStore.startPolling()
    }
  } catch (_) {
    showPairing.value = true
  }
})

watch(forcePairing, async (isForced) => {
  if (!isForced) return
  playerStore.stopPolling()
  playerStore.setActiveScreen(routeScreenId.value)
  showPairing.value = true
})

function enterPairing() {
  playerStore.clearDeviceIdentity(routeScreenId.value)
  playerStore.stopPolling()
  showPairing.value = true
}

function handlePaired({ screenId, deviceToken }) {
  const expectedScreenId = routeScreenId.value
  if (expectedScreenId && screenId && expectedScreenId !== String(screenId)) {
    playerStore.status = 'unpaired'
    playerStore.errorMessage = 'Paired to a different screen. Please pair this TV with the screen from the current URL.'
    showPairing.value = true
    return
  }

  const targetScreenId = expectedScreenId || screenId
  playerStore.saveDeviceIdentity(targetScreenId, deviceToken)
  showPairing.value = false
  // Re-initialize the player with the new identity
  playerStore.initialize(targetScreenId).then(() => {
    playerStore.startPolling()
  }).catch((err) => {
    console.error('[WebPlayer] Post-pairing init failed:', err)
  })
}

const sortedLayers = computed(() => {
  if (!template.value?.layers) return []
  return [...template.value.layers]
    .filter(layer => layer.is_active !== false)
    .sort((a, b) => {
      const zA = a.z_index || 0
      const zB = b.z_index || 0
      if (zA !== zB) return zA - zB
      return (a.name || '').localeCompare(b.name || '')
    })
})

const {
  scaleFactor,
  setupResizeListener,
  cleanupResizeListener,
} = useResponsiveScaling(template)

const containerStyle = computed(() => ({
  position: 'fixed',
  top: 0,
  left: 0,
  width: '100vw',
  height: '100vh',
  overflow: 'visible',
  backgroundColor: '#000000',
}))

const templateContainerStyle = computed(() => ({
  width: '100vw',
  height: '100vh',
  position: 'relative',
  visibility: 'visible',
  opacity: 1,
  overflow: 'visible',
}))

let contextMenuHandler = null
let keydownHandler = null

const toggleFullscreen = async () => {
  const el = playerContainer.value
  if (!el) return
  try {
    if (!document.fullscreenElement) {
      await (el.requestFullscreen || el.webkitRequestFullscreen || el.mozRequestFullScreen || el.msRequestFullscreen).call(el)
    } else {
      await (document.exitFullscreen || document.webkitExitFullscreen || document.mozCancelFullScreen || document.msExitFullscreen).call(document)
    }
  } catch (_) { /* ignore */ }
}

onMounted(async () => {
  document.documentElement.style.overflow = 'hidden'
  document.body.style.overflow = 'hidden'

  contextMenuHandler = (e) => e.preventDefault()
  document.addEventListener('contextmenu', contextMenuHandler)

  keydownHandler = (e) => {
    if (e.key === 'F12') return
    if (e.key === 'f' || e.key === 'F') { toggleFullscreen(); e.preventDefault(); return }
    if (e.ctrlKey || e.metaKey) return
    e.preventDefault()
  }
  document.addEventListener('keydown', keydownHandler, true)
  document.addEventListener('selectstart', (e) => e.preventDefault())
  document.addEventListener('dragstart', (e) => e.preventDefault())

  playerStore.setActiveScreen(routeScreenId.value)

  if (forcePairing.value) {
    showPairing.value = true
    return
  }

  // Decide: pair or play
  if (!playerStore.hasDeviceIdentity(routeScreenId.value)) {
    showPairing.value = true
    return
  }

  try {
    await playerStore.initialize(routeScreenId.value)

    if (playerStore.status === 'unpaired') {
      showPairing.value = true
      return
    }

    playerStore.startPolling()
  } catch (error) {
    if (
      error.code === 'SCREEN_NOT_PAIRED' ||
      error.code === 'DEVICE_NOT_PAIRED' ||
      error.code === 'DEVICE_AUTH_FAILED'
    ) {
      playerStore.clearDeviceIdentity(routeScreenId.value)
      showPairing.value = true
      return
    }
    playerStore.status = 'error'
    playerStore.errorMessage = error.message || 'Initialization failed'
  }
})

onUnmounted(() => {
  document.documentElement.style.overflow = ''
  document.body.style.overflow = ''
  if (contextMenuHandler) document.removeEventListener('contextmenu', contextMenuHandler)
  if (keydownHandler) document.removeEventListener('keydown', keydownHandler, true)
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
  pointer-events: none;
}

.message-box {
  max-width: 70vw;
  padding: 18px 22px;
  background: rgba(0, 0, 0, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
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
  overflow: visible;
  transform: translateZ(0);
  -webkit-transform: translateZ(0);
  contain: layout style;
}
</style>
