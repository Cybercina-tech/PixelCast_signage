import { defineStore } from 'pinia'
import { templatesAPI, layersAPI, widgetsAPI } from '../services/api'
import { smartUpdateObject } from '../utils/deepCompare'

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
    async duplicateTemplate(templateId) {
      this.loading = true
      this.error = null
      try {
        // Fetch the full template details
        // If template is already in store, use it; otherwise fetch
        let originalTemplate = this.templates.find(t => t.id === templateId)
        if (!originalTemplate) {
          originalTemplate = await this.fetchTemplate(templateId)
        }
        
        // Create duplicate with "Copy of" naming
        const duplicateData = {
          name: `Copy of ${originalTemplate.name}`,
          description: originalTemplate.description || '',
          width: originalTemplate.width,
          height: originalTemplate.height,
          orientation: originalTemplate.orientation || 'landscape',
          is_active: false, // Duplicates start as inactive
          config_json: originalTemplate.config_json || {},
        }
        
        const newTemplate = await this.createTemplate(duplicateData)
        
        // Note: Layers and widgets are not duplicated automatically
        // User can manually recreate them in the template editor if needed
        
        return newTemplate
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
        console.log(`DEBUG [activateOnScreen]: Starting activation - templateId: ${templateId}, screenId: ${screenId}, syncContent: ${syncContent}`)
        
        const response = await templatesAPI.activateOnScreen(templateId, {
          screen_id: screenId,
          sync_content: syncContent,
        })
        
        // DEBUG: Log activation response
        console.log('DEBUG [activateOnScreen]: Activation Response:', response.data)
        console.log('DEBUG [activateOnScreen]: Response screen data:', response.data?.screen)
        console.log('DEBUG [activateOnScreen]: Response screen.active_template:', response.data?.screen?.active_template)
        
        // CRITICAL: Update screen in screens store immediately if response includes screen data
        // This ensures UI updates without waiting for next fetch
        if (response.data && response.data.screen) {
          console.log('DEBUG [activateOnScreen]: Updating Screen Store with:', response.data.screen)
          console.log('DEBUG [activateOnScreen]: Screen active_template in response:', response.data.screen.active_template)
          
          // Import screens store to update screen data (lazy import to avoid circular dependency)
          const { useScreensStore } = await import('@/stores/screens')
          const screensStore = useScreensStore()
          
          // Update screen in store with returned data
          const updatedScreen = response.data.screen
          const index = screensStore.screens.findIndex(s => s.id === screenId)
          
          console.log('DEBUG [activateOnScreen]: Screen index in store:', index)
          console.log('DEBUG [activateOnScreen]: Current screen in store:', index !== -1 ? screensStore.screens[index] : 'NOT FOUND')
          console.log('DEBUG [activateOnScreen]: Current screen.active_template in store:', index !== -1 ? screensStore.screens[index]?.active_template : 'N/A')
          
          if (index !== -1) {
            // Use smart update to preserve references if unchanged
            const oldScreen = screensStore.screens[index]
            screensStore.screens[index] = smartUpdateObject(oldScreen, updatedScreen)
            console.log('DEBUG [activateOnScreen]: Screen updated in store. New active_template:', screensStore.screens[index]?.active_template)
          } else {
            // Screen not in list, add it
            screensStore.screens.push(updatedScreen)
            console.log('DEBUG [activateOnScreen]: Screen added to store')
          }
          
          // Update currentScreen if it's the one being updated
          if (screensStore.currentScreen?.id === screenId) {
            console.log('DEBUG [activateOnScreen]: Updating currentScreen')
            console.log('DEBUG [activateOnScreen]: currentScreen.active_template BEFORE:', screensStore.currentScreen?.active_template)
            screensStore.currentScreen = smartUpdateObject(screensStore.currentScreen, updatedScreen)
            console.log('DEBUG [activateOnScreen]: currentScreen.active_template AFTER:', screensStore.currentScreen?.active_template)
          }
        } else {
          console.warn('DEBUG [activateOnScreen]: Response does not include screen data!')
        }
        
        return response.data
      } catch (error) {
        console.error('DEBUG [activateOnScreen]: Activation error:', error)
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
        // Only store layers for the current template to avoid mixing layers from different templates
        const layers = response.data.results || response.data || []
        // Filter to ensure only layers for this template are stored
        this.layers = layers.filter(layer => layer.template === templateId || layer.template?.id === templateId)
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
        const newLayer = response.data
        // Only add if it belongs to the current template being viewed
        const templateId = data.template || newLayer.template || newLayer.template?.id
        if (templateId) {
          // Check if this layer belongs to the template we're currently viewing
          const currentTemplateId = this.currentTemplate?.id
          if (!currentTemplateId || currentTemplateId === templateId) {
            this.layers.push(newLayer)
          }
        } else {
          // If no template specified, add it anyway (shouldn't happen)
          this.layers.push(newLayer)
        }
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
        const widgets = response.data.results || response.data || []
        // Only store widgets for the current layer to avoid mixing widgets from different layers
        this.widgets = widgets.filter(widget => widget.layer === layerId || widget.layer?.id === layerId)
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
        const newWidget = response.data
        // Only add if it belongs to the current layer being viewed
        const layerId = data.layer || newWidget.layer || newWidget.layer?.id
        if (layerId) {
          // Check if this widget belongs to a layer we're currently viewing
          const currentLayerIds = this.layers.map(l => l.id)
          if (currentLayerIds.includes(layerId)) {
            this.widgets.push(newWidget)
          }
        } else {
          // If no layer specified, add it anyway (shouldn't happen)
          this.widgets.push(newWidget)
        }
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
