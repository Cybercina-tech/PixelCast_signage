import axios from 'axios'
import { getNotification } from '@/composables/useNotification'

// API base URL - update this to match your backend
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Error message mapping for user-friendly notifications
const ERROR_MESSAGES = {
  400: 'Invalid request. Please check your input.',
  401: 'Authentication required. Please log in.',
  403: 'You do not have permission to perform this action.',
  404: 'The requested resource was not found.',
  413: 'File too large. Please choose a smaller file.',
  415: 'Unsupported file type. Please choose a different file.',
  422: 'Validation error. Please check your input.',
  429: 'Too many requests. Please wait a moment and try again.',
  500: 'Server error. Please try again later.',
  502: 'Service temporarily unavailable. Please try again later.',
  503: 'Service unavailable. Please try again later.',
  504: 'Request timeout. Please try again.',
}

/**
 * Get user-friendly error message from error response
 */
function getUserFriendlyMessage(error) {
  const status = error.response?.status
  const data = error.response?.data
  
  // Check for custom error message from backend
  if (data?.message) {
    return data.message
  }
  
  // Check for error field
  if (data?.error) {
    return data.error
  }
  
  // Check for detail field (DRF format)
  if (data?.detail) {
    return data.detail
  }
  
  // Use status code mapping
  if (status && ERROR_MESSAGES[status]) {
    return ERROR_MESSAGES[status]
  }
  
  // Fallback to generic message
  return 'An error occurred. Please try again.'
}

/**
 * Extract field-specific validation errors from response
 */
function getFieldErrors(error) {
  const data = error.response?.data
  
  if (!data) return {}
  
  // DRF validation errors format: { field: ['error1', 'error2'] }
  if (data.errors && typeof data.errors === 'object') {
    return data.errors
  }
  
  // Alternative format: { field: 'error' }
  if (data.error && typeof data.error === 'object' && !Array.isArray(data.error)) {
    return data.error
  }
  
  // Nested errors format
  const fieldErrors = {}
  for (const key in data) {
    if (key !== 'message' && key !== 'error' && key !== 'detail' && key !== 'status') {
      fieldErrors[key] = Array.isArray(data[key]) ? data[key] : [data[key]]
    }
  }
  
  return Object.keys(fieldErrors).length > 0 ? fieldErrors : {}
}

