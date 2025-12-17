import { defineStore } from 'pinia'
import { screensAPI, commandsAPI, contentsAPI, logsAPI } from '../services/api'

export const useDashboardStore = defineStore('dashboard', {
  state: () => ({
    stats: {
      online_screens: 0,
      offline_screens: 0,
      commands_in_queue: 0,
      content_downloading: 0,
    },
    metrics: {
      cpu: [],
      memory: [],
      latency: [],
    },
    activities: [],
    loading: false,
    error: null,
  }),
  actions: {
    async fetchStats() {
      this.loading = true
      this.error = null
      try {
        // Fetch screens to calculate stats
        const screensResponse = await screensAPI.list()
        const screens = screensResponse.data.results || screensResponse.data || []
        
        // Fetch pending commands
        const commandsResponse = await commandsAPI.pending()
        const pendingCommands = commandsResponse.data.commands || commandsResponse.data.results || commandsResponse.data || []
        
        // Fetch downloading content
        const contentsResponse = await contentsAPI.list({ download_status: 'downloading' })
        const downloadingContent = contentsResponse.data.results || contentsResponse.data || []
        
        this.stats = {
          online_screens: screens.filter(s => s.is_online).length,
          offline_screens: screens.filter(s => !s.is_online).length,
          commands_in_queue: pendingCommands.length,
          content_downloading: downloadingContent.length,
        }
      } catch (error) {
        this.error = error.response?.data?.detail || error.response?.data?.message || error.message
        // Set default stats on error
        this.stats = {
          online_screens: 0,
          offline_screens: 0,
          commands_in_queue: 0,
          content_downloading: 0,
        }
      } finally {
        this.loading = false
      }
    },
    async fetchMetrics() {
      this.loading = true
      this.error = null
      try {
        // Fetch recent screen status logs for metrics
        const response = await logsAPI.screenStatus.list({ page_size: 100 })
        const logs = response.data.results || response.data || []
        
        // Process logs for charts (last 24 hours)
        const now = new Date()
        const last24h = logs
          .filter(log => {
            if (!log.recorded_at) return false
            const logDate = new Date(log.recorded_at)
            return (now - logDate) < 24 * 60 * 60 * 1000
          })
          .sort((a, b) => new Date(a.recorded_at) - new Date(b.recorded_at))
        
        this.metrics = {
          cpu: last24h.map(log => ({
            time: log.recorded_at,
            value: log.cpu_usage || 0,
          })),
          memory: last24h.map(log => ({
            time: log.recorded_at,
            value: log.memory_usage || 0,
          })),
          latency: last24h.map(log => ({
            time: log.recorded_at,
            value: log.heartbeat_latency || 0,
          })),
        }
      } catch (error) {
        this.error = error.response?.data?.detail || error.response?.data?.message || error.message
        // Set empty metrics on error
        this.metrics = {
          cpu: [],
          memory: [],
          latency: [],
        }
      } finally {
        this.loading = false
      }
    },
    async fetchActivities() {
      this.loading = true
      this.error = null
      try {
        // Fetch recent activities from logs
        const activities = []
        
        // Recent command executions
        try {
          const cmdLogs = await logsAPI.commandExecution.list({ page_size: 10 })
          const cmdLogsData = cmdLogs.data.results || cmdLogs.data || []
          cmdLogsData.forEach(log => {
            activities.push({
              id: `cmd-${log.id}`,
              type: 'command',
              message: `Command ${log.command_type_display || log.command_type} ${log.status_display || log.status} on ${log.screen_name || 'Screen'}`,
              timestamp: log.created_at,
              details: log,
            })
          })
        } catch (e) {
          console.error('Failed to fetch command logs:', e)
        }
        
        // Recent content downloads
        try {
          const contentLogs = await logsAPI.contentDownload.list({ page_size: 10 })
          const contentLogsData = contentLogs.data.results || contentLogs.data || []
          contentLogsData.forEach(log => {
            activities.push({
              id: `content-${log.id}`,
              type: 'content',
              message: `Content "${log.content_name || 'Unknown'}" ${log.status_display || log.status} on ${log.screen_name || 'Screen'}`,
              timestamp: log.created_at,
              details: log,
            })
          })
        } catch (e) {
          console.error('Failed to fetch content logs:', e)
        }
        
        // Recent screen status changes
        try {
          const statusLogs = await logsAPI.screenStatus.list({ page_size: 10 })
          const statusLogsData = statusLogs.data.results || statusLogs.data || []
          statusLogsData.forEach(log => {
            activities.push({
              id: `status-${log.id}`,
              type: 'screen',
              message: `Screen "${log.screen_name || 'Unknown'}" is ${log.status_display || log.status}`,
              timestamp: log.recorded_at,
              details: log,
            })
          })
        } catch (e) {
          console.error('Failed to fetch status logs:', e)
        }
        
        // Sort by timestamp and take most recent
        this.activities = activities
          .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
          .slice(0, 20)
      } catch (error) {
        this.error = error.response?.data?.detail || error.response?.data?.message || error.message
        this.activities = []
      } finally {
        this.loading = false
      }
    },
  },
})
