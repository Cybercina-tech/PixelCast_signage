/**
 * Composable for collecting and sending system information
 * Collects: App Version, OS Version, Device Model, Screen Resolution, IP Address
 */

import { ref } from 'vue'

// Cache for system info to avoid repeated calculations
const systemInfoCache = ref(null)

function safeCapture(text, regex, idx = 1) {
  if (!text || typeof text !== 'string') return null
  const match = text.match(regex)
  if (!match || typeof match[idx] !== 'string') return null
  return match[idx]
}

/**
 * Get app version from package.json or environment
 */
function getAppVersion() {
  // Try to get from window.__APP_VERSION__ (set in vite.config.js)
  if (typeof window !== 'undefined' && window.__APP_VERSION__) {
    return window.__APP_VERSION__
  }
  
  // Try to get from import.meta.env
  if (import.meta.env?.VITE_APP_VERSION) {
    return import.meta.env.VITE_APP_VERSION
  }
  
  // Fallback
  return '1.0.0'
}

/**
 * Get OS version from user agent
 */
function getOSVersion() {
  if (typeof navigator === 'undefined') {
    return 'Unknown'
  }

  const userAgent = String(navigator.userAgent || navigator.vendor || window.opera || '')
  
  // Windows
  if (userAgent.indexOf('Windows NT 10.0') !== -1) return 'Windows 10'
  if (userAgent.indexOf('Windows NT 6.3') !== -1) return 'Windows 8.1'
  if (userAgent.indexOf('Windows NT 6.2') !== -1) return 'Windows 8'
  if (userAgent.indexOf('Windows NT 6.1') !== -1) return 'Windows 7'
  if (userAgent.indexOf('Windows NT 6.0') !== -1) return 'Windows Vista'
  if (userAgent.indexOf('Windows NT 5.1') !== -1) return 'Windows XP'
  if (userAgent.indexOf('Windows NT 5.0') !== -1) return 'Windows 2000'
  if (userAgent.indexOf('Windows') !== -1) return 'Windows'
  
  // macOS
  if (userAgent.indexOf('Mac OS X') !== -1) {
    const major = safeCapture(userAgent, /Mac OS X (\d+)[._](\d+)/, 1)
    const minor = safeCapture(userAgent, /Mac OS X (\d+)[._](\d+)/, 2)
    if (major && minor) {
      return `macOS ${major}.${minor}`
    }
    return 'macOS'
  }
  
  // iOS
  if (/iPad|iPhone|iPod/.test(userAgent) && !window.MSStream) {
    const major = safeCapture(userAgent, /OS (\d+)[._](\d+)/, 1)
    const minor = safeCapture(userAgent, /OS (\d+)[._](\d+)/, 2)
    if (major && minor) {
      return `iOS ${major}.${minor}`
    }
    return 'iOS'
  }
  
  // Android
  if (userAgent.indexOf('Android') !== -1) {
    const major = safeCapture(userAgent, /Android (\d+)[._](\d+)/, 1)
    const minor = safeCapture(userAgent, /Android (\d+)[._](\d+)/, 2)
    if (major && minor) {
      return `Android ${major}.${minor}`
    }
    return 'Android'
  }
  
  // Linux
  if (userAgent.indexOf('Linux') !== -1) {
    return 'Linux'
  }
  
  // Chrome OS
  if (userAgent.indexOf('CrOS') !== -1) {
    return 'Chrome OS'
  }
  
  return 'Unknown'
}

/**
 * Get device model from user agent
 */
function getDeviceModel() {
  if (typeof navigator === 'undefined') {
    return 'Unknown'
  }

  const userAgent = String(navigator.userAgent || navigator.vendor || window.opera || '')
  
  // Try to get device model from user agent
  // iPhone
  if (/iPhone/.test(userAgent)) {
    const model = safeCapture(userAgent, /iPhone\s*([^;]+)/, 1)
    if (model) {
      return `iPhone ${model.trim()}`
    }
    return 'iPhone'
  }
  
  // iPad
  if (/iPad/.test(userAgent)) {
    const match = userAgent.match(/iPad[^;]*/)
    if (match) {
      return match[0].trim()
    }
    return 'iPad'
  }
  
  // Android devices
  if (/Android/.test(userAgent)) {
    // Try to extract model from user agent
    const match = userAgent.match(/Android[^;]*(?:;|$)/)
    if (match) {
      // Try to find device model
      const model = safeCapture(userAgent, /\(([^)]+)\)/, 1)
      if (model) {
        return model.trim()
      }
    }
    return 'Android Device'
  }
  
  // Try to get from navigator.platform
  if (navigator.platform) {
    return navigator.platform
  }
  
  // Try to get from navigator.userAgentData (if available)
  if (navigator.userAgentData?.platform) {
    return navigator.userAgentData.platform
  }
  
  return 'Unknown Device'
}

/**
 * Get screen resolution
 */
function getScreenResolution() {
  if (typeof screen === 'undefined') {
    return { width: null, height: null }
  }
  
  return {
    width: screen.width || window.innerWidth,
    height: screen.height || window.innerHeight
  }
}

/**
 * Get client IP address (requires backend to extract from request)
 * This will be set by the backend when sending heartbeat
 */
function getClientIP() {
  // IP address is typically extracted server-side from request headers
  // We'll return null here and let the backend handle it
  return null
}

/**
 * Collect all system information
 */
export function collectSystemInfo() {
  // Return cached info if available
  if (systemInfoCache.value) {
    return systemInfoCache.value
  }
  
  const resolution = getScreenResolution()
  
  const info = {
    app_version: getAppVersion(),
    os_version: getOSVersion(),
    device_model: getDeviceModel(),
    screen_width: resolution.width,
    screen_height: resolution.height,
  }
  
  // Cache the info
  systemInfoCache.value = info
  
  return info
}

/**
 * Clear system info cache (useful for testing or when info might change)
 */
export function clearSystemInfoCache() {
  systemInfoCache.value = null
}

/**
 * Composable function
 */
export function useSystemInfo() {
  return {
    collectSystemInfo,
    clearSystemInfoCache,
    getAppVersion,
    getOSVersion,
    getDeviceModel,
    getScreenResolution,
  }
}

