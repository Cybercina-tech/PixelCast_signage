import { defineStore } from 'pinia'
import playerAPI from '@/services/playerApi'
import { collectSystemInfo } from '@/composables/useSystemInfo'

export const usePlayerStore = defineStore('player', {
  state: () => ({
    status: 'loading', // loading | success | no_template | error | unpaired
    template: null,
    errorMessage: null,
    retryCountdown: 0,
    pollingInterval: null,
    heartbeatInterval: null,
    retryTimer: null,
    lastSuccessfulHeartbeat: null, // Timestamp of last successful heartbeat
    connectionLostTimer: null // Timer to track connection loss
  }),

  actions: {
    /**
     * Initialize the player
     * Loads configuration and fetches initial template
     */
    async initialize() {
      try {
        // Load configuration
        await this.loadConfig()
        
        // Verify credentials are actually set before proceeding
        const storedToken = localStorage.getItem('player_auth_token')
        const storedSecret = localStorage.getItem('player_secret_key')
        
        if (!storedToken || !storedSecret) {
          const error = new Error('Credentials not found after loading. Please pair your screen first.')
          error.code = 'CREDENTIALS_NOT_LOADED'
          throw error
        }
        
        console.log('[PlayerStore] Credentials verified, fetching template')
        
        // Fetch initial template
        await this.fetchTemplate()
      } catch (error) {
        console.error('[PlayerStore] Player initialization error:', error)
        this.status = 'error'
        this.errorMessage = error.message || 'Initialization failed'
        
        // If credentials are missing, set specific status
        if (error.code === 'CREDENTIALS_MISSING' || 
            error.code === 'CREDENTIALS_EMPTY' || 
            error.code === 'CREDENTIALS_NOT_LOADED' ||
            error.message?.includes('credentials')) {
          this.status = 'unpaired'
          this.errorMessage = 'Please pair your screen first to continue.'
        }
        
        // Re-throw to allow caller to handle (e.g., redirect)
        throw error
      }
    },

    /**
     * Load player configuration from localStorage, URL params, or env config
     * Priority: localStorage > URL params > env vars
     */
    async loadConfig() {
      let authToken = null
      let secretKey = null
      let source = 'none'
      
      // 1. Try localStorage first (persistent pairing)
      // New method: Check for screen_id first (after pairing, only screen_id is stored)
      try {
        const storedScreenId = localStorage.getItem('player_screen_id')
        const isPaired = localStorage.getItem('player_is_paired') === 'true'
        
        if (storedScreenId && isPaired) {
          // New method: Use screen_id (credentials are stored in backend)
          playerAPI.setScreenId(storedScreenId)
          source = 'localStorage (screen_id)'
          console.log('[PlayerStore] Loaded screen_id from localStorage', {
            screenId: storedScreenId,
            isPaired: isPaired
          })
          // Don't set authToken/secretKey - they're not needed with screen_id method
        } else {
          // Legacy method: Try to load credentials (for backward compatibility)
          const storedToken = localStorage.getItem('player_auth_token')
          const storedSecret = localStorage.getItem('player_secret_key')
          
          if (storedToken && storedSecret) {
            authToken = storedToken
            secretKey = storedSecret
            source = 'localStorage (legacy)'
            console.log('[PlayerStore] Loaded credentials from localStorage (legacy)', {
              tokenPrefix: authToken.substring(0, 8) + '...',
              secretLength: secretKey.length
            })
          } else {
            console.debug('[PlayerStore] No credentials or screen_id in localStorage', {
              hasScreenId: !!storedScreenId,
              isPaired: isPaired,
              hasToken: !!storedToken,
              hasSecret: !!storedSecret
            })
          }
        }
      } catch (error) {
        console.warn('[PlayerStore] Failed to read from localStorage:', error)
      }
      
      // 2. Fallback to URL params
      if (!authToken || !secretKey) {
        const urlParams = new URLSearchParams(window.location.search)
        authToken = urlParams.get('auth_token')
        secretKey = urlParams.get('secret_key')
        
        if (authToken && secretKey) {
          source = 'urlParams'
          console.log('[PlayerStore] Loaded credentials from URL params', {
            tokenPrefix: authToken.substring(0, 8) + '...',
            secretLength: secretKey.length
          })
          
          // Save to localStorage for future use
          try {
            localStorage.setItem('player_auth_token', authToken)
            localStorage.setItem('player_secret_key', secretKey)
            const screenId = urlParams.get('screen_id')
            if (screenId) {
              localStorage.setItem('player_screen_id', screenId)
            }
            console.log('[PlayerStore] Saved credentials to localStorage')
          } catch (error) {
            console.warn('[PlayerStore] Failed to save credentials to localStorage:', error)
          }
        } else {
          console.debug('[PlayerStore] No credentials in URL params', {
            hasToken: !!authToken,
            hasSecret: !!secretKey,
            url: window.location.href
          })
        }
      }
      
      // 3. Fallback to env vars (for development/testing)
      if (!authToken || !secretKey) {
        authToken = import.meta.env.VITE_PLAYER_AUTH_TOKEN
        secretKey = import.meta.env.VITE_PLAYER_SECRET_KEY
        if (authToken && secretKey) {
          source = 'env'
          console.log('[PlayerStore] Loaded credentials from environment variables', {
            tokenPrefix: authToken.substring(0, 8) + '...',
            secretLength: secretKey.length
          })
        } else {
          console.debug('[PlayerStore] No credentials in environment variables')
        }
      }

      if (!authToken || !secretKey) {
        console.error('[PlayerStore] No credentials found from any source', {
          checkedSources: ['localStorage', 'urlParams', 'env'],
          localStorage: {
            hasToken: !!localStorage.getItem('player_auth_token'),
            hasSecret: !!localStorage.getItem('player_secret_key')
          },
          urlParams: window.location.search,
          env: {
            hasToken: !!import.meta.env.VITE_PLAYER_AUTH_TOKEN,
            hasSecret: !!import.meta.env.VITE_PLAYER_SECRET_KEY
          }
        })
        const error = new Error('auth_token and secret_key are required. Please pair your screen first.')
        error.code = 'CREDENTIALS_MISSING'
        throw error
      }

      // Validate credentials are not empty strings
      if (authToken.trim() === '' || secretKey.trim() === '') {
        console.error('[PlayerStore] Credentials are empty strings', {
          source,
          tokenLength: authToken.length,
          secretLength: secretKey.length
        })
        const error = new Error('Invalid credentials: auth_token and secret_key cannot be empty.')
        error.code = 'CREDENTIALS_EMPTY'
        throw error
      }

      console.log('[PlayerStore] Credentials loaded successfully', {
        source,
        tokenPrefix: authToken.substring(0, 8) + '...',
        secretLength: secretKey.length
      })

      // Store in playerAPI
      playerAPI.setCredentials(authToken, secretKey)
      
      // Verify credentials were set
      if (!playerAPI || typeof playerAPI.setCredentials !== 'function') {
        console.error('[PlayerStore] playerAPI.setCredentials is not available')
        const error = new Error('Player API not initialized')
        error.code = 'API_NOT_INITIALIZED'
        throw error
      }
      
      console.log('[PlayerStore] Credentials set in playerAPI successfully')
    },

    /**
     * Fetch template from API
     */
    async fetchTemplate() {
      try {
        this.status = 'loading'
        this.errorMessage = null

        const response = await playerAPI.fetchTemplate()

        if (response.status === 'success') {
          this.template = response.template
          this.status = 'success'
        } else if (response.status === 'no_template') {
          this.template = null
          this.status = 'no_template'
        } else {
          throw new Error(response.message || 'Unknown response status')
        }
      } catch (error) {
        console.error('Template fetch error:', error)
        
        // Check if credentials are invalid (401 Unauthorized) or screen not found (404)
        const errorData = error.response?.data || {}
        const errorMessage = errorData.error || errorData.auth_token?.[0] || errorData.detail || error.message || ''
        const statusCode = error.response?.status
        
        if (statusCode === 401 || statusCode === 404) {
          // Check if screen was deleted/unpaired
          if (
            errorMessage.includes('Invalid authentication') ||
            errorMessage.includes('Screen not found') ||
            errorMessage.includes('Invalid authentication token') ||
            statusCode === 404
          ) {
            // Screen was unpaired/deleted - show unpair message
            this.clearCredentials()
            this.status = 'unpaired'
            this.errorMessage = 'Device has been unpaired from your account.'
            this.stopPolling() // Stop all polling
            return // Don't throw, just set status
          }
          
          // Other 401 errors - clear credentials and show error
          this.clearCredentials()
          this.status = 'error'
          this.errorMessage = 'Invalid credentials. Please pair your screen again.'
          throw new Error('Invalid credentials. Redirecting to pairing page.')
        }
        
        this.status = 'error'
        this.errorMessage = error.response?.data?.error || error.message || 'Failed to fetch template'
        
        // Start retry countdown
        this.startRetryCountdown()
      }
    },

    /**
     * Start retry countdown (30 seconds)
     */
    startRetryCountdown() {
      this.retryCountdown = 30
      
      if (this.retryTimer) {
        clearInterval(this.retryTimer)
      }

      this.retryTimer = setInterval(() => {
        this.retryCountdown--
        
        if (this.retryCountdown <= 0) {
          clearInterval(this.retryTimer)
          this.retryTimer = null
          // Retry fetching
          this.fetchTemplate()
        }
      }, 1000)
    },

    /**
     * Send heartbeat with system information
     */
    async sendHeartbeat() {
      try {
        const systemInfo = collectSystemInfo()
        const response = await playerAPI.sendHeartbeat(systemInfo)
        
        // Update last successful heartbeat timestamp
        this.lastSuccessfulHeartbeat = Date.now()
        
        // Clear connection lost timer since we got a successful heartbeat
        if (this.connectionLostTimer) {
          clearTimeout(this.connectionLostTimer)
          this.connectionLostTimer = null
        }
        
        // Start monitoring for connection loss (5 minutes = 300000 ms)
        this.startConnectionLossMonitoring()
        
        console.log('Heartbeat sent successfully', {
          is_online: response.is_online,
          screen_id: response.screen_id,
          last_heartbeat_at: response.last_heartbeat_at
        })
        return response
      } catch (error) {
        console.error('Heartbeat error:', error)
        
        // Check if screen was deleted/unpaired
        const errorData = error.response?.data || {}
        const errorMessage = errorData.error || errorData.auth_token?.[0] || errorData.detail || error.message || ''
        const statusCode = error.response?.status
        
        // Check if screen was deleted/unpaired (401, 404, or validation error for auth_token)
        if (
          statusCode === 401 ||
          statusCode === 404 ||
          (statusCode === 400 && (
            errorMessage.includes('Invalid authentication token') ||
            errorMessage.includes('Invalid authentication') ||
            errorData.auth_token
          ))
        ) {
          // Screen was unpaired/deleted - show unpair message
          this.handleUnpair('Device has been unpaired from your account.')
          throw error // Re-throw to allow caller to handle
        }
        
        // Check if we've lost connection for 5 minutes
        this.checkConnectionLoss()
        
        // Re-throw error to allow caller to handle retries
        throw error
      }
    },

    /**
     * Start monitoring for connection loss
     * If no successful heartbeat for 5 minutes, unpair the screen
     */
    startConnectionLossMonitoring() {
      // Clear existing timer
      if (this.connectionLostTimer) {
        clearTimeout(this.connectionLostTimer)
      }
      
      // Set timer for 5 minutes (300000 ms)
      this.connectionLostTimer = setTimeout(() => {
        this.checkConnectionLoss()
      }, 300000) // 5 minutes
    },

    /**
     * Check if connection has been lost for 5 minutes
     */
    checkConnectionLoss() {
      if (!this.lastSuccessfulHeartbeat) {
        // No successful heartbeat yet, start monitoring from now
        this.startConnectionLossMonitoring()
        return
      }
      
      const now = Date.now()
      const timeSinceLastHeartbeat = now - this.lastSuccessfulHeartbeat
      const fiveMinutes = 5 * 60 * 1000 // 5 minutes in milliseconds
      
      if (timeSinceLastHeartbeat >= fiveMinutes) {
        // Connection lost for 5 minutes - unpair screen
        console.warn('Connection lost for 5 minutes, unpairing screen...')
        this.handleUnpair('Connection lost for 5 minutes. Please pair your screen again.')
      }
    },

    /**
     * Handle screen unpairing
     */
    handleUnpair(message = 'Device has been unpaired.') {
      // Clear credentials
      this.clearCredentials()
      
      // Stop all polling and timers
      this.stopPolling()
      
      // Clear connection monitoring
      if (this.connectionLostTimer) {
        clearTimeout(this.connectionLostTimer)
        this.connectionLostTimer = null
      }
      
      // Set status to unpaired
      this.status = 'unpaired'
      this.errorMessage = message
      
      // Note: Redirect will be handled by WebPlayer component when status becomes 'unpaired'
    },

    /**
     * Start polling for template updates and sending heartbeats
     * Polls every 30 seconds if no template, or every 5 minutes if template exists
     * Sends heartbeat every 30 seconds
     */
    startPolling() {
      // Verify screen_id or credentials exist before starting polling
      const storedScreenId = localStorage.getItem('player_screen_id')
      const isPaired = localStorage.getItem('player_is_paired') === 'true'
      const storedToken = localStorage.getItem('player_auth_token')
      const storedSecret = localStorage.getItem('player_secret_key')
      
      // New method: Check for screen_id first
      if (!storedScreenId || !isPaired) {
        // Legacy method: Check for credentials
        if (!storedToken || !storedSecret) {
          console.error('[PlayerStore] Cannot start polling: screen not paired')
          this.status = 'error'
          this.errorMessage = 'Screen not paired. Please pair your screen first.'
          this.handleUnpair('Screen not paired. Please pair your screen again.')
          return
        }
      }
      
      // Verify playerAPI is available
      if (!playerAPI) {
        console.error('[PlayerStore] playerAPI not available')
        this.status = 'error'
        this.errorMessage = 'Player API not initialized'
        return
      }
      
      // Double-check that screen_id or credentials are actually set in playerAPI
      // This is important after pairing when screen_id was just saved
      try {
        if (storedScreenId && isPaired) {
          // New method: Re-set screen_id to ensure it's in playerAPI
          playerAPI.setScreenId(storedScreenId)
          console.log('[PlayerStore] Screen ID re-set in playerAPI after verification')
        } else if (storedToken && storedSecret) {
          // Legacy method: Re-set credentials to ensure they're in playerAPI
          if (typeof playerAPI.setCredentials === 'function') {
            playerAPI.setCredentials(storedToken, storedSecret)
            console.log('[PlayerStore] Credentials re-set in playerAPI after verification (legacy)')
          }
        }
      } catch (error) {
        console.error('[PlayerStore] Failed to set screen_id/credentials in playerAPI:', error)
        this.status = 'error'
        this.errorMessage = 'Failed to configure player API'
        return
      }
      
      console.log('[PlayerStore] Starting polling with credentials verified')
      
      if (this.pollingInterval) {
        clearInterval(this.pollingInterval)
        this.pollingInterval = null
      }

      // Initialize last successful heartbeat timestamp
      this.lastSuccessfulHeartbeat = Date.now()

      // Send initial heartbeat with a small delay to ensure credentials are fully set
      // This is especially important after pairing when credentials were just saved
      setTimeout(() => {
        this.sendHeartbeat().catch(error => {
          console.warn('[PlayerStore] Initial heartbeat failed, will retry:', error)
          console.warn('[PlayerStore] Heartbeat error details:', {
            message: error.message,
            status: error.response?.status,
            statusText: error.response?.statusText,
            data: error.response?.data
          })
          // Retry after 5 seconds
          setTimeout(() => {
            this.sendHeartbeat().catch(err => {
              console.error('[PlayerStore] Retry heartbeat also failed:', err)
              console.error('[PlayerStore] Retry heartbeat error details:', {
                message: err.message,
                status: err.response?.status,
                statusText: err.response?.statusText,
                data: err.response?.data
              })
              // Check connection loss even on retry failure
              this.checkConnectionLoss()
            })
          }, 5000)
        })
      }, 500) // Small delay to ensure everything is initialized

      // Start heartbeat interval (every 30 seconds for more frequent updates)
      this.heartbeatInterval = setInterval(() => {
        this.sendHeartbeat().catch(error => {
          console.error('Heartbeat failed:', error)
          // Check connection loss on each failure
          this.checkConnectionLoss()
        })
      }, 30000) // 30 seconds (reduced from 60 for faster status updates)

      const poll = () => {
        // Poll more frequently if no template (to detect when one is assigned)
        const interval = this.status === 'no_template' ? 30000 : 300000 // 30s or 5min
        
        this.pollingInterval = setInterval(() => {
          this.fetchTemplate().then(() => {
            // Restart polling with new interval if status changed
            if (this.pollingInterval) {
              const newInterval = this.status === 'no_template' ? 30000 : 300000
              if (newInterval !== interval) {
                clearInterval(this.pollingInterval)
                this.pollingInterval = null
                poll() // Restart with new interval
              }
            }
          })
        }, interval)
      }

      poll()
    },

    /**
     * Stop polling and heartbeat
     */
    stopPolling() {
      if (this.pollingInterval) {
        clearInterval(this.pollingInterval)
        this.pollingInterval = null
      }
      
      if (this.heartbeatInterval) {
        clearInterval(this.heartbeatInterval)
        this.heartbeatInterval = null
      }
      
      if (this.retryTimer) {
        clearInterval(this.retryTimer)
        this.retryTimer = null
      }
      
      if (this.connectionLostTimer) {
        clearTimeout(this.connectionLostTimer)
        this.connectionLostTimer = null
      }
    },
    
    /**
     * Clear stored credentials (for unpairing)
     */
    clearCredentials() {
      try {
        localStorage.removeItem('player_auth_token')
        localStorage.removeItem('player_secret_key')
        localStorage.removeItem('player_screen_id')
        localStorage.removeItem('player_paired_at')
        console.log('Credentials cleared from localStorage')
      } catch (error) {
        console.error('Failed to clear credentials:', error)
      }
    }
  }
})

