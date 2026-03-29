/**
 * Origin used for API-relative dev setups (e.g. VITE_API_BASE_URL=/api).
 */
export function getBackendOrigin() {
  const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'
  if (apiBase.startsWith('http://') || apiBase.startsWith('https://')) {
    try {
      const parsed = new URL(apiBase)
      return `${parsed.protocol}//${parsed.host}`
    } catch {
      return 'http://localhost:8000'
    }
  }
  return typeof window !== 'undefined' ? window.location.origin : 'http://localhost:8000'
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
export function resolveMediaFileUrl(fileUrl) {
  if (fileUrl == null || String(fileUrl).trim() === '') return null

  const url = String(fileUrl).trim()

  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url
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
