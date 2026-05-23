import { getBrowserApiBaseUrl, isDockerServiceHostname } from '@/utils/apiBaseUrl'

export function getBackendOrigin() {
  if (typeof window !== 'undefined') {
    try {
      const apiBase = getBrowserApiBaseUrl()
      const u = new URL(apiBase, window.location.origin)
      return `${u.protocol}//${u.host}`
    } catch {
      return window.location.origin
    }
  }
  const apiBase = import.meta.env.VITE_API_BASE_URL || '/api'
  if (apiBase.startsWith('http://') || apiBase.startsWith('https://')) {
    try {
      const parsed = new URL(apiBase)
      if (isDockerServiceHostname(parsed.hostname)) {
        return 'http://localhost:8000'
      }
      return `${parsed.protocol}//${parsed.host}`
    } catch {
      return 'http://localhost:8000'
    }
  }
  return 'http://localhost:8000'
}

/**
 * Resolve a media file URL for use in <img src> / <video src>.
 *
 * - Absolute http(s) URLs are returned unchanged.
 * - Relative paths (/media/...) get the correct origin:
 *   - If VITE_API_BASE_URL is absolute (e.g. http://localhost:8000/api), use that host.
 *   - If it is relative (e.g. /api from Docker + Vite), use window.location.origin so
 *     /media/ is requested from the dev server (Vite proxies /media to Django).
 */
function isInternalMediaHostname(hostname) {
  if (!hostname) return true
  const h = String(hostname).toLowerCase()
  if (isDockerServiceHostname(h)) return true
  if (h === 'localhost' || h === '127.0.0.1' || h === '0.0.0.0' || h === 'backend') {
    return true
  }
  return false
}

export function resolveMediaFileUrl(fileUrl) {
  if (fileUrl == null || String(fileUrl).trim() === '') return null

  const url = String(fileUrl).trim()

  if (url.startsWith('http://') || url.startsWith('https://')) {
    try {
      const parsed = new URL(url)
      const pageOrigin =
        typeof window !== 'undefined' && window.location?.origin
          ? window.location.origin
          : getBackendOrigin()
      if (isInternalMediaHostname(parsed.hostname)) {
        return `${pageOrigin}${parsed.pathname}${parsed.search}${parsed.hash}`
      }
      if (
        typeof window !== 'undefined' &&
        window.location?.hostname &&
        parsed.hostname !== window.location.hostname
      ) {
        return `${pageOrigin}${parsed.pathname}${parsed.search}${parsed.hash}`
      }
      return url
    } catch {
      return url
    }
  }

  const origin = getBackendOrigin()

  if (url.startsWith('/media/') || url.startsWith('/static/')) {
    return `${origin}${url}`
  }

  const clean = url.startsWith('/') ? url.slice(1) : url
  if (clean.includes('media/') || clean.includes('static/')) {
    return `${origin}/${clean}`
  }

  return `${origin}/media/${clean}`
}
