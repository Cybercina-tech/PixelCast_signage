import { defineStore } from 'pinia'
import { contentsAPI } from '../services/api'

export const useContentStore = defineStore('content', {
  state: () => ({
    contents: [],
    currentContent: null,
    loading: false,
    error: null,
    filters: {
      search: '',
      type: null,
      download_status: null,
      widget: null,
    },
  }),
  getters: {
    downloadedContents: (state) => state.contents.filter(c => c.downloaded),
    pendingContents: (state) => state.contents.filter(c => !c.downloaded && c.download_status === 'pending'),
    failedContents: (state) => state.contents.filter(c => c.download_status === 'failed'),
    filteredContents: (state) => {
      let filtered = state.contents
      if (state.filters.search) {
        const search = state.filters.search.toLowerCase()
        filtered = filtered.filter(c => 
          c.name?.toLowerCase().includes(search) ||
          c.description?.toLowerCase().includes(search)
        )
      }
      if (state.filters.type) {
        filtered = filtered.filter(c => c.type === state.filters.type)
      }
      if (state.filters.download_status) {
        filtered = filtered.filter(c => c.download_status === state.filters.download_status)
      }
      if (state.filters.widget) {
        filtered = filtered.filter(c => c.widget === state.filters.widget)
      }
      return filtered
    },
  },
  actions: {
    async fetchContents(params = {}) {
      this.loading = true
      this.error = null
      try {
        const response = await contentsAPI.list({ ...this.filters, ...params })
        this.contents = response.data.results || response.data || []
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || error.response?.data?.message || error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    async fetchContent(id) {
      this.loading = true
      this.error = null
      try {
        const response = await contentsAPI.detail(id)
        this.currentContent = response.data
        // Update in list if exists
        const index = this.contents.findIndex(c => c.id === id)
        if (index !== -1) {
          this.contents[index] = response.data
        }
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || error.response?.data?.message || error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    async createContent(data) {
      this.loading = true
      this.error = null
      try {
        const response = await contentsAPI.create(data)
        this.contents.push(response.data)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || error.response?.data?.message || error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    async updateContent(id, data) {
      this.loading = true
      this.error = null
      try {
        const response = await contentsAPI.update(id, data)
        const index = this.contents.findIndex(c => c.id === id)
        if (index !== -1) {
          this.contents[index] = response.data
        }
        if (this.currentContent?.id === id) {
          this.currentContent = response.data
        }
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || error.response?.data?.message || error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    async deleteContent(id) {
      this.loading = true
      this.error = null
      try {
        await contentsAPI.delete(id)
        this.contents = this.contents.filter(c => c.id !== id)
        if (this.currentContent?.id === id) {
          this.currentContent = null
        }
      } catch (error) {
        this.error = error.response?.data?.detail || error.response?.data?.message || error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    async uploadContent(id, file, additionalData = {}) {
      this.loading = true
      this.error = null
      try {
        const response = await contentsAPI.upload(id, file, additionalData)
        // Update content in list
        const index = this.contents.findIndex(c => c.id === id)
        if (index !== -1) {
          this.contents[index] = { ...this.contents[index], ...response.data }
        }
        if (this.currentContent?.id === id) {
          this.currentContent = { ...this.currentContent, ...response.data }
        }
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || error.response?.data?.message || error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    async downloadToScreen(contentId, screenId) {
      this.loading = true
      this.error = null
      try {
        const response = await contentsAPI.downloadToScreen(contentId, { screen_id: screenId })
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || error.response?.data?.message || error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    async retryDownload(contentId, screenId) {
      this.loading = true
      this.error = null
      try {
        const response = await contentsAPI.retryDownload(contentId, { screen_id: screenId })
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || error.response?.data?.message || error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    async getDownloadURL(contentId, expiration = null) {
      this.loading = true
      this.error = null
      try {
        const params = expiration ? { expiration } : {}
        const response = await contentsAPI.download(contentId, params)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || error.response?.data?.message || error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    async verifyIntegrity(contentId, file = null) {
      this.loading = true
      this.error = null
      try {
        const formData = file ? new FormData() : null
        if (formData) {
          formData.append('file', file)
        }
        const response = await contentsAPI.verifyIntegrity(contentId, formData || {})
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
  },
})
