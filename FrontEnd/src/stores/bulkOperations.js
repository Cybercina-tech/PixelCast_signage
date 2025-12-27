/**
 * Bulk Operations Store
 * Manages bulk operations for multiple resources
 */
import { defineStore } from 'pinia'
import { bulkOperationsAPI } from '../services/api'
import { useNotificationStore } from './notification'

export const useBulkOperationsStore = defineStore('bulkOperations', {
  state: () => ({
    loading: false,
    error: null,
    lastResult: null,
  }),

  actions: {
    /**
     * Bulk delete screens
     */
    async bulkDeleteScreens(itemIds) {
      this.loading = true
      this.error = null
      const notifyStore = useNotificationStore()
      
      try {
        const response = await bulkOperationsAPI.screensDelete({ item_ids: itemIds })
        this.lastResult = response.data
        notifyStore.success(`Deleted ${response.data.success_count || 0} screens`)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || error.response?.data?.detail || error.message
        notifyStore.error('Failed to delete screens: ' + this.error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Bulk update screens
     */
    async bulkUpdateScreens(itemIds, updateData) {
      this.loading = true
      this.error = null
      const notifyStore = useNotificationStore()
      
      try {
        const response = await bulkOperationsAPI.screensUpdate({
          item_ids: itemIds,
          update_data: updateData,
        })
        this.lastResult = response.data
        notifyStore.success(`Updated ${response.data.success_count || 0} screens`)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || error.response?.data?.detail || error.message
        notifyStore.error('Failed to update screens: ' + this.error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Bulk activate template on screens
     */
    async bulkActivateTemplateOnScreens(screenIds, templateId, syncContent = true) {
      this.loading = true
      this.error = null
      const notifyStore = useNotificationStore()
      
      try {
        const response = await bulkOperationsAPI.screensActivateTemplate({
          item_ids: screenIds,
          template_id: templateId,
          sync_content: syncContent,
        })
        this.lastResult = response.data
        notifyStore.success(`Activated template on ${response.data.success_count || 0} screens`)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || error.response?.data?.detail || error.message
        notifyStore.error('Failed to activate template: ' + this.error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Bulk send command to screens
     */
    async bulkSendCommandToScreens(screenIds, commandType, payload = {}, priority = 0) {
      this.loading = true
      this.error = null
      const notifyStore = useNotificationStore()
      
      try {
        const response = await bulkOperationsAPI.screensSendCommand({
          item_ids: screenIds,
          command_type: commandType,
          payload: payload,
          priority: priority,
        })
        this.lastResult = response.data
        notifyStore.success(`Sent command to ${response.data.success_count || 0} screens`)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || error.response?.data?.detail || error.message
        notifyStore.error('Failed to send command: ' + this.error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Bulk delete templates
     */
    async bulkDeleteTemplates(itemIds) {
      this.loading = true
      this.error = null
      const notifyStore = useNotificationStore()
      
      try {
        const response = await bulkOperationsAPI.templatesDelete({ item_ids: itemIds })
        this.lastResult = response.data
        notifyStore.success(`Deleted ${response.data.success_count || 0} templates`)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || error.response?.data?.detail || error.message
        notifyStore.error('Failed to delete templates: ' + this.error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Bulk update templates
     */
    async bulkUpdateTemplates(itemIds, updateData) {
      this.loading = true
      this.error = null
      const notifyStore = useNotificationStore()
      
      try {
        const response = await bulkOperationsAPI.templatesUpdate({
          item_ids: itemIds,
          update_data: updateData,
        })
        this.lastResult = response.data
        notifyStore.success(`Updated ${response.data.success_count || 0} templates`)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || error.response?.data?.detail || error.message
        notifyStore.error('Failed to update templates: ' + this.error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Bulk activate templates
     */
    async bulkActivateTemplates(itemIds) {
      this.loading = true
      this.error = null
      const notifyStore = useNotificationStore()
      
      try {
        const response = await bulkOperationsAPI.templatesActivate({ item_ids: itemIds })
        this.lastResult = response.data
        notifyStore.success(`Activated ${response.data.success_count || 0} templates`)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || error.response?.data?.detail || error.message
        notifyStore.error('Failed to activate templates: ' + this.error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Bulk activate templates on screens
     */
    async bulkActivateTemplatesOnScreens(templateIds, screenIds) {
      this.loading = true
      this.error = null
      const notifyStore = useNotificationStore()
      
      try {
        const response = await bulkOperationsAPI.templatesActivateOnScreens({
          item_ids: templateIds,
          screen_ids: screenIds,
        })
        this.lastResult = response.data
        notifyStore.success(`Activated templates on ${response.data.success_count || 0} screens`)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || error.response?.data?.detail || error.message
        notifyStore.error('Failed to activate templates on screens: ' + this.error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Bulk delete contents
     */
    async bulkDeleteContents(itemIds) {
      this.loading = true
      this.error = null
      const notifyStore = useNotificationStore()
      
      try {
        const response = await bulkOperationsAPI.contentsDelete({ item_ids: itemIds })
        this.lastResult = response.data
        notifyStore.success(`Deleted ${response.data.success_count || 0} contents`)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || error.response?.data?.detail || error.message
        notifyStore.error('Failed to delete contents: ' + this.error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Bulk update contents
     */
    async bulkUpdateContents(itemIds, updateData) {
      this.loading = true
      this.error = null
      const notifyStore = useNotificationStore()
      
      try {
        const response = await bulkOperationsAPI.contentsUpdate({
          item_ids: itemIds,
          update_data: updateData,
        })
        this.lastResult = response.data
        notifyStore.success(`Updated ${response.data.success_count || 0} contents`)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || error.response?.data?.detail || error.message
        notifyStore.error('Failed to update contents: ' + this.error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Bulk download contents to screens
     */
    async bulkDownloadContents(itemIds, screenIds) {
      this.loading = true
      this.error = null
      const notifyStore = useNotificationStore()
      
      try {
        const response = await bulkOperationsAPI.contentsDownload({
          item_ids: itemIds,
          screen_ids: screenIds,
        })
        this.lastResult = response.data
        notifyStore.success(`Downloaded ${response.data.success_count || 0} contents`)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || error.response?.data?.detail || error.message
        notifyStore.error('Failed to download contents: ' + this.error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Bulk retry content downloads
     */
    async bulkRetryContents(itemIds) {
      this.loading = true
      this.error = null
      const notifyStore = useNotificationStore()
      
      try {
        const response = await bulkOperationsAPI.contentsRetry({ item_ids: itemIds })
        this.lastResult = response.data
        notifyStore.success(`Retried ${response.data.success_count || 0} content downloads`)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || error.response?.data?.detail || error.message
        notifyStore.error('Failed to retry content downloads: ' + this.error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Bulk delete schedules
     */
    async bulkDeleteSchedules(itemIds) {
      this.loading = true
      this.error = null
      const notifyStore = useNotificationStore()
      
      try {
        const response = await bulkOperationsAPI.schedulesDelete({ item_ids: itemIds })
        this.lastResult = response.data
        notifyStore.success(`Deleted ${response.data.success_count || 0} schedules`)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || error.response?.data?.detail || error.message
        notifyStore.error('Failed to delete schedules: ' + this.error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Bulk update schedules
     */
    async bulkUpdateSchedules(itemIds, updateData) {
      this.loading = true
      this.error = null
      const notifyStore = useNotificationStore()
      
      try {
        const response = await bulkOperationsAPI.schedulesUpdate({
          item_ids: itemIds,
          update_data: updateData,
        })
        this.lastResult = response.data
        notifyStore.success(`Updated ${response.data.success_count || 0} schedules`)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || error.response?.data?.detail || error.message
        notifyStore.error('Failed to update schedules: ' + this.error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Bulk activate schedules
     */
    async bulkActivateSchedules(itemIds) {
      this.loading = true
      this.error = null
      const notifyStore = useNotificationStore()
      
      try {
        const response = await bulkOperationsAPI.schedulesActivate({ item_ids: itemIds })
        this.lastResult = response.data
        notifyStore.success(`Activated ${response.data.success_count || 0} schedules`)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || error.response?.data?.detail || error.message
        notifyStore.error('Failed to activate schedules: ' + this.error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Bulk execute schedules
     */
    async bulkExecuteSchedules(itemIds) {
      this.loading = true
      this.error = null
      const notifyStore = useNotificationStore()
      
      try {
        const response = await bulkOperationsAPI.schedulesExecute({ item_ids: itemIds })
        this.lastResult = response.data
        notifyStore.success(`Executed ${response.data.success_count || 0} schedules`)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || error.response?.data?.detail || error.message
        notifyStore.error('Failed to execute schedules: ' + this.error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Bulk delete commands
     */
    async bulkDeleteCommands(itemIds) {
      this.loading = true
      this.error = null
      const notifyStore = useNotificationStore()
      
      try {
        const response = await bulkOperationsAPI.commandsDelete({ item_ids: itemIds })
        this.lastResult = response.data
        notifyStore.success(`Deleted ${response.data.success_count || 0} commands`)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || error.response?.data?.detail || error.message
        notifyStore.error('Failed to delete commands: ' + this.error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Bulk execute commands
     */
    async bulkExecuteCommands(itemIds) {
      this.loading = true
      this.error = null
      const notifyStore = useNotificationStore()
      
      try {
        const response = await bulkOperationsAPI.commandsExecute({ item_ids: itemIds })
        this.lastResult = response.data
        notifyStore.success(`Executed ${response.data.success_count || 0} commands`)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || error.response?.data?.detail || error.message
        notifyStore.error('Failed to execute commands: ' + this.error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Bulk retry commands
     */
    async bulkRetryCommands(itemIds) {
      this.loading = true
      this.error = null
      const notifyStore = useNotificationStore()
      
      try {
        const response = await bulkOperationsAPI.commandsRetry({ item_ids: itemIds })
        this.lastResult = response.data
        notifyStore.success(`Retried ${response.data.success_count || 0} commands`)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || error.response?.data?.detail || error.message
        notifyStore.error('Failed to retry commands: ' + this.error)
        throw error
      } finally {
        this.loading = false
      }
    },
  },
})