// Request interceptor to add auth token and handle FormData
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // CRITICAL: Remove Content-Type header for FormData so axios can set it automatically with boundary
    // If we don't do this, the default 'application/json' header will break multipart/form-data uploads
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type']
      // axios will automatically set: Content-Type: multipart/form-data; boundary=----WebKitFormBoundary...
    }
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling and token refresh
let isRefreshing = false
let failedQueue = []

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  failedQueue = []
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    const status = error.response?.status
    
    // Don't try to refresh token for auth endpoints (login, signup, etc.)
    const isAuthEndpoint = originalRequest.url?.includes('/auth/login/') || 
                          originalRequest.url?.includes('/auth/signup/') ||
                          originalRequest.url?.includes('/auth/token/')
    
    // Handle 401 - try to refresh token (but not for auth endpoints)
    if (status === 401 && !originalRequest._retry && !isAuthEndpoint) {
      if (isRefreshing) {
        // If already refreshing, queue this request
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        })
          .then(token => {
            originalRequest.headers.Authorization = `Bearer ${token}`
            return api(originalRequest)
          })
          .catch(err => {
            return Promise.reject(err)
          })
      }

      originalRequest._retry = true
      isRefreshing = true

      const refreshToken = localStorage.getItem('refresh_token')
      
      if (!refreshToken) {
        // No refresh token, clear everything and redirect to login
        localStorage.removeItem('auth_token')
        localStorage.removeItem('refresh_token')
        isRefreshing = false
        processQueue(new Error('No refresh token'), null)
        
        const notify = getNotification()
        notify.error('Session expired. Please log in again.')
        
        if (window.location.pathname !== '/login' && 
            window.location.pathname !== '/' &&
            !window.location.pathname.startsWith('/401')) {
          window.location.href = '/login'
        }
        return Promise.reject(error)
      }

      try {
        const response = await authAPI.refreshToken(refreshToken)
        const { access } = response.data
        
        localStorage.setItem('auth_token', access)
        if (response.data.refresh) {
          localStorage.setItem('refresh_token', response.data.refresh)
        }
        
        originalRequest.headers.Authorization = `Bearer ${access}`
        isRefreshing = false
        processQueue(null, access)
        
        return api(originalRequest)
      } catch (refreshError) {
        // Refresh failed, clear tokens and redirect to login
        localStorage.removeItem('auth_token')
        localStorage.removeItem('refresh_token')
        isRefreshing = false
        processQueue(refreshError, null)
        
        const notify = getNotification()
        notify.error('Session expired. Please log in again.')
        
        if (window.location.pathname !== '/login' && 
            window.location.pathname !== '/' &&
            !window.location.pathname.startsWith('/401')) {
          window.location.href = '/login'
        }
        return Promise.reject(refreshError)
      }
    }
    
    // Handle 4xx and 5xx errors with user-friendly notifications
    if (status && status >= 400) {
      const userMessage = getUserFriendlyMessage(error)
      const errorData = error.response?.data || {}
      
      // Suppress screen_id errors - these are expected for global dashboard endpoints
      // and shouldn't be shown to users
      const isScreenIdError = userMessage?.includes('screen_id') || 
                              errorData?.message?.includes('screen_id') ||
                              errorData?.error?.includes('screen_id') ||
                              originalRequest.url?.includes('/screens/command-pull/') ||
                              originalRequest.url?.includes('/screens/health-check/')
      
      // Only show notification if it's not a suppressed screen_id error
      if (!isScreenIdError) {
        const notify = getNotification()
        const fieldErrors = getFieldErrors(error)
        
        // Show toast notification
        if (status >= 500) {
          notify.error(userMessage, { title: 'Server Error', duration: 5000 })
        } else if (status === 403) {
          notify.error(userMessage, { title: 'Access Denied', duration: 4000 })
          // Redirect to 403 page if not already there
          if (!window.location.pathname.startsWith('/403')) {
            setTimeout(() => {
              window.location.href = '/403'
            }, 2000)
          }
        } else if (status === 401) {
          notify.error(userMessage, { title: 'Authentication Required', duration: 3000 })
        } else {
          // 4xx errors (400, 404, 413, 422, etc.)
          notify.error(userMessage, { title: 'Request Error', duration: 4000 })
        }
        
        // Attach field errors to error object for component-level handling
        if (Object.keys(fieldErrors).length > 0) {
          error.fieldErrors = fieldErrors
        }
      } else {
        // Log suppressed error for debugging (but don't show to user)
        console.debug('Suppressed screen_id error:', {
          url: originalRequest.url,
          message: userMessage,
          error: errorData
        })
      }
    }
    
    return Promise.reject(error)
  }
)

// Authentication API
export const authAPI = {
  signup: (data) => api.post('/auth/signup/', data),
  login: (credentials) => api.post('/auth/login/', credentials),
  logout: (data) => api.post('/auth/logout/', data),
  logoutAll: () => api.post('/auth/logout-all/'),
  sessions: () => api.get('/auth/sessions/'),
  token: (credentials) => api.post('/auth/token/', credentials),
  refreshToken: (refresh) => {
    // Use a separate axios instance without interceptors to avoid infinite loop
    const refreshApi = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    })
    return refreshApi.post('/auth/token/refresh/', { refresh })
  },
}

