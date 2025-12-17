import { defineStore } from 'pinia'
import { commandsAPI } from '../services/api'

export const useCommandsStore = defineStore('commands', {
  state: () => ({
    commands: [],
    currentCommand: null,
    loading: false,
    error: null,
    filters: {
      search: '',
      type: null,
      status: null,
      screen: null,
    },
  }),
  getters: {
    pendingCommands: (state) => state.commands.filter(c => c.status === 'pending'),
    executingCommands: (state) => state.commands.filter(c => c.status === 'executing'),
    completedCommands: (state) => state.commands.filter(c => c.status === 'done'),
    failedCommands: (state) => state.commands.filter(c => c.status === 'failed'),
    filteredCommands: (state) => {
      let filtered = state.commands
      if (state.filters.search) {
        const search = state.filters.search.toLowerCase()
        filtered = filtered.filter(c => 
          c.name?.toLowerCase().includes(search) ||
          c.type?.toLowerCase().includes(search)
        )
      }
      if (state.filters.type) {
        filtered = filtered.filter(c => c.type === state.filters.type)
      }
      if (state.filters.status) {
        filtered = filtered.filter(c => c.status === state.filters.status)
      }
      if (state.filters.screen) {
        filtered = filtered.filter(c => c.screen === state.filters.screen)
      }
      return filtered
    },
  },
  actions: {
    async fetchCommands(params = {}) {
      this.loading = true
      this.error = null
      try {
        const response = await commandsAPI.list({ ...this.filters, ...params })
        this.commands = response.data.results || response.data || []
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || error.response?.data?.message || error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    async fetchCommand(id) {
      this.loading = true
      this.error = null
      try {
        const response = await commandsAPI.detail(id)
        this.currentCommand = response.data
        // Update in list if exists
        const index = this.commands.findIndex(c => c.id === id)
        if (index !== -1) {
          this.commands[index] = response.data
        }
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || error.response?.data?.message || error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    async createCommand(data) {
      this.loading = true
      this.error = null
      try {
        const response = await commandsAPI.create(data)
        this.commands.push(response.data)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || error.response?.data?.message || error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    async updateCommand(id, data) {
      this.loading = true
      this.error = null
      try {
        const response = await commandsAPI.update(id, data)
        const index = this.commands.findIndex(c => c.id === id)
        if (index !== -1) {
          this.commands[index] = response.data
        }
        if (this.currentCommand?.id === id) {
          this.currentCommand = response.data
        }
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || error.response?.data?.message || error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    async deleteCommand(id) {
      this.loading = true
      this.error = null
      try {
        await commandsAPI.delete(id)
        this.commands = this.commands.filter(c => c.id !== id)
        if (this.currentCommand?.id === id) {
          this.currentCommand = null
        }
      } catch (error) {
        this.error = error.response?.data?.detail || error.response?.data?.message || error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    async executeCommand(id, data = {}) {
      this.loading = true
      this.error = null
      try {
        const response = await commandsAPI.execute(id, data)
        // Update command status
        const index = this.commands.findIndex(c => c.id === id)
        if (index !== -1) {
          this.commands[index] = { ...this.commands[index], ...response.data }
        }
        if (this.currentCommand?.id === id) {
          this.currentCommand = { ...this.currentCommand, ...response.data }
        }
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || error.response?.data?.message || error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    async retryCommand(id) {
      this.loading = true
      this.error = null
      try {
        const response = await commandsAPI.retry(id)
        // Update command status
        const index = this.commands.findIndex(c => c.id === id)
        if (index !== -1) {
          this.commands[index] = { ...this.commands[index], ...response.data }
        }
        if (this.currentCommand?.id === id) {
          this.currentCommand = { ...this.currentCommand, ...response.data }
        }
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || error.response?.data?.message || error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    async fetchPending(params = {}) {
      this.loading = true
      this.error = null
      try {
        const response = await commandsAPI.pending(params)
        // Backend returns: {status: 'success', commands: [...], count: N}
        const commands = response.data.commands || response.data.results || response.data || []
        return commands
      } catch (error) {
        this.error = error.response?.data?.detail || error.response?.data?.message || error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    async fetchStatus(params = {}) {
      this.loading = true
      this.error = null
      try {
        const response = await commandsAPI.status(params)
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
