<template>
  <AppLayout>
    <div class="max-w-4xl mx-auto space-y-6">
      <div class="flex items-center justify-between">
        <h1 class="text-2xl font-bold text-primary">Add New Screen</h1>
        <button
          @click="$router.push('/screens')"
          class="btn-secondary px-4 py-2 rounded-lg"
        >
          Cancel
        </button>
      </div>

      <Card>
        <div class="space-y-6">
          <div>
            <h2 class="text-lg font-semibold mb-4">Pair Your Screen</h2>
            <p class="text-gray-600 dark:text-gray-300 mb-6">
              Connect your TV or display device to your account. You can either scan the QR code
              displayed on the screen or enter the 6-digit pairing code manually.
            </p>
          </div>

          <!-- Tabs for QR scan vs manual entry -->
          <div class="border-b border-gray-200 dark:border-gray-700">
            <nav class="flex space-x-8">
              <button
                @click="activeTab = 'qr'"
                :class="[
                  'py-4 px-1 border-b-2 font-medium text-sm transition-colors',
                  activeTab === 'qr'
                    ? 'border-primary text-primary'
                    : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
                ]"
              >
                Scan QR Code
              </button>
              <button
                @click="activeTab = 'manual'"
                :class="[
                  'py-4 px-1 border-b-2 font-medium text-sm transition-colors',
                  activeTab === 'manual'
                    ? 'border-primary text-primary'
                    : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
                ]"
              >
                Enter Code Manually
              </button>
            </nav>
          </div>

          <!-- QR Code Tab -->
          <div v-if="activeTab === 'qr'" class="space-y-4">
            <div class="bg-gray-50 dark:bg-gray-800 p-6 rounded-lg">
              <p class="text-sm text-gray-600 dark:text-gray-300 mb-4">
                Make sure the TV screen is displaying the pairing code. Then either:
              </p>
              <ul class="list-disc list-inside space-y-2 text-sm text-gray-600 dark:text-gray-300 mb-4">
                <li>Use your device camera to scan the QR code on the TV</li>
                <li>Or paste the pairing URL from the QR code below</li>
              </ul>

              <!-- Camera input (if supported) -->
              <div v-if="cameraSupported" class="mb-4">
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Scan QR Code
                </label>
                <div class="relative">
                  <input
                    ref="qrFileInput"
                    type="file"
                    accept="image/*"
                    capture="environment"
                    @change="handleQRFileUpload"
                    class="hidden"
                  />
                  <button
                    @click="$refs.qrFileInput?.click()"
                    class="btn-secondary w-full py-3"
                  >
                    📷 Take Photo or Choose Image
                  </button>
                </div>
              </div>

              <!-- Manual URL input -->
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Or Paste Pairing URL
                </label>
                <input
                  v-model="qrUrlInput"
                  type="text"
                  placeholder="https://your-domain/connect?token=..."
                  class="input-base w-full px-3 py-2 rounded-lg"
                  @input="handleQRUrlInput"
                />
                <p v-if="qrUrlError" class="text-sm text-red-600 dark:text-red-400 mt-1">{{ qrUrlError }}</p>
              </div>
            </div>
          </div>

          <!-- Manual Code Entry Tab -->
          <div v-if="activeTab === 'manual'" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                6-Digit Pairing Code
              </label>
              <input
                v-model="pairingCode"
                type="text"
                maxlength="6"
                pattern="[0-9]{6}"
                placeholder="123456"
                class="input-base w-full px-3 py-2 rounded-lg text-center text-2xl font-mono tracking-widest"
                @input="handleCodeInput"
              />
              <p v-if="codeError" class="text-sm text-red-600 dark:text-red-400 mt-1">{{ codeError }}</p>
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Enter the 6-digit code displayed on your TV screen
              </p>
            </div>
          </div>

          <!-- Screen Name (optional) -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Screen Name (Optional)
            </label>
            <input
              v-model="screenName"
              type="text"
              placeholder="e.g., Lobby TV, Conference Room Display"
              class="input-base w-full px-3 py-2 rounded-lg"
              maxlength="255"
            />
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Give your screen a friendly name to identify it easily
            </p>
          </div>

          <!-- Status Messages -->
          <div v-if="statusMessage" class="p-4 rounded-lg" :class="statusMessageClass">
            <p class="text-sm font-medium">{{ statusMessage }}</p>
          </div>

          <!-- Action Buttons -->
          <div class="flex justify-end space-x-3 pt-4 border-t border-gray-200 dark:border-gray-700">
            <button
              @click="$router.push('/screens')"
              class="btn-secondary px-6 py-2 rounded-lg"
            >
              Cancel
            </button>
            <button
              @click="pairScreen"
              :disabled="!canPair || isPairing"
              class="btn-primary px-6 py-2 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span v-if="isPairing">Pairing...</span>
              <span v-else>Pair Screen</span>
            </button>
          </div>
        </div>
      </Card>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { pairingAPI } from '@/services/api'
import { useScreensStore } from '@/stores/screens'
import AppLayout from '@/components/layout/AppLayout.vue'
import Card from '@/components/common/Card.vue'

const router = useRouter()
const screensStore = useScreensStore()

// State
const activeTab = ref('qr') // 'qr' | 'manual'
const pairingCode = ref('')
const qrUrlInput = ref('')
const screenName = ref('')
const isPairing = ref(false)
const statusMessage = ref('')
const statusMessageClass = ref('')
const codeError = ref('')
const qrUrlError = ref('')
const cameraSupported = ref(false)
const qrFileInput = ref(null)

// Computed
const canPair = computed(() => {
  if (activeTab.value === 'manual') {
    return pairingCode.value.length === 6 && /^\d{6}$/.test(pairingCode.value)
  } else {
    // QR tab - need valid URL with token
    return qrUrlInput.value.trim().length > 0 && (
      qrUrlInput.value.includes('token=') || 
      qrUrlInput.value.match(/token=([^&]+)/)
    )
  }
})