// Users API
export const usersAPI = {
  list: (params) => api.get('/users/', { params }),
  detail: (id) => api.get(`/users/${id}/`),
  create: (data) => api.post('/users/', data),
  update: (id, data) => api.put(`/users/${id}/`, data),
  patch: (id, data) => api.patch(`/users/${id}/`, data),
  delete: (id) => api.delete(`/users/${id}/`),
  me: () => api.get('/users/me/'),
  updateMe: (data) => api.patch('/users/me/', data),
  changePasswordMe: (data) => api.post('/users/change_password_me/', data),
  activityLogs: (params) => api.get('/users/activity_logs/', { params }),
  changePassword: (id, data) => api.post(`/users/${id}/change_password/`, data),
  changeRole: (id, data) => api.post(`/users/${id}/change_role/`, data),
  sendVerificationEmail: () => api.post('/send-verification-email/'),
  verifyEmail: (data) => api.post('/verify-email/', data),
  sidebarItems: () => api.get('/sidebar-items/'),
}

// Roles API
export const rolesAPI = {
  list: () => api.get('/roles/'),
  create: (data) => api.post('/roles/create/', data),
}

// Screens API
export const screensAPI = {
  list: (params) => api.get('/screens/', { params }),
  detail: (id) => api.get(`/screens/${id}/`),
  create: (data) => api.post('/screens/', data),
  update: (id, data) => api.put(`/screens/${id}/`, data),
  patch: (id, data) => api.patch(`/screens/${id}/`, data),
  delete: (id) => api.delete(`/screens/${id}/`),
  heartbeat: (id, data) => api.post(`/screens/${id}/heartbeat/`, data),
  // Standalone endpoints (for screen clients)
  heartbeatStandalone: (data) => api.post('/screens/heartbeat/', data),
  commandPull: (params) => api.get('/screens/command-pull/', { params }),
  commandResponse: (data) => api.post('/screens/command-response/', data),
  contentSync: (data) => api.post('/screens/content-sync/', data),
  healthCheck: (params) => api.get('/screens/health-check/', { params }),
}

// Pairing API
export const pairingAPI = {
  generate: () => api.post('/pairing/generate/'),
  status: (params) => api.get('/pairing/status/', { params }),
  bind: (data) => api.post('/pairing/bind/', data),
}

// Templates API
export const templatesAPI = {
  list: (params) => api.get('/templates/', { params }),
  detail: (id) => api.get(`/templates/${id}/`),
  create: (data) => api.post('/templates/', data),
  update: (id, data) => api.put(`/templates/${id}/`, data),
  patch: (id, data) => api.patch(`/templates/${id}/`, data),
  delete: (id) => api.delete(`/templates/${id}/`),
  activateOnScreen: (id, data) => api.post(`/templates/${id}/activate_on_screen/`, data),
}

// Layers API
export const layersAPI = {
  list: (params) => api.get('/layers/', { params }),
  detail: (id) => api.get(`/layers/${id}/`),
  create: (data) => api.post('/layers/', data),
  update: (id, data) => api.put(`/layers/${id}/`, data),
  patch: (id, data) => api.patch(`/layers/${id}/`, data),
  delete: (id) => api.delete(`/layers/${id}/`),
}

// Widgets API
export const widgetsAPI = {
  list: (params) => api.get('/widgets/', { params }),
  detail: (id) => api.get(`/widgets/${id}/`),
  create: (data) => api.post('/widgets/', data),
  update: (id, data) => api.put(`/widgets/${id}/`, data),
  patch: (id, data) => api.patch(`/widgets/${id}/`, data),
  delete: (id) => api.delete(`/widgets/${id}/`),
}

