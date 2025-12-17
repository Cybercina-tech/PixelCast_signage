import axios from 'axios'

// API base URL - update this to match your backend
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized - redirect to login
      localStorage.removeItem('auth_token')
      localStorage.removeItem('refresh_token')
      if (window.location.pathname !== '/login' && window.location.pathname !== '/') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

// Authentication API
export const authAPI = {
  login: (credentials) => api.post('/auth/login/', credentials),
  logout: (data) => api.post('/auth/logout/', data),
  token: (credentials) => api.post('/auth/token/', credentials),
  refreshToken: (refresh) => api.post('/auth/token/refresh/', { refresh }),
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
  updateMe: (data) => api.put('/users/update_me/', data),
  changePassword: (id, data) => api.post(`/users/${id}/change_password/`, data),
  changeRole: (id, data) => api.post(`/users/${id}/change_role/`, data),
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
    const formData = new FormData()
    formData.append('file', file)
    Object.keys(data).forEach(key => {
      formData.append(key, data[key])
    })
    return api.post(`/contents/${id}/upload/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
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

// WebSocket URL helper
export const getWebSocketURL = (path, token = null) => {
  const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const wsHost = import.meta.env.VITE_WS_HOST || window.location.host
  const baseURL = `${wsProtocol}//${wsHost}`
  const url = `${baseURL}${path}`
  return token ? `${url}?token=${token}` : url
}

export default api
