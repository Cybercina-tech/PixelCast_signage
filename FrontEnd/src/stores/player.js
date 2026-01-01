import { defineStore } from 'pinia'
import playerAPI from '@/services/playerApi'
import { collectSystemInfo } from '@/composables/useSystemInfo'

export const usePlayerStore = defineStore('player', {
  state: () => ({
    status: 'loading', // loading | success | no_template | error | unpaired
    template: null,
    errorMessage: null,
    retryCountdown: 0,
    // UI overlays (e.g., display_message command)
    overlayMessage: null,
    overlayVisible: false,
    overlayTimer: null,
    pollingInterval: null,
    heartbeatInterval: null,
    commandPollingInterval: null, // Interval for polling commands
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
        // Load configuration (only screen_id)
        await this.loadConfig()
        
        // Verify screen_id exists
        const storedScreenId = localStorage.getItem('player_screen_id')
        
        if (!storedScreenId) {
          const error = new Error('Screen not paired. Please pair your screen first.')
          error.code = 'SCREEN_NOT_PAIRED'
          throw error
        }
        
        console.log('[PlayerStore] Screen ID verified, fetching template', {
          screenId: storedScreenId
        })
        
        // Fetch initial template
        await this.fetchTemplate()
      } catch (error) {
        console.error('[PlayerStore] Player initialization error:', error)
        this.status = 'error'
        this.errorMessage = error.message || 'Initialization failed'
        
        // If screen_id is missing, set unpaired status
        if (error.code === 'SCREEN_NOT_PAIRED' || 
            error.message?.includes('not paired') ||
            error.message?.includes('screen_id')) {
          this.status = 'unpaired'
          this.errorMessage = 'Please pair your screen first to continue.'
        }
        
        // Re-throw to allow caller to handle (e.g., redirect)
        throw error
      }
    },

    /**
     * Load player configuration from localStorage or URL params
     * Priority: localStorage > URL params
     * ONLY looks for screen_id - no token logic
     */
    async loadConfig() {
      let screenId = null
      let source = 'none'
      
      // 1. Try localStorage first (persistent pairing)
      try {
        screenId = localStorage.getItem('player_screen_id')
        if (screenId) {
          source = 'localStorage'
          console.log('[PlayerStore] Loaded screen_id from localStorage', {
            screenId: screenId
          })
        }
      } catch (error) {
        console.warn('[PlayerStore] Failed to read from localStorage:', error)
      }
      
      // 2. Fallback to URL params (only if screen_id not found in localStorage)
      if (!screenId) {
        const urlParams = new URLSearchParams(window.location.search)
        screenId = urlParams.get('screen_id')
        
        if (screenId) {
          source = 'urlParams'
          console.log('[PlayerStore] Loaded screen_id from URL params', {
            screenId: screenId
          })
          
          // Save to localStorage for future use
          try {
            localStorage.setItem('player_screen_id', screenId)
            console.log('[PlayerStore] Saved screen_id to localStorage')
          } catch (error) {
            console.warn('[PlayerStore] Failed to save screen_id to localStorage:', error)
          }
        }
      }

      // Validate screen_id is present
      if (!screenId) {
        console.error('[PlayerStore] No screen_id found from any source', {
          checkedSources: ['localStorage', 'urlParams'],
          localStorage: {
            hasScreenId: !!localStorage.getItem('player_screen_id')
          },
          urlParams: window.location.search
        })
        const error = new Error('screen_id is required. Please pair your screen first.')
        error.code = 'SCREEN_ID_MISSING'
        throw error
      }

      // Set screen_id in playerAPI
      console.log('[PlayerStore] Using screen_id authentication', {
        source,
        screenId: screenId
      })
      playerAPI.setScreenId(screenId)
      
      // Verify authentication was set
      if (!playerAPI || typeof playerAPI.setScreenId !== 'function') {
        console.error('[PlayerStore] playerAPI.setScreenId is not available')
        const error = new Error('Player API not initialized')
        error.code = 'API_NOT_INITIALIZED'
        throw error
      }
      
      console.log('[PlayerStore] Screen ID set in playerAPI successfully')
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
        
        const errorData = error.response?.data || {}
        const errorMessage = errorData.error || errorData.message || error.message || ''
        const statusCode = error.response?.status
        
        // Handle 404 (screen not found) - but DON'T clear screen_id
        if (statusCode === 404) {
          if (errorMessage.includes('Screen not found')) {
            this.status = 'unpaired'
            this.errorMessage = 'Screen not found. Please verify your screen_id.'
            this.stopPolling()
            return // Don't throw, just set status
          }
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
        
        const errorData = error.response?.data || {}
        const errorMessage = errorData.error || errorData.message || error.message || ''
        const statusCode = error.response?.status
        
        // Handle 404 (screen not found) - but DON'T clear screen_id
        if (statusCode === 404) {
          if (errorMessage.includes('Screen not found')) {
            this.status = 'unpaired'
            this.errorMessage = 'Screen not found. Please verify your screen_id.'
            this.stopPolling()
            throw error
          }
        }
        
        // Check if we've lost connection for 5 minutes
        this.checkConnectionLoss()
        
        // Re-throw error to allow caller to handle retries
        throw error
      }
    },

    /**
     * Start monitoring for connection loss
     * If no successful heartbeat for 5 minutes, show warning
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
        // Connection lost for 5 minutes - show warning but DON'T clear screen_id
        console.warn('Connection lost for 5 minutes, showing warning...')
        this.status = 'error'
        this.errorMessage = 'Connection lost for 5 minutes. Please check your network connection.'
      }
    },

    /**
     * Show an on-screen overlay message (used by display_message command)
     */
    showOverlay(message, durationMs = 10000) {
      // Clear any existing timer
      if (this.overlayTimer) {
        clearTimeout(this.overlayTimer)
        this.overlayTimer = null
      }

      this.overlayMessage = message
      this.overlayVisible = true

      // Auto-hide after duration
      this.overlayTimer = setTimeout(() => {
        this.clearOverlay()
      }, durationMs)
    },

    /**
     * Clear overlay message
     */
    clearOverlay() {
      if (this.overlayTimer) {
        clearTimeout(this.overlayTimer)
        this.overlayTimer = null
      }
      this.overlayVisible = false
      this.overlayMessage = null
    },

    /**
     * Start polling for template updates and sending heartbeats
     * Polls every 30 seconds if no template, or every 5 minutes if template exists
     * Sends heartbeat every 30 seconds
     * Commands are polled every 5 seconds for fast execution
     */
    startPolling() {
      // Verify screen_id exists before starting polling
      const storedScreenId = localStorage.getItem('player_screen_id')
      
      if (!storedScreenId) {
        console.error('[PlayerStore] Cannot start polling: screen not paired')
        this.status = 'error'
        this.errorMessage = 'Screen not paired. Please pair your screen first.'
        return
      }
      
      // Verify playerAPI is available
      if (!playerAPI) {
        console.error('[PlayerStore] playerAPI not available')
        this.status = 'error'
        this.errorMessage = 'Player API not initialized'
        return
      }
      
      // Re-set screen_id to ensure it's in playerAPI
      try {
        playerAPI.setScreenId(storedScreenId)
        console.log('[PlayerStore] Screen ID re-set in playerAPI after verification')
      } catch (error) {
        console.error('[PlayerStore] Failed to set screen_id in playerAPI:', error)
        this.status = 'error'
        this.errorMessage = 'Failed to configure player API'
        return
      }
      
      console.log('[PlayerStore] Starting polling with screen_id verified')
      
      if (this.pollingInterval) {
        clearInterval(this.pollingInterval)
        this.pollingInterval = null
      }

      // Initialize last successful heartbeat timestamp
      this.lastSuccessfulHeartbeat = Date.now()

      // Send initial heartbeat with a small delay to ensure screen_id is fully set
      setTimeout(() => {
        this.sendHeartbeat().catch(error => {
          console.warn('[PlayerStore] Initial heartbeat failed, will retry:', error)
          // Retry after 5 seconds
          setTimeout(() => {
            this.sendHeartbeat().catch(err => {
              console.error('[PlayerStore] Retry heartbeat also failed:', err)
              // Check connection loss even on retry failure
              this.checkConnectionLoss()
            })
          }, 5000)
        })
      }, 500) // Small delay to ensure everything is initialized

      // Start heartbeat interval (every 30 seconds)
      this.heartbeatInterval = setInterval(() => {
        this.sendHeartbeat().catch(error => {
          console.error('Heartbeat failed:', error)
          // Check connection loss on each failure
          this.checkConnectionLoss()
        })
      }, 30000) // 30 seconds

      // Start command polling interval (every 5 seconds for fast command execution)
      // Also fetch commands immediately (don't wait)
      console.log('[PlayerStore] Starting command polling (every 5 seconds for fast execution)')
      
      // Fetch commands immediately
      this.fetchAndExecuteCommands().catch(error => {
        console.error('[PlayerStore] Initial command fetch failed:', error)
        // Don't break the player if command polling fails
      })
      
      // Poll every 5 seconds for fast command execution
      this.commandPollingInterval = setInterval(() => {
        console.log('[PlayerStore] Fetching pending commands...')
        this.fetchAndExecuteCommands().catch(error => {
          console.error('[PlayerStore] Command polling failed:', error)
          // Don't break the player if command polling fails
        })
      }, 5000) // 5 seconds - fast polling for immediate command execution

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
     * Fetch pending commands and execute them
     */
    async fetchAndExecuteCommands() {
      // Verify screen_id exists before fetching commands
      const storedScreenId = localStorage.getItem('player_screen_id')
      if (!storedScreenId) {
        console.warn('[PlayerStore] Cannot fetch commands: screen_id not found in localStorage')
        return
      }
      
      // Verify screen_id is set in playerAPI
      const currentScreenId = playerAPI.getScreenId()
      if (currentScreenId !== storedScreenId) {
        console.warn('[PlayerStore] Screen ID mismatch, updating playerAPI', {
          stored: storedScreenId,
          current: currentScreenId
        })
        playerAPI.setScreenId(storedScreenId)
      }
      
      console.log('[PlayerStore] Fetching pending commands...', { screenId: storedScreenId })
      try {
        const response = await playerAPI.fetchPendingCommands()
        
        console.log('[PlayerStore] Command fetch response:', {
          status: response.status,
          count: response.count || 0,
          hasCommands: !!(response.commands && response.commands.length > 0)
        })
        
        if (response.status === 'success' && response.commands && response.commands.length > 0) {
          console.log(`[PlayerStore] Found ${response.commands.length} pending commands - executing immediately`, {
            commands: response.commands.map(c => ({ id: c.id, type: c.type, name: c.name }))
          })
          
          // Execute each command sequentially for reliability
          // Commands are executed immediately when fetched (fast polling ensures quick execution)
          for (const command of response.commands) {
            await this.executeCommand(command)
          }
        } else {
          console.log('[PlayerStore] No pending commands found')
        }
      } catch (error) {
        console.error('[PlayerStore] Error fetching commands:', error)
        // Don't throw - command polling failures shouldn't break the player
      }
    },

    /**
     * Execute a command
     */
    async executeCommand(command) {
      const { id, type, payload } = command
      
      console.log(`[PlayerStore] Executing command ${id} of type ${type}`, { 
        commandId: id,
        commandType: type,
        payload: payload 
      })
      
      try {
        let success = false
        let errorMessage = ''
        
        // Execute based on command type
        switch (type) {
          case 'restart':
            // Reload the page
            console.log('[PlayerStore] Executing restart command - reloading page in 1 second')
            success = true
            // Update status first, then reload
            await playerAPI.updateCommandStatus(id, 'done', '', {})
            setTimeout(() => {
              window.location.reload()
            }, 1000)
            return // Exit early since we're reloading
            
          case 'refresh':
            // Refresh the template
            console.log('[PlayerStore] Executing refresh command - fetching template')
            success = true
            await this.fetchTemplate()
            break
            
          case 'change_template':
            // Change to a different template (template_id in payload)
            if (payload && payload.template_id) {
              console.log('[PlayerStore] Executing change_template command', { template_id: payload.template_id })
              // Force template refresh - the next poll will get the new template
              success = true
              await this.fetchTemplate()
            } else {
              errorMessage = 'Template ID not provided in payload'
              console.warn('[PlayerStore] change_template command missing template_id in payload')
            }
            break
            
          case 'display_message':
            // Display a message (could show a modal or overlay)
            if (payload && payload.message) {
              console.log('[PlayerStore] Executing display_message command:', payload.message)
              // Show overlay on screen
              const durationSeconds = payload.duration || 10
              const durationMs = Math.max(1000, durationSeconds * 1000)
              this.showOverlay(payload.message, durationMs)
              success = true
            } else {
              errorMessage = 'Message not provided in payload'
              console.warn('[PlayerStore] display_message command missing message in payload')
            }
            break
            
          case 'sync_content':
            // Sync content files (content_ids in payload, or all if empty)
            console.log('[PlayerStore] Executing sync_content command', { content_ids: payload?.content_ids })
            // Content sync would typically be handled by the backend
            // For now, just mark as done
            success = true
            break
            
          case 'custom':
            // Execute custom JavaScript (payload.script)
            if (payload && payload.script) {
              try {
                // WARNING: Executing arbitrary JavaScript is a security risk
                // In production, you should validate and sanitize the script
                // For now, we'll just log it
                console.warn('[PlayerStore] Custom script execution requested (not executed for security):', payload.script)
                success = true
                errorMessage = 'Custom script execution not implemented for security reasons'
              } catch (e) {
                errorMessage = `Script execution error: ${e.message}`
                console.error('[PlayerStore] Custom script execution error:', e)
              }
            } else {
              errorMessage = 'Script not provided in payload'
              console.warn('[PlayerStore] custom command missing script in payload')
            }
            break
            
          default:
            errorMessage = `Unknown command type: ${type}`
            console.warn(`[PlayerStore] Unknown command type: ${type}`)
        }
        
        // Update command status on backend (unless it was restart which already updated)
        const status = success ? 'done' : 'failed'
        console.log(`[PlayerStore] Updating command ${id} status to ${status}`, { errorMessage })
        await playerAPI.updateCommandStatus(id, status, errorMessage, {})
        
        console.log(`[PlayerStore] Command ${id} execution completed with status: ${status}`, { 
          errorMessage: errorMessage || 'none' 
        })
        
      } catch (error) {
        console.error(`[PlayerStore] Error executing command ${id}:`, error)
        
        // Update command status as failed
        try {
          await playerAPI.updateCommandStatus(id, 'failed', error.message || 'Command execution error', {})
          console.log(`[PlayerStore] Command ${id} marked as failed due to error`)
        } catch (updateError) {
          console.error('[PlayerStore] Error updating command status:', updateError)
        }
      }
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
      
      if (this.commandPollingInterval) {
        clearInterval(this.commandPollingInterval)
        this.commandPollingInterval = null
      }
      
      if (this.retryTimer) {
        clearInterval(this.retryTimer)
        this.retryTimer = null
      }
      
      if (this.connectionLostTimer) {
        clearTimeout(this.connectionLostTimer)
        this.connectionLostTimer = null
      }

      if (this.overlayTimer) {
        clearTimeout(this.overlayTimer)
        this.overlayTimer = null
      }

      this.overlayVisible = false
      this.overlayMessage = null
    }
  }
})