// Contents API
export const contentsAPI = {
  list: (params) => api.get('/contents/', { params }),
  detail: (id) => api.get(`/contents/${id}/`),
  create: (data) => api.post('/contents/', data),
  update: (id, data) => api.put(`/contents/${id}/`, data),
  patch: (id, data) => api.patch(`/contents/${id}/`, data),
  delete: (id) => api.delete(`/contents/${id}/`),
  downloadToScreen: (id, data) => api.post(`/contents/${id}/download_to_screen/`, data),
  retryDownload: (id, data) => api.post(`/contents/${id}/retry_download/`, data),
  upload: (id, file, data = {}) => {
    console.log('[API] uploadContent called', {
      contentId: id,
      fileName: file?.name,
      fileSize: file?.size,
      fileType: file?.type,
      additionalData: data
    })
    
    // Validate file
    if (!file) {
      console.error('[API] uploadContent: No file provided')
      return Promise.reject(new Error('No file provided'))
    }
    
    const formData = new FormData()
    formData.append('file', file)
    
    // Append additional data if provided
    Object.keys(data).forEach(key => {
      formData.append(key, data[key])
      console.log(`[API] uploadContent: Added form field "${key}":`, data[key])
    })
    
    // Log FormData contents (for debugging)
    console.log('[API] uploadContent: FormData prepared', {
      hasFile: formData.has('file'),
      fileInFormData: file,
      formDataKeys: Array.from(formData.keys())
    })
    
    // DO NOT set Content-Type manually - let axios set it with boundary
    // Setting it manually breaks multipart/form-data boundary
    return api.post(`/contents/${id}/upload/`, formData, {
      // Remove manual Content-Type header - axios will set it automatically with boundary
      // headers: { 'Content-Type': 'multipart/form-data' }, // ❌ WRONG - breaks boundary
    })
  },
  download: (id, params) => api.get(`/contents/${id}/download/`, { params }),
  verifyIntegrity: (id, data) => api.post(`/contents/${id}/verify_integrity/`, data),
}

// Schedules API
export const schedulesAPI = {
  list: (params) => api.get('/schedules/', { params }),
  detail: (id) => api.get(`/schedules/${id}/`),
  create: (data) => api.post('/schedules/', data),
  update: (id, data) => api.put(`/schedules/${id}/`, data),
  patch: (id, data) => api.patch(`/schedules/${id}/`, data),
  delete: (id) => api.delete(`/schedules/${id}/`),
  execute: (id, data) => api.post(`/schedules/${id}/execute/`, data),
  dueSchedules: (params) => api.get('/schedules/due_schedules/', { params }),
  conflicting: (params) => api.get('/schedules/conflicting/', { params }),
}

// Commands API
export const commandsAPI = {
  list: (params) => api.get('/commands/', { params }),
  detail: (id) => api.get(`/commands/${id}/`),
  create: (data) => api.post('/commands/', data),
  update: (id, data) => api.put(`/commands/${id}/`, data),
  patch: (id, data) => api.patch(`/commands/${id}/`, data),
  delete: (id) => api.delete(`/commands/${id}/`),
  execute: (id, data = {}) => api.post(`/commands/${id}/execute/`, data),
  retry: (id) => api.post(`/commands/${id}/retry/`),
  status: (params) => api.get('/commands/status/', { params }),
  pending: (params) => api.get('/commands/pending/', { params }),
}

// Logs API
export const logsAPI = {
  screenStatus: {
    list: (params) => api.get('/logs/screen-status/', { params }),
    detail: (id) => api.get(`/logs/screen-status/${id}/`),
    summary: (params) => api.get('/logs/screen-status/summary/', { params }),
  },
  contentDownload: {
    list: (params) => api.get('/logs/content-download/', { params }),
    detail: (id) => api.get(`/logs/content-download/${id}/`),
    summary: (params) => api.get('/logs/content-download/summary/', { params }),
  },
  commandExecution: {
    list: (params) => api.get('/logs/command-execution/', { params }),
    detail: (id) => api.get(`/logs/command-execution/${id}/`),
    summary: (params) => api.get('/logs/command-execution/summary/', { params }),
  },
}

// Analytics API
export const analyticsAPI = {
  screenStatistics: (params) => api.get('/analytics/screens/', { params }),
  screenDetail: (id) => api.get(`/analytics/screens/${id}/`),
  commandStatistics: (params) => api.get('/analytics/commands/', { params }),
  contentStatistics: (params) => api.get('/analytics/content/', { params }),
  templateStatistics: (params) => api.get('/analytics/templates/', { params }),
  activityTrends: (params) => api.get('/analytics/activity/', { params }),
}