// Methods
function handleCodeInput(event) {
  // Only allow digits
  pairingCode.value = event.target.value.replace(/\D/g, '').slice(0, 6)
  codeError.value = ''
  
  if (pairingCode.value.length === 6) {
    statusMessage.value = ''
  }
}

function handleQRUrlInput() {
  qrUrlError.value = ''
  
  // Extract token from URL
  if (qrUrlInput.value.includes('token=')) {
    statusMessage.value = 'QR code URL detected. Click "Pair Screen" to continue.'
    statusMessageClass.value = 'bg-blue-50 text-blue-800'
  } else {
    statusMessage.value = ''
  }
}

function handleQRFileUpload(event) {
  const file = event.target.files?.[0]
  if (!file) return
  
  // For now, we'll just show a message
  // In a production app, you'd use a QR code scanning library like jsQR
  statusMessage.value = 'QR code scanning from image is not yet implemented. Please use the URL input or manual code entry.'
  statusMessageClass.value = 'bg-yellow-50 text-yellow-800'
  
  // Reset file input
  if (qrFileInput.value) {
    qrFileInput.value.value = ''
  }
}

async function pairScreen() {
  if (!canPair.value || isPairing.value) return
  
  isPairing.value = true
  statusMessage.value = ''
  codeError.value = ''
  qrUrlError.value = ''
  
  try {
    // Build request payload - only include fields that have values
    const payload = {}
    
    if (activeTab.value === 'manual') {
      if (pairingCode.value && pairingCode.value.length === 6) {
        payload.pairing_code = pairingCode.value
      }
    } else {
      // Extract token from URL
      try {
        const url = new URL(qrUrlInput.value)
        const token = url.searchParams.get('token')
        if (token) {
          payload.pairing_token = token
        } else {
          throw new Error('Invalid QR code URL. Token not found.')
        }
      } catch (urlError) {
        // If URL parsing fails, try to extract token from string
        const tokenMatch = qrUrlInput.value.match(/token=([^&]+)/)
        if (tokenMatch && tokenMatch[1]) {
          payload.pairing_token = tokenMatch[1]
        } else {
          throw new Error('Invalid QR code URL. Token not found.')
        }
      }
    }
    
    // Add screen name if provided
    if (screenName.value && screenName.value.trim()) {
      payload.screen_name = screenName.value.trim()
    }
    
    // Validate that we have either code or token
    if (!payload.pairing_code && !payload.pairing_token) {
      throw new Error('Please enter a pairing code or QR code URL')
    }
    
    // Call pairing API
    const response = await pairingAPI.bind(payload)
    
    if (response.data.status === 'success') {
      const screen = response.data.screen
      statusMessage.value = `Screen "${screen.name}" paired successfully!`
      statusMessageClass.value = 'bg-green-50 text-green-800'
      
      // Optimistically add screen to store with "Connecting" state
      const optimisticScreen = {
        ...screen,
        is_online: false,
        _isNew: true,
        _createdAt: new Date().toISOString(),
      }
      
      // Check if screen already exists in store
      const existingIndex = screensStore.screens.findIndex(s => s.id === screen.id)
      if (existingIndex !== -1) {
        screensStore.screens[existingIndex] = optimisticScreen
      } else {
        screensStore.screens.push(optimisticScreen)
      }
      
      // Immediately fetch the latest status (in case heartbeat already arrived)
      // This ensures we get the real status without waiting for next poll
      screensStore.fetchSingleScreenStatus(screen.id).catch(err => {
        console.warn('Failed to fetch initial screen status after pairing:', err)
      })
      
      // Redirect to screens list after a short delay
      setTimeout(() => {
        router.push('/screens')
      }, 2000)
    } else {
      throw new Error(response.data.message || 'Pairing failed')
    }
  } catch (error) {
    console.error('Pairing error:', error)
    
    // Extract error message from various possible locations
    let errorMsg = 'Failed to pair screen. Please try again.'
    
    if (error.response?.data) {
      const data = error.response.data
      
      // Check for non_field_errors first (general errors)
      if (data.non_field_errors && data.non_field_errors.length > 0) {
        errorMsg = data.non_field_errors[0]
      }
      // Check for specific field errors
      else if (data.pairing_code && Array.isArray(data.pairing_code)) {
        errorMsg = data.pairing_code[0]
        codeError.value = data.pairing_code[0]
      }
      else if (data.pairing_token && Array.isArray(data.pairing_token)) {
        errorMsg = data.pairing_token[0]
        qrUrlError.value = data.pairing_token[0]
      }
      // Check for error field
      else if (data.error) {
        errorMsg = data.error
      }
      // Check for detail field (DRF default)
      else if (data.detail) {
        errorMsg = data.detail
      }
    } else if (error.message) {
      errorMsg = error.message
    }
    
    statusMessage.value = errorMsg
    statusMessageClass.value = 'bg-red-50 text-red-800'
  } finally {
    isPairing.value = false
  }
}

// Check if URL has token parameter (from QR scan redirect)
onMounted(() => {
  const urlParams = new URLSearchParams(window.location.search)
  const token = urlParams.get('token')
  
  if (token) {
    // User came from QR code scan
    activeTab.value = 'qr'
    qrUrlInput.value = window.location.href
    handleQRUrlInput()
    
    // Clean up URL
    window.history.replaceState({}, document.title, window.location.pathname)
  }
  
  // Check camera support
  cameraSupported.value = 'mediaDevices' in navigator && 'getUserMedia' in navigator.mediaDevices
})
</script>

<style scoped>
/* Additional styles if needed */
</style>

