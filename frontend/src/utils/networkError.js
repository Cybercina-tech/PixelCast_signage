/**
 * Detect transient client/network failures (no HTTP response).
 */
export function isTransientNetworkError(error) {
  if (!error) return false
  if (error.response) return false

  if (typeof navigator !== 'undefined' && navigator.onLine === false) {
    return true
  }

  const msg = String(error.message || error.code || '').toLowerCase()
  if (msg.includes('network error')) return true
  if (msg.includes('err_network_changed')) return true
  if (msg.includes('network_changed')) return true
  if (msg.includes('econnaborted')) return true
  if (msg.includes('timeout')) return true
  if (error.code === 'ERR_NETWORK') return true
  if (error.code === 'ECONNABORTED') return true

  return false
}

export const OFFLINE_ERROR_CODE = 'offline_or_unstable'
