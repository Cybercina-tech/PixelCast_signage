import { defineStore } from 'pinia'
import { screensAPI, commandsAPI, contentsAPI, logsAPI } from '../services/api'
import { smartUpdateObject, smartUpdateArray } from '../utils/deepCompare'

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
        console.log('DEBUG [fetchStats]: Starting stats fetch...')
        
        // Fetch screens to calculate stats
        let screens = []
        try {
          const screensResponse = await screensAPI.list()
          console.log('DEBUG [fetchStats]: Screens response:', screensResponse.data)
          // Handle different response structures
          if (screensResponse.data?.results && Array.isArray(screensResponse.data.results)) {
            screens = screensResponse.data.results
          } else if (Array.isArray(screensResponse.data)) {
            screens = screensResponse.data
          } else if (screensResponse.data?.data && Array.isArray(screensResponse.data.data)) {
            screens = screensResponse.data.data
          }
          console.log('DEBUG [fetchStats]: Parsed screens:', screens.length)
        } catch (e) {
          console.error('DEBUG [fetchStats]: Error fetching screens:', e)
        }
        
        // Fetch pending commands
        let pendingCommands = []
        try {
          const commandsResponse = await commandsAPI.pending()
          console.log('DEBUG [fetchStats]: Commands response:', commandsResponse.data)
          // Handle different response structures
          if (commandsResponse.data?.commands && Array.isArray(commandsResponse.data.commands)) {
            pendingCommands = commandsResponse.data.commands
          } else if (commandsResponse.data?.results && Array.isArray(commandsResponse.data.results)) {
            pendingCommands = commandsResponse.data.results
          } else if (Array.isArray(commandsResponse.data)) {
            pendingCommands = commandsResponse.data
          } else if (commandsResponse.data?.data && Array.isArray(commandsResponse.data.data)) {
            pendingCommands = commandsResponse.data.data
          }
          console.log('DEBUG [fetchStats]: Parsed pending commands:', pendingCommands.length)
        } catch (e) {
          console.error('DEBUG [fetchStats]: Error fetching commands:', e)
        }
        
        // Fetch downloading content - try different status values
        let downloadingContent = []
        try {
          // Try 'downloading' status first
          let contentsResponse = await contentsAPI.list({ download_status: 'downloading' })
          console.log('DEBUG [fetchStats]: Contents response (downloading):', contentsResponse.data)
          
          // Handle different response structures
          if (contentsResponse.data?.results && Array.isArray(contentsResponse.data.results)) {
            downloadingContent = contentsResponse.data.results
          } else if (Array.isArray(contentsResponse.data)) {
            downloadingContent = contentsResponse.data
          } else if (contentsResponse.data?.data && Array.isArray(contentsResponse.data.data)) {
            downloadingContent = contentsResponse.data.data
          }
          
          // If no results, try 'pending' status
          if (downloadingContent.length === 0) {
            contentsResponse = await contentsAPI.list({ download_status: 'pending' })
            if (contentsResponse.data?.results && Array.isArray(contentsResponse.data.results)) {
              downloadingContent = contentsResponse.data.results.filter(c => 
                c.download_status === 'downloading' || c.download_status === 'pending'
              )
            } else if (Array.isArray(contentsResponse.data)) {
              downloadingContent = contentsResponse.data.filter(c => 
                c.download_status === 'downloading' || c.download_status === 'pending'
              )
            }
          }
          
          console.log('DEBUG [fetchStats]: Parsed downloading content:', downloadingContent.length)
        } catch (e) {
          console.error('DEBUG [fetchStats]: Error fetching content:', e)
        }
        
        // Calculate stats
        const onlineScreens = screens.filter(s => s.is_online === true).length
        const offlineScreens = screens.filter(s => s.is_online === false).length
        
        console.log('DEBUG [fetchStats]: Calculated stats:', {
          online_screens: onlineScreens,
          offline_screens: offlineScreens,
          commands_in_queue: pendingCommands.length,
          content_downloading: downloadingContent.length,
        })
        
        // Smart update: Only update stats if values changed
        const newStats = {
          online_screens: onlineScreens,
          offline_screens: offlineScreens,
          commands_in_queue: pendingCommands.length,
          content_downloading: downloadingContent.length,
        }
        this.stats = smartUpdateObject(this.stats, newStats)
        
        console.log('DEBUG [fetchStats]: Final stats:', this.stats)
      } catch (error) {
        console.error('DEBUG [fetchStats]: Error:', error)
        this.error = error.response?.data?.detail || error.response?.data?.message || error.message
        // Don't reset stats on error - keep previous values
        console.warn('DEBUG [fetchStats]: Error occurred, keeping previous stats')
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
        
        // Smart update: Only update metrics if data changed
        const newMetrics = {
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
        // Update each metric array only if changed
        this.metrics = {
          cpu: smartUpdateArray(this.metrics.cpu || [], newMetrics.cpu, 'time'),
          memory: smartUpdateArray(this.metrics.memory || [], newMetrics.memory, 'time'),
          latency: smartUpdateArray(this.metrics.latency || [], newMetrics.latency, 'time'),
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
          const cmdLogs = await logsAPI.commandExecution.list({ page_size: 15, ordering: '-created_at' })
          const cmdLogsData = cmdLogs.data.results || cmdLogs.data || []
          if (Array.isArray(cmdLogsData)) {
            cmdLogsData.forEach(log => {
              if (log && log.id) {
                activities.push({
                  id: `cmd-${log.id}`,
                  type: 'command',
                  message: `Command "${log.command_name || log.command_type_display || log.command_type || 'Unknown'}" ${log.status_display || log.status || 'executed'} on ${log.screen_name || 'Screen'}`,
                  timestamp: log.created_at || log.started_at || new Date().toISOString(),
                  details: log,
                })
              }
            })
          }
        } catch (e) {
          console.error('Failed to fetch command logs:', e)
        }
        
        // Recent content downloads
        try {
          const contentLogs = await logsAPI.contentDownload.list({ page_size: 15, ordering: '-created_at' })
          const contentLogsData = contentLogs.data.results || contentLogs.data || []
          if (Array.isArray(contentLogsData)) {
            contentLogsData.forEach(log => {
              if (log && log.id) {
                activities.push({
                  id: `content-${log.id}`,
                  type: 'content',
                  message: `Content "${log.content_name || 'Unknown'}" ${log.status_display || log.status || 'downloaded'} on ${log.screen_name || 'Screen'}`,
                  timestamp: log.created_at || log.downloaded_at || new Date().toISOString(),
                  details: log,
                })
              }
            })
          }
        } catch (e) {
          console.error('Failed to fetch content logs:', e)
        }
        
        // Recent screen status changes (only significant ones - online/offline transitions)
        try {
          const statusLogs = await logsAPI.screenStatus.list({ page_size: 15, ordering: '-recorded_at' })
          const statusLogsData = statusLogs.data.results || statusLogs.data || []
          if (Array.isArray(statusLogsData)) {
            // Group by screen and only show status changes
            const screenStatusMap = new Map()
            statusLogsData.forEach(log => {
              if (log && log.id && log.screen_id) {
                const key = log.screen_id
                if (!screenStatusMap.has(key) || screenStatusMap.get(key).recorded_at < log.recorded_at) {
                  screenStatusMap.set(key, log)
                }
              }
            })
            
            screenStatusMap.forEach(log => {
              activities.push({
                id: `status-${log.id}`,
                type: 'screen',
                message: `Screen "${log.screen_name || 'Unknown'}" is now ${log.status_display || log.status || 'online'}`,
                timestamp: log.recorded_at || new Date().toISOString(),
                details: log,
              })
            })
          }
        } catch (e) {
          console.error('Failed to fetch status logs:', e)
        }
        
        // Sort by timestamp (most recent first) and take top 20
        const newActivities = activities
          .filter(activity => activity.timestamp) // Only include activities with valid timestamps
          .sort((a, b) => {
            const dateA = new Date(a.timestamp)
            const dateB = new Date(b.timestamp)
            return dateB - dateA // Most recent first
          })
          .slice(0, 20)
        
        // Smart update: Only update activities array if changed
        this.activities = smartUpdateArray(this.activities || [], newActivities, 'id')
        
        console.log(`Loaded ${this.activities.length} recent activities`)
      } catch (error) {
        console.error('Error fetching activities:', error)
        this.error = error.response?.data?.detail || error.response?.data?.message || error.message
        this.activities = []
      } finally {
        this.loading = false
      }
    },
  },
})
