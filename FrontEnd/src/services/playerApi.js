import axios from 'axios'

// THE IoT ESCAPE PLAN: Use /iot/ namespace to bypass strict /api/ security filters
// IoT base URL - separate from standard API to bypass authentication middleware
const IOT_BASE_URL = import.meta.env.VITE_IOT_BASE_URL || 'http://localhost:8000/iot'

// Media base URL - backend server URL for serving media files
export const MEDIA_BASE_URL = import.meta.env.VITE_MEDIA_BASE_URL || 'http://localhost:8000'

// Create axios instance for player API (IoT endpoints)
// CRITICAL: Do NOT send Authorization headers - these are IoT endpoints
const playerApi = axios.create({
  baseURL: IOT_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    // Explicitly DO NOT include Authorization header
  },
  timeout: 10000 // 10 second timeout
})

// Ensure no Authorization header is sent for IoT requests
playerApi.interceptors.request.use((config) => {
  // Remove any Authorization header that might have been set
  delete config.headers.Authorization
  delete config.headers.authorization
  return config
})

// Screen ID storage (ONLY method - no tokens)
let screenId = null

/**
 * Set screen ID (ONLY authentication method)
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
 * ONLY uses screen_id - no token logic
 */
export const fetchTemplate = async () => {
  if (!screenId) {
    throw new Error('screen_id is required. Please pair your screen first.')
  }

  try {
    // THE IoT ESCAPE PLAN: Use /iot/player/template/ instead of /api/player/template/
    const response = await playerApi.get('/player/template/', {
      params: {
        screen_id: screenId
      },
      // Ensure no Authorization header is sent
      headers: {
        'Content-Type': 'application/json'
      }
    })

    return response.data
  } catch (error) {
    if (error.response) {
      // Server responded with error
      throw new Error(error.response.data?.error || error.response.data?.message || `HTTP ${error.response.status}`)
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
 * ONLY uses screen_id - no token logic
 */
export const sendHeartbeat = async (systemInfo = {}) => {
  if (!screenId) {
    const error = new Error('screen_id is required. Please pair your screen first.')
    console.error('[playerApi] sendHeartbeat: Missing screen_id')
    throw error
  }

  // Build payload with screen_id and system info
  const payload = {
    screen_id: screenId,
    ...systemInfo
  }
  
  console.log('[playerApi] sendHeartbeat: Sending request', {
    url: '/iot/screens/heartbeat/',  // THE IoT ESCAPE PLAN: Using /iot/ namespace
    screenId: screenId,
    hasSystemInfo: Object.keys(systemInfo).length > 0
  })
  
  try {
    // THE IoT ESCAPE PLAN: Use /iot/screens/heartbeat/ instead of /api/screens/heartbeat/
    const response = await playerApi.post('/screens/heartbeat/', payload, {
      // Ensure no Authorization header is sent
      headers: {
        'Content-Type': 'application/json'
      }
    })

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
      data: error.response?.data
    })
    
    if (error.response) {
      // Server responded with error
      const errorData = error.response.data || {}
      const errorMessage = errorData.error || errorData.message || errorData.detail || `HTTP ${error.response.status}`
      
      console.error('[playerApi] sendHeartbeat: Server error details', {
        status: error.response.status,
        message: errorMessage
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

/**
 * Fetch pending commands for the player
 * ONLY uses screen_id - no token logic
 */
export const fetchPendingCommands = async () => {
  if (!screenId) {
    throw new Error('screen_id is required. Please pair your screen first.')
  }

  try {
    // THE IoT ESCAPE PLAN: Use /iot/commands/pending/ instead of /api/commands/pending/
    const response = await playerApi.get('/commands/pending/', {
      params: {
        screen_id: screenId,
        limit: 10
      },
      headers: {
        'Content-Type': 'application/json'
      }
    })

    return response.data
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data?.error || error.response.data?.message || `HTTP ${error.response.status}`)
    } else if (error.request) {
      throw new Error('Network error: No response from server')
    } else {
      throw new Error(error.message || 'Request failed')
    }
  }
}

/**
 * Update command status after execution
 * ONLY uses screen_id - no token logic
 */
export const updateCommandStatus = async (commandId, status, errorMessage = '', responsePayload = {}) => {
  if (!screenId) {
    throw new Error('screen_id is required. Please pair your screen first.')
  }

  if (!commandId) {
    throw new Error('command_id is required')
  }

  const payload = {
    screen_id: screenId,
    command_id: commandId,
    status: status, // 'done' or 'failed'
    error_message: errorMessage,
    response_payload: responsePayload
  }

  try {
    // THE IoT ESCAPE PLAN: Use /iot/commands/status/ instead of /api/commands/{id}/status/
    const response = await playerApi.post('/commands/status/', payload, {
      headers: {
        'Content-Type': 'application/json'
      }
    })

    return response.data
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data?.error || error.response.data?.message || `HTTP ${error.response.status}`)
    } else if (error.request) {
      throw new Error('Network error: No response from server')
    } else {
      throw new Error(error.message || 'Request failed')
    }
  }
}

// Export default API object
const playerAPI = {
  setScreenId,
  getScreenId,
  fetchTemplate,
  sendHeartbeat,
  fetchPendingCommands,
  updateCommandStatus
}

export default playerAPI
