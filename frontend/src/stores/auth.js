import { defineStore } from 'pinia'
import { authAPI, usersAPI, platformAPI } from '../services/api'
import { normalizeApiError } from '../utils/apiError'

const USER_INITIATED_LOGOUT_KEY = 'user_initiated_logout_at'

export const useAuthStore = defineStore('auth', {
  state: () => {
    const token = localStorage.getItem('auth_token')
    const refreshToken = localStorage.getItem('refresh_token')
    return {
      user: null,
      token,
      refreshToken,
      isAuthenticated: !!token,
      loading: false,
      error: null,
      initialized: false,
      /** Set when Developer is viewing the app as another user */
      impersonation: null,
    }
  },
  actions: {
    setTokens(accessToken, refreshToken = null) {
      this.token = accessToken || null
      if (refreshToken) {
        this.refreshToken = refreshToken
      }
      if (this.token) {
        localStorage.setItem('auth_token', this.token)
      } else {
        localStorage.removeItem('auth_token')
      }
      if (this.refreshToken) {
        localStorage.setItem('refresh_token', this.refreshToken)
      } else {
        localStorage.removeItem('refresh_token')
      }
      this.isAuthenticated = Boolean(this.token)
    },
    clearAuthState() {
      this.token = null
      this.refreshToken = null
      this.user = null
      this.isAuthenticated = false
      this.impersonation = null
      this.restriction = null
      localStorage.removeItem('auth_token')
      localStorage.removeItem('refresh_token')
      sessionStorage.removeItem('platform_admin_refresh')
    },
    async login(credentials) {
      this.loading = true
      this.error = null
      try {
        const response = await authAPI.login(credentials)
        if (response.data.status === '2fa_required') {
          return {
            needs2fa: true,
            twoFactorToken: response.data.two_factor_token,
          }
        }
        if (response.data.status === 'email_verification_required') {
          return {
            needsEmailVerification: true,
            verificationToken: response.data.verification_token,
            email: response.data.email,
          }
        }
        // Backend returns: {status: 'success', user: {...}, tokens: {refresh, access}}
        if (response.data.tokens) {
          this.setTokens(response.data.tokens.access, response.data.tokens.refresh)
        }
        
        // Set user info from response
        if (response.data.user) {
          this.user = response.data.user
        } else {
          // Fallback: fetch user info
          await this.fetchMe()
        }
        
        this.isAuthenticated = true
        return response.data
      } catch (error) {
        this.error = normalizeApiError(error).userMessage || 'Login failed. Please check your credentials.'
        throw error
      } finally {
        this.loading = false
      }
    },
    async completeEmailVerification({ verificationToken, code }) {
      this.loading = true
      this.error = null
      try {
        const response = await authAPI.emailVerificationConfirm({
          verification_token: verificationToken,
          code: String(code || '').trim(),
        })
        if (response.data.status === '2fa_required') {
          return {
            needs2fa: true,
            twoFactorToken: response.data.two_factor_token,
          }
        }
        if (response.data.tokens) {
          this.setTokens(response.data.tokens.access, response.data.tokens.refresh)
        }
        if (response.data.user) {
          this.user = response.data.user
        } else {
          await this.fetchMe()
        }
        this.isAuthenticated = true
        return response.data
      } catch (error) {
        this.error = normalizeApiError(error).userMessage || 'Verification failed.'
        throw error
      } finally {
        this.loading = false
      }
    },
    async complete2fa({ twoFactorToken, code }) {
      this.loading = true
      this.error = null
      try {
        const response = await authAPI.login2fa({
          two_factor_token: twoFactorToken,
          code: String(code || '').trim(),
        })
        if (response.data.tokens) {
          this.setTokens(response.data.tokens.access, response.data.tokens.refresh)
        }
        if (response.data.user) {
          this.user = response.data.user
        } else {
          await this.fetchMe()
        }
        this.isAuthenticated = true
        return response.data
      } catch (error) {
        this.error = normalizeApiError(error).userMessage || 'Invalid code.'
        throw error
      } finally {
        this.loading = false
      }
    },
    async logout({ skipServer = false, userInitiated = false } = {}) {
      try {
        if (userInitiated) {
          sessionStorage.setItem(USER_INITIATED_LOGOUT_KEY, String(Date.now()))
        }
        const refreshToken = this.refreshToken || localStorage.getItem('refresh_token')
        if (!skipServer && refreshToken) {
          await authAPI.logout({ refresh_token: refreshToken })
        }
      } catch (error) {
        // Ignore errors on logout - clear local state anyway
        console.error('Logout error:', error)
      } finally {
        this.clearAuthState()
        try {
          const { dashboardWebSocket } = await import('@/composables/useWebSocket')
          dashboardWebSocket.disconnect()
        } catch {
          /* WS module optional during tests */
        }
      }
    },
    async fetchMe() {
      try {
        const response = await usersAPI.me()
        this.user = response.data
        this.isAuthenticated = true
        return response.data
      } catch (error) {
        // If fetch fails, clear auth
        if (error.response?.status === 401 || error.response?.status === 403) {
          this.clearAuthState()
        }
        throw error
      }
    },
    async refreshAccessToken() {
      if (!this.refreshToken) {
        this.refreshToken = localStorage.getItem('refresh_token')
      }
      if (!this.refreshToken) {
        throw new Error('No refresh token available')
      }
      try {
        const response = await authAPI.refreshToken(this.refreshToken)
        if (response.data.access) {
          this.setTokens(response.data.access, response.data.refresh || this.refreshToken)
        }
        return this.token
      } catch (error) {
        // Refresh failed, logout user
        await this.logout({ skipServer: true })
        throw error
      }
    },
    async updateMe(data) {
      try {
        const response = await usersAPI.updateMe(data)
        this.user = response.data
        return response.data
      } catch (error) {
        throw error
      }
    },
    async startPlatformImpersonation(userId) {
      const adminRefresh = this.refreshToken || localStorage.getItem('refresh_token')
      const { data } = await platformAPI.impersonate(userId)
      if (adminRefresh) {
        sessionStorage.setItem('platform_admin_refresh', adminRefresh)
      }
      this.setTokens(data.tokens.access, data.tokens.refresh)
      this.impersonation = data.impersonation || { active: true }
      await this.fetchMe()
    },
    async stopPlatformImpersonation() {
      const adminRefresh = sessionStorage.getItem('platform_admin_refresh')
      if (!adminRefresh) {
        this.impersonation = null
        return
      }
      const { data } = await platformAPI.impersonateStop(adminRefresh)
      sessionStorage.removeItem('platform_admin_refresh')
      this.setTokens(data.tokens.access, data.tokens.refresh)
      this.impersonation = null
      await this.fetchMe()
    },
    async initialize() {
      // Initialize auth state on app startup
      if (this.initialized) return
      
      const token = localStorage.getItem('auth_token')
      if (token && !this.user) {
        try {
          this.token = token
          this.refreshToken = localStorage.getItem('refresh_token')
          await this.fetchMe()
          this.isAuthenticated = true
          if (sessionStorage.getItem('platform_admin_refresh')) {
            this.impersonation = { active: true }
          }
        } catch (error) {
          // Token invalid, clear it
          this.clearAuthState()
        }
      }
      this.initialized = true
    },
  },
})
