/**
 * URL utility functions for handling media URLs
 */

// Backend media base URL - for serving media files
const MEDIA_BASE_URL = import.meta.env.VITE_MEDIA_BASE_URL || 'http://localhost:8000'

/**
 * Ensure URL is absolute (starts with http:// or https://)
 * If relative, prepend the backend media base URL
 * 
 * @param {string} url - The URL to make absolute
 * @returns {string|null} - Absolute URL or null if url is empty
 */
export function ensureAbsoluteUrl(url) {
  if (!url) {
    return null
  }
  
  // If already absolute, return as is
  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url
  }
  
  // If starts with /, it's a root-relative URL
  if (url.startsWith('/')) {
    return `${MEDIA_BASE_URL}${url}`
  }
  
  // Otherwise, it's a relative URL - prepend media base URL with /
  return `${MEDIA_BASE_URL}/${url}`
}

/**
 * Get content file URL - prefers absolute_file_url, falls back to file_url
 * 
 * @param {object} content - Content object with file_url and/or absolute_file_url
 * @returns {string|null} - Absolute URL or null
 */
export function getContentFileUrl(content) {
  if (!content) {
    return null
  }
  
  // Prefer absolute_file_url if available
  if (content.absolute_file_url) {
    return ensureAbsoluteUrl(content.absolute_file_url)
  }
  
  // Fallback to file_url
  if (content.file_url) {
    return ensureAbsoluteUrl(content.file_url)
  }
  
  // Fallback to secure_url (for player context)
  if (content.secure_url) {
    return ensureAbsoluteUrl(content.secure_url)
  }
  
  return null
}

export { MEDIA_BASE_URL }

