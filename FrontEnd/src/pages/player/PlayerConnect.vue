<template>
  <div class="player-connect bg-gradient-to-br from-slate-50 via-slate-100 to-slate-200 dark:from-slate-950 dark:via-slate-900 dark:to-slate-800 min-h-screen flex items-center justify-center p-4">
    <div class="connect-container w-full max-w-4xl">
      <!-- Loading state -->
      <Card v-if="status === 'loading'" class="text-center">
        <div class="flex flex-col items-center justify-center py-12">
          <div class="spinner mb-6"></div>
          <p class="text-lg font-semibold text-primary">Generating pairing code...</p>
        </div>
      </Card>

      <!-- Pairing state -->
      <div v-else-if="status === 'pairing'" class="space-y-6">
        <Card class="text-center">
          <h1 class="text-3xl md:text-4xl font-bold text-primary mb-12">Pair Your Screen</h1>
          
          <!-- 6-digit code section -->
          <div class="code-display mb-12">
            <div class="code-digits bg-gradient-to-br from-slate-100 to-slate-200 dark:from-slate-700 dark:to-slate-800 border-2 border-emerald-500/30 dark:border-emerald-400/30 rounded-2xl p-8 shadow-2xl inline-block">
              <div class="text-6xl md:text-7xl font-bold text-emerald-600 dark:text-emerald-400 font-mono tracking-wider">
                {{ pairingCode }}
              </div>
            </div>
            <p class="text-secondary mt-6 text-lg font-medium">Enter this code in your dashboard</p>
          </div>

          <!-- QR Code section -->
          <div class="qr-container">
            <div v-if="qrCodeDataUrl" class="qr-code-wrapper bg-gradient-to-br from-slate-100 to-slate-200 dark:from-slate-700 dark:to-slate-800 border-2 border-emerald-500/30 dark:border-emerald-400/30 rounded-2xl p-6 shadow-2xl inline-block">
              <img :src="qrCodeDataUrl" alt="QR Code" class="qr-code-image rounded-lg" />
            </div>
            <div v-else class="qr-placeholder bg-gradient-to-br from-slate-100 to-slate-200 dark:from-slate-700 dark:to-slate-800 border-2 border-emerald-500/30 dark:border-emerald-400/30 rounded-2xl p-12 flex items-center justify-center">
              <p class="text-secondary">Generating QR code...</p>
            </div>
            <p class="text-secondary mt-6 text-lg font-medium">Or scan this QR code</p>
          </div>

          <!-- Countdown timer -->
          <div class="countdown-container mt-12">
            <div class="bg-gradient-to-br from-slate-100 to-slate-200 dark:from-slate-700 dark:to-slate-800 border-2 border-emerald-500/30 dark:border-emerald-400/30 rounded-xl p-4 inline-block shadow-lg">
              <p class="text-secondary text-lg">
                Expires in <span class="countdown-value text-emerald-600 dark:text-emerald-400 font-bold font-mono text-xl">{{ formattedCountdown }}</span>
              </p>
            </div>
          </div>

          <!-- Status message -->
          <div v-if="statusMessage" class="status-message mt-6" :class="statusMessageClass">
            {{ statusMessage }}
          </div>
        </Card>
      </div>

      <!-- Error state -->
      <Card v-else-if="status === 'error'" class="text-center">
        <div class="error-content py-8">
          <div class="error-icon mb-6">
            <svg
              class="w-16 h-16 text-error mx-auto"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
          </div>
          <h2 class="text-2xl md:text-3xl font-bold text-primary mb-4">Connection Error</h2>
          <p class="text-secondary text-lg mb-6">{{ errorMessage }}</p>
          <button @click="retry" class="btn-primary px-6 py-3 rounded-xl">Retry</button>
        </div>
      </Card>

      <!-- Success state (redirecting) -->
      <Card v-else-if="status === 'success'" class="text-center">
        <div class="success-content py-12">
          <div class="success-icon mb-6">
            <div class="w-20 h-20 bg-success rounded-full flex items-center justify-center mx-auto">
              <svg
                class="w-12 h-12 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="3"
                  d="M5 13l4 4L19 7"
                />
              </svg>
            </div>
          </div>
          <h2 class="text-2xl md:text-3xl font-bold text-primary mb-4">Screen Paired Successfully!</h2>
          <p class="text-secondary text-lg">Redirecting to player...</p>
        </div>
      </Card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { pairingAPI } from '@/services/api'
import * as QRCode from 'qrcode'
import Card from '@/components/common/Card.vue'

const router = useRouter()

