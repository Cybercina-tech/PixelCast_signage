import { defineStore } from 'pinia'
import { screensAPI } from '../services/api'

export const useScreensStore = defineStore('screens', {
  state: () => ({
    screens: [],
    currentScreen: null,
    loading: false,
    error: null,
    filters: {
      search: '',
      status: null,
      organization: null,
    },
  }),
  getters: {
    onlineScreens: (state) => state.screens.filter(s => s.is_online),
    offlineScreens: (state) => state.screens.filter(s => !s.is_online),
    filteredScreens: (state) => {
      let filtered = state.screens
      if (state.filters.search) {
        const search = state.filters.search.toLowerCase()
        filtered = filtered.filter(s => 
          s.name?.toLowerCase().includes(search) ||
          s.device_id?.toLowerCase().includes(search) ||
          s.location?.toLowerCase().includes(search)
        )
      }
      if (state.filters.status === 'online') {
        filtered = filtered.filter(s => s.is_online)
      } else if (state.filters.status === 'offline') {
        filtered = filtered.filter(s => !s.is_online)
      }
      return filtered
    },
  },
  actions: {
    async fetchScreens(params = {}) {
      this.loading = true
      this.error = null
      try {
        const response = await screensAPI.list({ ...this.filters, ...params })
        this.screens = response.data.results || response.data || []
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    async fetchScreen(id) {
      this.loading = true
      this.error = null
      try {
        const response = await screensAPI.detail(id)
        this.currentScreen = response.data
        // Update in list if exists
        const index = this.screens.findIndex(s => s.id === id)
        if (index !== -1) {
          this.screens[index] = response.data
        }
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    async createScreen(data) {
      this.loading = true
      this.error = null
      try {
        const response = await screensAPI.create(data)
        this.screens.push(response.data)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    async updateScreen(id, data) {
      this.loading = true
      this.error = null
      try {
        const response = await screensAPI.update(id, data)
        const index = this.screens.findIndex(s => s.id === id)
        if (index !== -1) {
          this.screens[index] = response.data
        }
        if (this.currentScreen?.id === id) {
          this.currentScreen = response.data
        }
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    async deleteScreen(id) {
      this.loading = true
      this.error = null
      try {
        await screensAPI.delete(id)
        this.screens = this.screens.filter(s => s.id !== id)
        if (this.currentScreen?.id === id) {
          this.currentScreen = null
        }
      } catch (error) {
        this.error = error.response?.data?.detail || error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    async sendHeartbeat(id, data) {
      this.loading = true
      this.error = null
      try {
        const response = await screensAPI.heartbeat(id, data)
        // Update screen status
        const index = this.screens.findIndex(s => s.id === id)
        if (index !== -1) {
          this.screens[index] = { ...this.screens[index], ...response.data }
        }
        if (this.currentScreen?.id === id) {
          this.currentScreen = { ...this.currentScreen, ...response.data }
        }
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || error.response?.data?.message || error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    setFilters(filters) {
      this.filters = { ...this.filters, ...filters }
    },
    clearFilters() {
      this.filters = { search: '', status: null, organization: null }
    },
  },
})
