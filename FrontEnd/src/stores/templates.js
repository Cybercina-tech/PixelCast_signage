import { defineStore } from 'pinia'
import { templatesAPI, layersAPI, widgetsAPI } from '../services/api'

export const useTemplatesStore = defineStore('templates', {
  state: () => ({
    templates: [],
    currentTemplate: null,
    layers: [],
    widgets: [],
    loading: false,
    error: null,
    filters: {
      search: '',
      is_active: null,
    },
  }),
  getters: {
    activeTemplates: (state) => state.templates.filter(t => t.is_active),
    filteredTemplates: (state) => {
      let filtered = state.templates
      if (state.filters.search) {
        const search = state.filters.search.toLowerCase()
        filtered = filtered.filter(t => 
          t.name?.toLowerCase().includes(search) ||
          t.description?.toLowerCase().includes(search)
        )
      }
      if (state.filters.is_active !== null) {
        filtered = filtered.filter(t => t.is_active === state.filters.is_active)
      }
      return filtered
    },
  },
  actions: {
    async fetchTemplates(params = {}) {
      this.loading = true
      this.error = null
      try {
        const response = await templatesAPI.list({ ...this.filters, ...params })
        this.templates = response.data.results || response.data || []
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || error.response?.data?.message || error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    async fetchTemplate(id) {
      this.loading = true
      this.error = null
      try {
        const response = await templatesAPI.detail(id)
        this.currentTemplate = response.data
        // Update in list if exists
        const index = this.templates.findIndex(t => t.id === id)
        if (index !== -1) {
          this.templates[index] = response.data
        }
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || error.response?.data?.message || error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    async createTemplate(data) {
      this.loading = true
      this.error = null
      try {
        const response = await templatesAPI.create(data)
        this.templates.push(response.data)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || error.response?.data?.message || error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    async updateTemplate(id, data) {
      this.loading = true
      this.error = null
      try {
        const response = await templatesAPI.update(id, data)
        const index = this.templates.findIndex(t => t.id === id)
        if (index !== -1) {
          this.templates[index] = response.data
        }
        if (this.currentTemplate?.id === id) {
          this.currentTemplate = response.data
        }
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || error.response?.data?.message || error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    async deleteTemplate(id) {
      this.loading = true
      this.error = null
      try {
        await templatesAPI.delete(id)
        this.templates = this.templates.filter(t => t.id !== id)
        if (this.currentTemplate?.id === id) {
          this.currentTemplate = null
        }
      } catch (error) {
        this.error = error.response?.data?.detail || error.response?.data?.message || error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    async activateOnScreen(templateId, screenId, syncContent = true) {
      this.loading = true
      this.error = null
      try {
        const response = await templatesAPI.activateOnScreen(templateId, {
          screen_id: screenId,
          sync_content: syncContent,
        })
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || error.response?.data?.message || error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    // Layers
    async fetchLayers(templateId, params = {}) {
      this.loading = true
      this.error = null
      try {
        const response = await layersAPI.list({ template: templateId, ...params })
        this.layers = response.data.results || response.data || []
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || error.response?.data?.message || error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    async createLayer(data) {
      this.loading = true
      this.error = null
      try {
        const response = await layersAPI.create(data)
        this.layers.push(response.data)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || error.response?.data?.message || error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    async updateLayer(id, data) {
      this.loading = true
      this.error = null
      try {
        const response = await layersAPI.update(id, data)
        const index = this.layers.findIndex(l => l.id === id)
        if (index !== -1) {
          this.layers[index] = response.data
        }
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || error.response?.data?.message || error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    async deleteLayer(id) {
      this.loading = true
      this.error = null
      try {
        await layersAPI.delete(id)
        this.layers = this.layers.filter(l => l.id !== id)
      } catch (error) {
        this.error = error.response?.data?.detail || error.response?.data?.message || error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    // Widgets
    async fetchWidgets(layerId, params = {}) {
      this.loading = true
      this.error = null
      try {
        const response = await widgetsAPI.list({ layer: layerId, ...params })
        this.widgets = response.data.results || response.data || []
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || error.response?.data?.message || error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    async createWidget(data) {
      this.loading = true
      this.error = null
      try {
        const response = await widgetsAPI.create(data)
        this.widgets.push(response.data)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || error.response?.data?.message || error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    async updateWidget(id, data) {
      this.loading = true
      this.error = null
      try {
        const response = await widgetsAPI.update(id, data)
        const index = this.widgets.findIndex(w => w.id === id)
        if (index !== -1) {
          this.widgets[index] = response.data
        }
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || error.response?.data?.message || error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    async deleteWidget(id) {
      this.loading = true
      this.error = null
      try {
        await widgetsAPI.delete(id)
        this.widgets = this.widgets.filter(w => w.id !== id)
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