// Bulk Operations API
export const bulkOperationsAPI = {
  // Screens
  screensDelete: (data) => api.post('/screens/bulk/delete/', data),
  screensUpdate: (data) => api.post('/screens/bulk/update/', data),
  screensActivateTemplate: (data) => api.post('/screens/bulk/activate_template/', data),
  screensSendCommand: (data) => api.post('/screens/bulk/send_command/', data),
  
  // Templates
  templatesDelete: (data) => api.post('/templates/bulk/delete/', data),
  templatesUpdate: (data) => api.post('/templates/bulk/update/', data),
  templatesActivate: (data) => api.post('/templates/bulk/activate/', data),
  templatesActivateOnScreens: (data) => api.post('/templates/bulk/activate_on_screens/', data),
  
  // Contents
  contentsDelete: (data) => api.post('/contents/bulk/delete/', data),
  contentsUpdate: (data) => api.post('/contents/bulk/update/', data),
  contentsDownload: (data) => api.post('/contents/bulk/download/', data),
  contentsRetry: (data) => api.post('/contents/bulk/retry/', data),
  
  // Schedules
  schedulesDelete: (data) => api.post('/schedules/bulk/delete/', data),
  schedulesUpdate: (data) => api.post('/schedules/bulk/update/', data),
  schedulesActivate: (data) => api.post('/schedules/bulk/activate/', data),
  schedulesExecute: (data) => api.post('/schedules/bulk/execute/', data),
  
  // Commands
  commandsDelete: (data) => api.post('/commands/bulk/delete/', data),
  commandsExecute: (data) => api.post('/commands/bulk/execute/', data),
  commandsRetry: (data) => api.post('/commands/bulk/retry/', data),
}

// Content Validation API
export const contentValidationAPI = {
  validate: (file, contentType, filename) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('content_type', contentType)
    if (filename) {
      formData.append('filename', filename)
    }
    // DO NOT set Content-Type manually - let axios set it automatically with boundary
    // The request interceptor will handle removing the default 'application/json' header
    return api.post('/content-validation/validate/', formData)
  },
  validateBulk: (files, contentTypes, filenames) => {
    const formData = new FormData()
    files.forEach((file, index) => {
      formData.append('files', file)
    })
    if (contentTypes) {
      contentTypes.forEach((type, index) => {
        formData.append('content_types', type)
      })
    }
    if (filenames) {
      filenames.forEach((name, index) => {
        formData.append('filenames', name)
      })
    }
    // DO NOT set Content-Type manually - let axios set it automatically with boundary
    // The request interceptor will handle removing the default 'application/json' header
    return api.post('/content-validation/bulk/', formData)
  },
}

// Core Infrastructure API
export const coreAPI = {
  // Audit Logs
  auditLogs: {
    list: (params) => api.get('/core/audit-logs/', { params }),
    detail: (id) => api.get(`/core/audit-logs/${id}/`),
    summary: (params) => api.get('/core/audit-logs/summary/', { params }),
  },
  // Backups
  backups: {
    list: (params) => api.get('/core/backups/', { params }),
    detail: (id) => api.get(`/core/backups/${id}/`),
    trigger: (data) => api.post('/core/backups/trigger/', data),
    verify: (id) => api.post(`/core/backups/${id}/verify/`),
    cleanup: () => api.post('/core/backups/cleanup/'),
  },
}

// Admin API (SuperAdmin only)
export const adminAPI = {
  // Error Logs
  errors: {
    list: (params) => api.get('/admin/errors/', { params }),
    detail: (id) => api.get(`/admin/errors/${id}/`),
    resolve: (id) => api.patch(`/admin/errors/${id}/resolve/`),
    stats: (params) => api.get('/admin/errors/stats/', { params }),
  },
}

// WebSocket URL helper
export const getWebSocketURL = (path, token = null) => {
  const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const wsHost = import.meta.env.VITE_WS_HOST || window.location.host
  const baseURL = `${wsProtocol}//${wsHost}`
  const url = `${baseURL}${path}`
  return token ? `${url}?token=${token}` : url
}

export default api
