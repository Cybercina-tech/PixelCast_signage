import { defineStore } from 'pinia'
import { authAPI, usersAPI } from '../services/api'
import { normalizeApiError } from '../utils/apiError'

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
    }
  },
  actions: {
    async login(credentials) {
      this.loading = true
      this.error = null
      try {
        const response = await authAPI.login(credentials)
        // Backend returns: {status: 'success', user: {...}, tokens: {refresh, access}}
        if (response.data.tokens) {
          this.token = response.data.tokens.access
          this.refreshToken = response.data.tokens.refresh
          localStorage.setItem('auth_token', this.token)
          localStorage.setItem('refresh_token', this.refreshToken)
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
    async logout() {
      try {
        const refreshToken = this.refreshToken || localStorage.getItem('refresh_token')
        if (refreshToken) {
          await authAPI.logout({ refresh_token: refreshToken })
        }
      } catch (error) {
        // Ignore errors on logout - clear local state anyway
        console.error('Logout error:', error)
      } finally {
        this.token = null
        this.refreshToken = null
        this.user = null
        this.isAuthenticated = false
        localStorage.removeItem('auth_token')
        localStorage.removeItem('refresh_token')
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
          this.token = null
          this.refreshToken = null
          this.user = null
          this.isAuthenticated = false
          localStorage.removeItem('auth_token')
          localStorage.removeItem('refresh_token')
        }
        throw error
      }
    },
    async refreshAccessToken() {
      if (!this.refreshToken) {
        throw new Error('No refresh token available')
      }
      try {
        const response = await authAPI.refreshToken(this.refreshToken)
        if (response.data.access) {
          this.token = response.data.access
          localStorage.setItem('auth_token', this.token)
          if (response.data.refresh) {
            this.refreshToken = response.data.refresh
            localStorage.setItem('refresh_token', this.refreshToken)
          }
        }
        return this.token
      } catch (error) {
        // Refresh failed, logout user
        await this.logout()
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
        } catch (error) {
          // Token invalid, clear it
          this.token = null
          this.refreshToken = null
          this.isAuthenticated = false
          localStorage.removeItem('auth_token')
          localStorage.removeItem('refresh_token')
        }
      }
      this.initialized = true
    },
  },
})
