/**
 * Content Validation Store
 * Manages content validation operations
 */
import { defineStore } from 'pinia'
import { contentValidationAPI } from '../services/api'
import { useNotificationStore } from './notification'

export const useContentValidationStore = defineStore('contentValidation', {
  state: () => ({
    validationResult: null,
    bulkValidationResults: null,
    loading: false,
    error: null,
    validatingFile: null,
  }),

  actions: {
    /**
     * Validate a single file
     */
    async validateFile(file, contentType, filename = null) {
      this.loading = true
      this.error = null
      this.validatingFile = filename || file.name
      
      try {
        const response = await contentValidationAPI.validate(file, contentType, filename)
        this.validationResult = response.data
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || error.response?.data?.detail || error.message
        throw error
      } finally {
        this.loading = false
        this.validatingFile = null
      }
    },

    /**
     * Validate multiple files in bulk
     */
    async validateFiles(files, contentTypes = [], filenames = []) {
      this.loading = true
      this.error = null
      const notifyStore = useNotificationStore()
      
      try {
        const response = await contentValidationAPI.validateBulk(
          files,
          contentTypes.length > 0 ? contentTypes : null,
          filenames.length > 0 ? filenames : null
        )
        this.bulkValidationResults = response.data.data || response.data
        
        const validCount = this.bulkValidationResults.valid_count || 0
        const invalidCount = this.bulkValidationResults.invalid_count || 0
        
        if (invalidCount > 0) {
          notifyStore.warning(
            `Validation complete: ${validCount} valid, ${invalidCount} invalid files`
          )
        } else {
          notifyStore.success(`All ${validCount} files are valid`)
        }
        
        return this.bulkValidationResults
      } catch (error) {
        this.error = error.response?.data?.error || error.response?.data?.detail || error.message
        notifyStore.error('Validation failed: ' + this.error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Get valid files from bulk validation results
     */
    getValidFiles() {
      if (!this.bulkValidationResults || !this.bulkValidationResults.results) {
        return []
      }
      return this.bulkValidationResults.results.filter(result => result.is_valid)
    },

    /**
     * Get invalid files from bulk validation results
     */
    getInvalidFiles() {
      if (!this.bulkValidationResults || !this.bulkValidationResults.results) {
        return []
      }
      return this.bulkValidationResults.results.filter(result => !result.is_valid)
    },

    /**
     * Reset validation state
     */
    reset() {
      this.validationResult = null
      this.bulkValidationResults = null
      this.error = null
      this.validatingFile = null
    },
  },
})
