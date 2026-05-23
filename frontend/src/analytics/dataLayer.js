/**
 * Google Tag Manager / Google Ads dataLayer helpers (SPA-safe).
 */

export function initDataLayer() {
  if (typeof window === 'undefined') return
  window.dataLayer = window.dataLayer || []
}

/**
 * @param {string} eventName
 * @param {Record<string, unknown>} [params]
 */
export function pushDataLayerEvent(eventName, params = {}) {
  initDataLayer()
  window.dataLayer.push({
    event: eventName,
    ...params,
  })
}

/**
 * Virtual page views for SPA route changes (map to GA4 page_view in GTM).
 */
export function pushVirtualPageView(to) {
  initDataLayer()
  const title = typeof document !== 'undefined' ? document.title : ''
  const seoIntentKeyword = getSeoIntentKeyword(to.path || '')
  const seoPageGroup = getSeoPageGroup(to.path || '')
  window.dataLayer.push({
    event: 'virtual_page_view',
    page_path: to.fullPath,
    page_title: title,
    page_location:
      typeof window !== 'undefined' ? `${window.location.origin}${to.fullPath}` : '',
    seo_page_group: seoPageGroup,
    seo_intent_keyword: seoIntentKeyword || undefined,
  })
  if (seoIntentKeyword) {
    window.dataLayer.push({
      event: 'seo_intent_page_view',
      seo_page_group: seoPageGroup,
      seo_intent_keyword: seoIntentKeyword,
      page_path: to.path,
    })
  }
}

export function pushCtaClick(ctaId, label, extra = {}) {
  pushDataLayerEvent('cta_click', {
    cta_id: ctaId,
    cta_label: label,
    ...extra,
  })
}

export function pushSignUp(method = 'email') {
  pushDataLayerEvent('sign_up', { method })
}

export function pushLogin(method = 'password') {
  pushDataLayerEvent('login', { method })
}

export function getSeoIntentKeyword(path) {
  const normalizedPath = String(path || '').replace(/\/$/, '') || '/'
  const keywordByPath = {
    '/solutions/browser-based-digital-signage-software': 'browser-based digital signage software',
    '/guides/turn-smart-tv-into-digital-signboard': 'how to turn a smart TV into a digital signboard',
    '/solutions/free-digital-signage-menu-boards': 'free digital signage for menu boards',
    '/solutions/cloud-digital-signage-tv-browser': 'cloud digital signage for running on TV browser',
  }
  return keywordByPath[normalizedPath] || ''
}

export function getSeoPageGroup(path) {
  const normalizedPath = String(path || '').replace(/\/$/, '') || '/'
  if (normalizedPath === '/blog' || normalizedPath.startsWith('/blog/')) return 'blog'
  if (normalizedPath.startsWith('/solutions/')) return 'intent_solution'
  if (normalizedPath.startsWith('/guides/')) return 'intent_guide'
  if (normalizedPath === '/pricing') return 'pricing'
  if (normalizedPath === '/') return 'landing'
  return 'other'
}
