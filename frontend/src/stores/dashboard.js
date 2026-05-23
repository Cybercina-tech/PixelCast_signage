import { defineStore } from 'pinia'
import { screensAPI, commandsAPI, contentsAPI, logsAPI, coreAPI } from '../services/api'
import { smartUpdateObject, smartUpdateArray } from '../utils/deepCompare'
import { hasPermission } from '../utils/permissions'
import { isTransientNetworkError, OFFLINE_ERROR_CODE } from '../utils/networkError'
import { useAuthStore } from './auth'

function isScreenIdError(e) {
  const msg = e?.response?.data?.message || e?.response?.data?.error || ''
  return String(msg).includes('screen_id')
}

function handleFetchError(e, context) {
  if (isScreenIdError(e)) {
    if (import.meta.env.DEV) {
      console.debug(`[fetchStats] Suppressed screen_id in ${context}`)
    }
    return
  }
  if (isTransientNetworkError(e)) {
    if (import.meta.env.DEV) {
      console.debug(`[fetchStats] Network unavailable (${context})`)
    }
    return OFFLINE_ERROR_CODE
  }
  if (import.meta.env.DEV) {
    console.error(`[fetchStats] Error fetching ${context}:`, e)
  }
  return e.response?.data?.detail || e.response?.data?.message || e.message
}

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
      if (typeof navigator !== 'undefined' && navigator.onLine === false) {
        this.error = OFFLINE_ERROR_CODE
        return
      }

      this.loading = true
      this.error = null
      let offlineHit = false

      try {
        let screens = []
        try {
          const screensResponse = await screensAPI.list({})
          if (screensResponse.data?.results && Array.isArray(screensResponse.data.results)) {
            screens = screensResponse.data.results
          } else if (Array.isArray(screensResponse.data)) {
            screens = screensResponse.data
          } else if (screensResponse.data?.data && Array.isArray(screensResponse.data.data)) {
            screens = screensResponse.data.data
          }
        } catch (e) {
          const err = handleFetchError(e, 'screens')
          if (err === OFFLINE_ERROR_CODE) offlineHit = true
        }

        let pendingCommands = []
        try {
          const commandsResponse = await commandsAPI.pending({})
          if (commandsResponse.data?.commands && Array.isArray(commandsResponse.data.commands)) {
            pendingCommands = commandsResponse.data.commands
          } else if (commandsResponse.data?.results && Array.isArray(commandsResponse.data.results)) {
            pendingCommands = commandsResponse.data.results
          } else if (Array.isArray(commandsResponse.data)) {
            pendingCommands = commandsResponse.data
          } else if (commandsResponse.data?.data && Array.isArray(commandsResponse.data.data)) {
            pendingCommands = commandsResponse.data.data
          }
        } catch (e) {
          const err = handleFetchError(e, 'commands')
          if (err === OFFLINE_ERROR_CODE) offlineHit = true
        }

        let downloadingContent = []
        try {
          let contentsResponse = await contentsAPI.list({ download_status: 'downloading' })
          if (contentsResponse.data?.results && Array.isArray(contentsResponse.data.results)) {
            downloadingContent = contentsResponse.data.results
          } else if (Array.isArray(contentsResponse.data)) {
            downloadingContent = contentsResponse.data
          } else if (contentsResponse.data?.data && Array.isArray(contentsResponse.data.data)) {
            downloadingContent = contentsResponse.data.data
          }

          if (downloadingContent.length === 0) {
            contentsResponse = await contentsAPI.list({ download_status: 'pending' })
            if (contentsResponse.data?.results && Array.isArray(contentsResponse.data.results)) {
              downloadingContent = contentsResponse.data.results.filter(
                (c) => c.download_status === 'downloading' || c.download_status === 'pending'
              )
            } else if (Array.isArray(contentsResponse.data)) {
              downloadingContent = contentsResponse.data.filter(
                (c) => c.download_status === 'downloading' || c.download_status === 'pending'
              )
            }
          }
        } catch (e) {
          const err = handleFetchError(e, 'content')
          if (err === OFFLINE_ERROR_CODE) offlineHit = true
        }

        const newStats = {
          online_screens: screens.filter((s) => s.is_online === true).length,
          offline_screens: screens.filter((s) => s.is_online === false).length,
          commands_in_queue: pendingCommands.length,
          content_downloading: downloadingContent.length,
        }
        this.stats = smartUpdateObject(this.stats, newStats)

        if (offlineHit) {
          this.error = OFFLINE_ERROR_CODE
        }
      } catch (error) {
        const err = handleFetchError(error, 'stats')
        if (err === OFFLINE_ERROR_CODE) {
          this.error = OFFLINE_ERROR_CODE
        } else if (err) {
          this.error = err
        }
      } finally {
        this.loading = false
      }
    },
    async fetchMetrics() {
      this.loading = true
      this.error = null
      const authStore = useAuthStore()
      if (!hasPermission(authStore.user, 'view_logs')) {
        this.metrics = { cpu: [], memory: [], latency: [] }
        this.loading = false
        return
      }
      try {
        const response = await logsAPI.screenStatus.list({ page_size: 100 })
        const logs = response.data.results || response.data || []

        const now = new Date()
        const last24h = logs
          .filter((log) => {
            if (!log.recorded_at) return false
            const logDate = new Date(log.recorded_at)
            return now - logDate < 24 * 60 * 60 * 1000
          })
          .sort((a, b) => new Date(a.recorded_at) - new Date(b.recorded_at))

        const newMetrics = {
          cpu: last24h.map((log) => ({
            time: log.recorded_at,
            value: log.cpu_usage || 0,
          })),
          memory: last24h.map((log) => ({
            time: log.recorded_at,
            value: log.memory_usage || 0,
          })),
          latency: last24h.map((log) => ({
            time: log.recorded_at,
            value: log.heartbeat_latency || 0,
          })),
        }
        this.metrics = {
          cpu: smartUpdateArray(this.metrics.cpu || [], newMetrics.cpu, 'time'),
          memory: smartUpdateArray(this.metrics.memory || [], newMetrics.memory, 'time'),
          latency: smartUpdateArray(this.metrics.latency || [], newMetrics.latency, 'time'),
        }
      } catch (error) {
        if (isTransientNetworkError(error)) {
          this.error = OFFLINE_ERROR_CODE
        } else {
          this.error = error.response?.data?.detail || error.response?.data?.message || error.message
        }
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
      if (typeof navigator !== 'undefined' && navigator.onLine === false) {
        this.error = OFFLINE_ERROR_CODE
        return
      }

      this.loading = true
      this.error = null
      try {
        const activities = []

        try {
          const auditLogs = await coreAPI.auditLogs.list({ page_size: 20, ordering: '-timestamp' })
          const auditLogsData = auditLogs.data?.results || auditLogs.data || []
          if (Array.isArray(auditLogsData)) {
            auditLogsData.forEach((log) => {
              if (log && log.id) {
                let activityType = 'update'
                if (log.action_type === 'create') {
                  activityType =
                    log.resource_type === 'Template'
                      ? 'template'
                      : log.resource_type === 'Screen'
                        ? 'screen'
                        : 'update'
                } else if (log.action_type === 'delete') {
                  activityType = 'alert'
                } else if (log.action_type === 'execute') {
                  activityType = 'command'
                }

                activities.push({
                  id: `audit-${log.id}`,
                  type: activityType,
                  message:
                    log.description ||
                    `${log.action_type} ${log.resource_type || 'resource'}: ${log.resource_name || 'Unknown'}`,
                  timestamp: log.timestamp || new Date().toISOString(),
                  details: log,
                })
              }
            })
          }
        } catch (e) {
          if (import.meta.env.DEV) {
            console.warn('Failed to fetch audit logs, falling back to logs:', e)
          }
        }

        const authStore = useAuthStore()
        const canViewOperationalLogs = hasPermission(authStore.user, 'view_logs')

        if (canViewOperationalLogs && activities.length < 10) {
          try {
            const cmdLogs = await logsAPI.commandExecution.list({ page_size: 10, ordering: '-created_at' })
            const cmdLogsData = cmdLogs.data.results || cmdLogs.data || []
            if (Array.isArray(cmdLogsData)) {
              cmdLogsData.forEach((log) => {
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
            handleFetchError(e, 'command logs')
          }
        }

        if (canViewOperationalLogs && activities.length < 15) {
          try {
            const contentLogs = await logsAPI.contentDownload.list({ page_size: 10, ordering: '-created_at' })
            const contentLogsData = contentLogs.data.results || contentLogs.data || []
            if (Array.isArray(contentLogsData)) {
              contentLogsData.forEach((log) => {
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
            handleFetchError(e, 'content logs')
          }
        }

        if (canViewOperationalLogs && activities.length < 20) {
          try {
            const statusLogs = await logsAPI.screenStatus.list({ page_size: 10, ordering: '-recorded_at' })
            const statusLogsData = statusLogs.data.results || statusLogs.data || []
            if (Array.isArray(statusLogsData)) {
              const screenStatusMap = new Map()
              statusLogsData.forEach((log) => {
                if (log && log.id && log.screen_id) {
                  const key = log.screen_id
                  if (!screenStatusMap.has(key) || screenStatusMap.get(key).recorded_at < log.recorded_at) {
                    screenStatusMap.set(key, log)
                  }
                }
              })

              screenStatusMap.forEach((log) => {
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
            handleFetchError(e, 'status logs')
          }
        }

        const newActivities = activities
          .filter((activity) => activity.timestamp)
          .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
          .slice(0, 20)

        this.activities = smartUpdateArray(this.activities || [], newActivities, 'id')
      } catch (error) {
        if (isTransientNetworkError(error)) {
          this.error = OFFLINE_ERROR_CODE
        } else {
          this.error = error.response?.data?.detail || error.response?.data?.message || error.message
        }
        this.activities = []
      } finally {
        this.loading = false
      }
    },
  },
})