// State
const status = ref('loading') // loading | pairing | error | success
const pairingCode = ref('')
const pairingToken = ref('')
const qrCodeDataUrl = ref('')
const expiresAt = ref(null)
const countdown = ref(300) // 5 minutes in seconds
const statusMessage = ref('')
const statusMessageType = ref('') // 'info' | 'error' | 'success'
const errorMessage = ref('')

// Computed for status message class
const statusMessageClass = computed(() => {
  if (statusMessageType.value === 'error') {
    return 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-800 dark:text-red-300 rounded-xl p-4'
  } else if (statusMessageType.value === 'success') {
    return 'bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-800 text-emerald-800 dark:text-emerald-300 rounded-xl p-4'
  } else {
    return 'bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 text-blue-800 dark:text-blue-300 rounded-xl p-4'
  }
})

// Timers
let countdownTimer = null
let statusPollTimer = null
let themeObserver = null

// Computed
const formattedCountdown = computed(() => {
  const minutes = Math.floor(countdown.value / 60)
  const seconds = countdown.value % 60
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
})

// Methods
async function generatePairingSession() {
  try {
    status.value = 'loading'
    errorMessage.value = ''
    
    const response = await pairingAPI.generate()
    
    if (response.data.status === 'success') {
      const session = response.data.pairing_session
      pairingCode.value = session.pairing_code
      pairingToken.value = session.pairing_token
      expiresAt.value = new Date(session.expires_at)
      
      // Calculate initial countdown
      const now = new Date()
      const expires = new Date(session.expires_at)
      countdown.value = Math.max(0, Math.floor((expires - now) / 1000))
      
      // Generate QR code
      await generateQRCode(session.qr_code_url)
      
      // Watch for theme changes and regenerate QR code
      watchThemeChanges()
      
      // Start countdown
      startCountdown()
      
      // Start polling for pairing status
      startStatusPolling()
      
      status.value = 'pairing'
    } else {
      throw new Error('Failed to generate pairing session')
    }
  } catch (error) {
    console.error('Pairing generation error:', error)
    status.value = 'error'
    errorMessage.value = error.response?.data?.error || error.message || 'Failed to generate pairing code'
  }
}

async function generateQRCode(url) {
  try {
    // Detect dark mode
    const isDark = document.documentElement.classList.contains('dark')
    
    const dataUrl = await QRCode.toDataURL(url, {
      width: 400,
      margin: 2,
      color: {
        dark: isDark ? '#FFFFFF' : '#000000',
        light: isDark ? '#1e293b' : '#FFFFFF' // slate-800 for dark mode, white for light
      },
      errorCorrectionLevel: 'M'
    })
    qrCodeDataUrl.value = dataUrl
  } catch (error) {
    console.error('QR code generation error:', error)
    statusMessage.value = 'Failed to generate QR code'
    statusMessageType.value = 'error'
  }
}

function startCountdown() {
  if (countdownTimer) {
    clearInterval(countdownTimer)
  }
  
  countdownTimer = setInterval(() => {
    if (countdown.value > 0) {
      countdown.value--
    } else {
      // Expired - regenerate
      clearInterval(countdownTimer)
      statusMessage.value = 'Pairing code expired. Generating new code...'
      statusMessageType.value = 'error'
      setTimeout(() => {
        generatePairingSession()
      }, 2000)
    }
  }, 1000)
}

function startStatusPolling() {
  if (statusPollTimer) {
    clearInterval(statusPollTimer)
  }
  
  // Poll every 2 seconds
  statusPollTimer = setInterval(async () => {
    if (!pairingToken.value) return
    
    try {
      const response = await pairingAPI.status({ pairing_token: pairingToken.value })
      
      if (response.data.status === 'paired') {
        // Successfully paired!
        clearInterval(statusPollTimer)
        clearInterval(countdownTimer)
        
        status.value = 'success'
        statusMessage.value = 'Screen paired successfully!'
        statusMessageType.value = 'success'
        
        // Store only screen_id (credentials are stored in backend, not in localStorage)
        const { screen_id } = response.data
        
        // Save only screen_id to localStorage (credentials removed for security)
        try {
          localStorage.setItem('player_screen_id', screen_id)
          // Store timestamp to track when paired
          localStorage.setItem('player_paired_at', new Date().toISOString())
          // Mark as paired
          localStorage.setItem('player_is_paired', 'true')
          // Remove old credentials if they exist
          localStorage.removeItem('player_auth_token')
          localStorage.removeItem('player_secret_key')
          console.log('Screen ID saved to localStorage, credentials removed')
        } catch (error) {
          console.error('Failed to save screen_id to localStorage:', error)
        }
        
        // Redirect to player (credentials will be loaded from localStorage)
        setTimeout(() => {
          router.push({
            path: '/player'
          })
        }, 2000)
      } else if (response.data.status === 'expired') {
        // Expired - regenerate
        clearInterval(statusPollTimer)
        clearInterval(countdownTimer)
        statusMessage.value = 'Pairing code expired. Generating new code...'
        statusMessageType.value = 'error'
        setTimeout(() => {
          generatePairingSession()
        }, 2000)
      }
    } catch (error) {
      // Silently handle polling errors (network issues, etc.)
      console.error('Status polling error:', error)
    }
  }, 2000)
}

