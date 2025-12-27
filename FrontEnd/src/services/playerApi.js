import axios from 'axios'

// API base URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

// Create axios instance for player API
const playerApi = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000 // 10 second timeout
})

// Credentials storage (legacy - for backward compatibility)
let authToken = null
let secretKey = null
// Screen ID storage (new method - after pairing, only screen_id is stored)
let screenId = null

/**
 * Set player credentials (legacy method)
 */
export const setCredentials = (token, secret) => {
  authToken = token
  secretKey = secret
  console.log('[playerApi] Credentials set (legacy method)', {
    hasToken: !!authToken,
    hasSecret: !!secretKey,
    tokenLength: authToken?.length || 0,
    secretLength: secretKey?.length || 0,
    tokenPrefix: authToken ? authToken.substring(0, 8) + '...' : 'N/A'
  })
}

/**
 * Set screen ID (new method - after pairing, only screen_id is stored)
 */
export const setScreenId = (id) => {
  screenId = id
  console.log('[playerApi] Screen ID set', {
    hasScreenId: !!screenId,
    screenId: screenId
  })
}

/**
 * Get screen ID
 */
export const getScreenId = () => {
  return screenId
}

/**
 * Fetch template for player
 */
export const fetchTemplate = async () => {
  if (!authToken || !secretKey) {
    throw new Error('Player credentials not configured')
  }

  try {
    const response = await playerApi.get('/player/template/', {
      params: {
        auth_token: authToken,
        secret_key: secretKey
      }
    })

    return response.data
  } catch (error) {
    if (error.response) {
      // Server responded with error
      throw new Error(error.response.data?.error || `HTTP ${error.response.status}`)
    } else if (error.request) {
      // Request made but no response
      throw new Error('Network error: No response from server')
    } else {
      // Error in request setup
      throw new Error(error.message || 'Request failed')
    }
  }
}

/**
 * Send heartbeat with system information
 */
export const sendHeartbeat = async (systemInfo = {}) => {
  if (!authToken || !secretKey) {
    const error = new Error('Player credentials not configured')
    console.error('[playerApi] sendHeartbeat: Missing credentials', {
      hasAuthToken: !!authToken,
      hasSecretKey: !!secretKey
    })
    throw error
  }

  // Log credentials status (masked for security)
  console.log('[playerApi] sendHeartbeat: Preparing heartbeat', {
    hasAuthToken: !!authToken,
    hasSecretKey: !!secretKey,
    authTokenPrefix: authToken ? authToken.substring(0, 8) + '...' : 'MISSING',
    secretKeyLength: secretKey?.length || 0,
    hasSystemInfo: Object.keys(systemInfo).length > 0
  })

  try {
    const payload = {
      auth_token: authToken,
      secret_key: secretKey,
      ...systemInfo
    }
    
    console.log('[playerApi] sendHeartbeat: Sending request', {
      url: '/screens/heartbeat/',
      hasAuthToken: !!payload.auth_token,
      hasSecretKey: !!payload.secret_key,
      authTokenLength: payload.auth_token?.length || 0,
      secretKeyLength: payload.secret_key?.length || 0,
      systemInfoKeys: Object.keys(systemInfo)
    })
    
    const response = await playerApi.post('/screens/heartbeat/', payload)

    console.log('[playerApi] sendHeartbeat: Success', {
      status: response.status,
      screenId: response.data?.screen_id,
      isOnline: response.data?.is_online
    })

    return response.data
  } catch (error) {
    console.error('[playerApi] sendHeartbeat: Error', {
      message: error.message,
      status: error.response?.status,
      statusText: error.response?.statusText,
      statusText: error.response?.statusText,
      data: error.response?.data,
      message: error.message
    })
    
    if (error.response) {
      // Server responded with error
      const errorData = error.response.data || {}
      const errorMessage = errorData.error || errorData.message || errorData.detail || `HTTP ${error.response.status}`
      const errorDetails = errorData.details || errorData
      
      console.error('[playerApi] sendHeartbeat: Server error details', {
        status: error.response.status,
        message: errorMessage,
        details: errorDetails
      })
      
      throw new Error(errorMessage)
    } else if (error.request) {
      // Request made but no response
      console.error('[playerApi] sendHeartbeat: No response from server')
      throw new Error('Network error: No response from server')
    } else {
      // Error in request setup
      console.error('[playerApi] sendHeartbeat: Request setup error', error.message)
      throw new Error(error.message || 'Request failed')
    }
  }
}

// Export default API object
const playerAPI = {
  setCredentials,
  setScreenId,
  getScreenId,
  fetchTemplate,
  sendHeartbeat
}

export default playerAPI

