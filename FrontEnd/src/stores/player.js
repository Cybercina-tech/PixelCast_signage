import { defineStore } from 'pinia'
import playerAPI from '@/services/playerApi'
import { collectSystemInfo } from '@/composables/useSystemInfo'

const STORAGE_KEYS = {
  screenId: 'player_screen_id',
  deviceToken: 'player_device_token',
  isPaired: 'player_is_paired',
  pairedAt: 'player_paired_at',
}

export const usePlayerStore = defineStore('player', {
  state: () => ({
    status: 'loading', // loading | success | no_template | error | unpaired
    template: null,
    errorMessage: null,
    retryCountdown: 0,
    overlayMessage: null,
    overlayVisible: false,
    overlayTimer: null,
    pollingInterval: null,
    heartbeatInterval: null,
    commandPollingInterval: null,
    retryTimer: null,
    lastSuccessfulHeartbeat: null,
    connectionLostTimer: null,
  }),

  actions: {
    // ── Device identity helpers ────────────────────────────────────

    saveDeviceIdentity(screenId, deviceToken) {
      try {
        localStorage.setItem(STORAGE_KEYS.screenId, screenId)
        localStorage.setItem(STORAGE_KEYS.deviceToken, deviceToken)
        localStorage.setItem(STORAGE_KEYS.isPaired, 'true')
        localStorage.setItem(STORAGE_KEYS.pairedAt, new Date().toISOString())
      } catch (e) {
        console.error('[PlayerStore] Failed to save device identity:', e)
      }
      playerAPI.setDeviceIdentity({ screenId, deviceToken })
    },

    loadDeviceIdentity() {
      const screenId = localStorage.getItem(STORAGE_KEYS.screenId)
      const deviceToken = localStorage.getItem(STORAGE_KEYS.deviceToken)
      if (screenId && deviceToken) {
        playerAPI.setDeviceIdentity({ screenId, deviceToken })
        return true
      }
      return false
    },

    hasDeviceIdentity() {
      return !!(
        localStorage.getItem(STORAGE_KEYS.screenId) &&
        localStorage.getItem(STORAGE_KEYS.deviceToken)
      )
    },

    clearDeviceIdentity() {
      for (const key of Object.values(STORAGE_KEYS)) {
        try { localStorage.removeItem(key) } catch (_) { /* ignore */ }
      }
      // Also clean up legacy keys
      for (const k of ['player_auth_token', 'player_secret_key']) {
        try { localStorage.removeItem(k) } catch (_) { /* ignore */ }
      }
      playerAPI.clearDeviceIdentity()
    },

    // Legacy alias expected by WebPlayer.vue
    clearCredentials() {
      this.clearDeviceIdentity()
    },

    // ── Initialization ─────────────────────────────────────────────

    async initialize() {
      try {
        if (!this.loadDeviceIdentity()) {
          const error = new Error('Screen not paired. Please pair your screen first.')
          error.code = 'SCREEN_NOT_PAIRED'
          throw error
        }
        await this.fetchTemplate()
      } catch (error) {
        console.error('[PlayerStore] Initialization error:', error)
        this.status = 'error'
        this.errorMessage = error.message || 'Initialization failed'

        if (
          error.code === 'SCREEN_NOT_PAIRED' ||
          error.code === 'DEVICE_NOT_PAIRED' ||
          error.code === 'DEVICE_AUTH_FAILED'
        ) {
          this.status = 'unpaired'
          this.errorMessage = 'Please pair your screen first to continue.'
        }
        throw error
      }
    },

    // ── Template ───────────────────────────────────────────────────

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

        if (error.code === 'DEVICE_AUTH_FAILED' || error.status === 401) {
          this.status = 'unpaired'
          this.errorMessage = 'Device token revoked or invalid. Please re-pair.'
          this.stopPolling()
          return
        }

        if (error.status === 404) {
          this.status = 'unpaired'
          this.errorMessage = 'Screen not found. Please re-pair.'
          this.stopPolling()
          return
        }

        this.status = 'error'
        this.errorMessage = error.message || 'Failed to fetch template'
        this.startRetryCountdown()
      }
    },

    startRetryCountdown() {
      this.retryCountdown = 30
      if (this.retryTimer) clearInterval(this.retryTimer)
      this.retryTimer = setInterval(() => {
        this.retryCountdown--
        if (this.retryCountdown <= 0) {
          clearInterval(this.retryTimer)
          this.retryTimer = null
          this.fetchTemplate()
        }
      }, 1000)
    },

    // ── Heartbeat ──────────────────────────────────────────────────

    async sendHeartbeat() {
      try {
        const systemInfo = collectSystemInfo()
        const response = await playerAPI.sendHeartbeat(systemInfo)
        this.lastSuccessfulHeartbeat = Date.now()
        if (this.connectionLostTimer) {
          clearTimeout(this.connectionLostTimer)
          this.connectionLostTimer = null
        }
        this.startConnectionLossMonitoring()
        return response
      } catch (error) {
        console.error('Heartbeat error:', error)

        if (error.code === 'DEVICE_AUTH_FAILED' || error.status === 401) {
          this.status = 'unpaired'
          this.errorMessage = 'Device token revoked. Returning to pairing.'
          this.stopPolling()
          throw error
        }

        this.checkConnectionLoss()
        throw error
      }
    },

    startConnectionLossMonitoring() {
      if (this.connectionLostTimer) clearTimeout(this.connectionLostTimer)
      this.connectionLostTimer = setTimeout(() => this.checkConnectionLoss(), 300000)
    },

    checkConnectionLoss() {
      if (!this.lastSuccessfulHeartbeat) {
        this.startConnectionLossMonitoring()
        return
      }
      if (Date.now() - this.lastSuccessfulHeartbeat >= 300000) {
        this.status = 'error'
        this.errorMessage = 'Connection lost for 5 minutes. Please check your network.'
      }
    },

    // ── Overlay ────────────────────────────────────────────────────

    showOverlay(message, durationMs = 10000) {
      if (this.overlayTimer) { clearTimeout(this.overlayTimer); this.overlayTimer = null }
      this.overlayMessage = message
      this.overlayVisible = true
      this.overlayTimer = setTimeout(() => this.clearOverlay(), durationMs)
    },

    clearOverlay() {
      if (this.overlayTimer) { clearTimeout(this.overlayTimer); this.overlayTimer = null }
      this.overlayVisible = false
      this.overlayMessage = null
    },

    // ── Polling ────────────────────────────────────────────────────

    startPolling() {
      if (!this.hasDeviceIdentity()) {
        this.status = 'unpaired'
        this.errorMessage = 'Screen not paired.'
        return
      }
      // Ensure API has identity loaded
      this.loadDeviceIdentity()

      if (this.pollingInterval) { clearInterval(this.pollingInterval); this.pollingInterval = null }

      this.lastSuccessfulHeartbeat = Date.now()

      // Initial heartbeat (small delay for init)
      setTimeout(() => {
        this.sendHeartbeat().catch(() => {
          setTimeout(() => this.sendHeartbeat().catch(() => this.checkConnectionLoss()), 5000)
        })
      }, 500)

      // Heartbeat every 30s
      this.heartbeatInterval = setInterval(() => {
        this.sendHeartbeat().catch(() => this.checkConnectionLoss())
      }, 30000)

      // Command polling every 5s
      this.fetchAndExecuteCommands().catch(() => {})
      this.commandPollingInterval = setInterval(() => {
        this.fetchAndExecuteCommands().catch(() => {})
      }, 5000)

      // Template polling
      const poll = () => {
        const interval = this.status === 'no_template' ? 30000 : 300000
        this.pollingInterval = setInterval(() => {
          this.fetchTemplate().then(() => {
            if (this.pollingInterval) {
              const newInterval = this.status === 'no_template' ? 30000 : 300000
              if (newInterval !== interval) {
                clearInterval(this.pollingInterval)
                this.pollingInterval = null
                poll()
              }
            }
          })
        }, interval)
      }
      poll()
    },

    // ── Commands ───────────────────────────────────────────────────

    async fetchAndExecuteCommands() {
      if (!this.hasDeviceIdentity()) return
      try {
        const response = await playerAPI.fetchPendingCommands()
        if (response.status === 'success' && response.commands?.length > 0) {
          for (const command of response.commands) {
            await this.executeCommand(command)
          }
        }
      } catch (error) {
        if (error.code === 'DEVICE_AUTH_FAILED' || error.status === 401) {
          this.status = 'unpaired'
          this.stopPolling()
        }
      }
    },

    async executeCommand(command) {
      const { id, type, payload } = command
      try {
        let success = false
        let errorMessage = ''

        switch (type) {
          case 'restart':
            success = true
            await playerAPI.updateCommandStatus(id, 'done', '', {})
            setTimeout(() => window.location.reload(), 1000)
            return

          case 'refresh':
            success = true
            await this.fetchTemplate()
            break

          case 'change_template':
            if (payload?.template_id) {
              success = true
              await this.fetchTemplate()
            } else {
              errorMessage = 'Template ID not provided in payload'
            }
            break

          case 'display_message':
            if (payload?.message) {
              const ms = Math.max(1000, (payload.duration || 10) * 1000)
              this.showOverlay(payload.message, ms)
              success = true
            } else {
              errorMessage = 'Message not provided in payload'
            }
            break

          case 'sync_content':
            success = true
            break

          case 'unpair':
            this.clearDeviceIdentity()
            success = true
            await playerAPI.updateCommandStatus(id, 'done', '', {})
            window.location.reload()
            return

          case 'custom':
            success = true
            errorMessage = 'Custom script execution not implemented for security'
            break

          default:
            errorMessage = `Unknown command type: ${type}`
        }

        await playerAPI.updateCommandStatus(id, success ? 'done' : 'failed', errorMessage, {})
      } catch (error) {
        try {
          await playerAPI.updateCommandStatus(id, 'failed', error.message || 'Execution error', {})
        } catch (_) { /* ignore */ }
      }
    },

    stopPolling() {
      for (const key of ['pollingInterval', 'heartbeatInterval', 'commandPollingInterval', 'retryTimer']) {
        if (this[key]) { clearInterval(this[key]); this[key] = null }
      }
      if (this.connectionLostTimer) { clearTimeout(this.connectionLostTimer); this.connectionLostTimer = null }
      if (this.overlayTimer) { clearTimeout(this.overlayTimer); this.overlayTimer = null }
      this.overlayVisible = false
      this.overlayMessage = null
    },
  },
})