function retry() {
  generatePairingSession()
}

// Watch for theme changes and regenerate QR code
function watchThemeChanges() {
  if (themeObserver) {
    themeObserver.disconnect()
  }
  
  // Watch for class changes on html element
  themeObserver = new MutationObserver(() => {
    if (pairingToken.value && qrCodeDataUrl.value) {
      // Regenerate QR code with new theme colors
      // Use the same URL pattern as when generating
      const baseUrl = window.location.origin
      const qrUrl = `${baseUrl}/screens/add?token=${pairingToken.value}`
      generateQRCode(qrUrl)
    }
  })
  
  themeObserver.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ['class']
  })
}

// Lifecycle
onMounted(() => {
  // Check if already paired (credentials exist in localStorage)
  const storedToken = localStorage.getItem('player_auth_token')
  const storedSecret = localStorage.getItem('player_secret_key')
  
  if (storedToken && storedSecret) {
    // Already paired - redirect to player
    console.log('Credentials found in localStorage, redirecting to player')
    router.push('/player')
    return
  }
  
  // Not paired yet - generate pairing session
  generatePairingSession()
})

onUnmounted(() => {
  if (countdownTimer) {
    clearInterval(countdownTimer)
  }
  if (statusPollTimer) {
    clearInterval(statusPollTimer)
  }
  if (themeObserver) {
    themeObserver.disconnect()
  }
})
</script>

<style scoped>
/* Loading spinner */
.spinner {
  width: 60px;
  height: 60px;
  border: 4px solid;
  border-color: rgba(16, 185, 129, 0.2);
  border-top-color: rgb(16, 185, 129);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.dark .spinner {
  border-color: rgba(16, 185, 129, 0.3);
  border-top-color: rgb(16, 185, 129);
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Code display */
.code-display {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.code-digits {
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.code-digits::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(16, 185, 129, 0.1), transparent);
  transition: left 0.5s;
}

.code-digits:hover::before {
  left: 100%;
}

.code-digits:hover {
  transform: scale(1.02);
  box-shadow: 0 20px 40px rgba(16, 185, 129, 0.2), 0 0 20px rgba(16, 185, 129, 0.1);
  border-color: rgba(16, 185, 129, 0.5);
}

.dark .code-digits:hover {
  box-shadow: 0 20px 40px rgba(16, 185, 129, 0.3), 0 0 30px rgba(16, 185, 129, 0.2);
  border-color: rgba(16, 185, 129, 0.6);
}

/* QR Code */
.qr-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.qr-code-wrapper {
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.qr-code-wrapper::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(16, 185, 129, 0.1), transparent);
  transition: left 0.5s;
  z-index: 1;
  pointer-events: none;
}

.qr-code-wrapper:hover::before {
  left: 100%;
}

.qr-code-wrapper:hover {
  transform: scale(1.02);
  box-shadow: 0 20px 40px rgba(16, 185, 129, 0.2), 0 0 20px rgba(16, 185, 129, 0.1);
  border-color: rgba(16, 185, 129, 0.5);
}

.dark .qr-code-wrapper:hover {
  box-shadow: 0 20px 40px rgba(16, 185, 129, 0.3), 0 0 30px rgba(16, 185, 129, 0.2);
  border-color: rgba(16, 185, 129, 0.6);
}

.qr-code-image {
  width: 100%;
  max-width: 300px;
  height: auto;
  display: block;
  position: relative;
  z-index: 0;
}

.qr-placeholder {
  width: 300px;
  height: 300px;
  min-height: 300px;
}

/* Countdown */
.countdown-value {
  font-family: 'Courier New', monospace;
  text-shadow: 0 0 10px rgba(16, 185, 129, 0.3);
}

.dark .countdown-value {
  text-shadow: 0 0 15px rgba(16, 185, 129, 0.5);
}

/* Error icon */
.error-icon {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

/* Success icon */
.success-icon {
  animation: scaleIn 0.5s ease-out;
}

@keyframes scaleIn {
  from {
    transform: scale(0);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .code-digits {
    padding: 1.5rem !important;
  }
  
  .code-digits .text-6xl {
    font-size: 3rem;
  }
  
  .qr-code-image {
    max-width: 250px;
  }
  
  .qr-placeholder {
    width: 250px;
    height: 250px;
    min-height: 250px;
  }
}
</style>

