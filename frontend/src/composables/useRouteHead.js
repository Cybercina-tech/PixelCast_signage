import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useHead, useSeoMeta } from '@unhead/vue'
import {
  DEFAULT_OG_LOCALE,
  DEFAULT_TWITTER_SITE,
  DEFAULT_DESCRIPTION,
  SITE_NAME,
  getDefaultOgImageUrl,
  getSiteOrigin,
} from '@/seo/siteConfig'
import { SEO_BY_ROUTE_NAME, getDefaultSeo } from '@/seo/presets'
import {
  buildBreadcrumbGraph,
  buildFaqNode,
  buildSoftwareApplicationGraph,
  buildWebPageGraph,
} from '@/seo/jsonLd'
import { BLOG_FAQ_ITEMS } from '@/seo/blogFaq'

export function useRouteHead() {
  const route = useRoute()

  const resolved = computed(() => {
    const fromMeta = route.meta?.seo
    const fromMap = route.name ? SEO_BY_ROUTE_NAME[route.name] : null
    return { ...getDefaultSeo(), ...fromMap, ...fromMeta }
  })

  const origin = computed(() => getSiteOrigin())

  const canonicalPath = computed(() => {
    const p = route.path || '/'
    if (p.length > 1 && p.endsWith('/')) return p.slice(0, -1)
    return p
  })

  const canonicalUrl = computed(() => {
    const o = origin.value
    if (!o) return ''
    const path = canonicalPath.value === '' ? '/' : canonicalPath.value
    return `${o}${path === '/' ? '' : path}`
  })

  const routeName = computed(() => String(route.name || ''))

  const title = computed(() => resolved.value.title || `${SITE_NAME} — Digital Signage`)
  const description = computed(() => resolved.value.description || DEFAULT_DESCRIPTION)
  const robots = computed(() => resolved.value.robots || 'noindex, nofollow')

  const ogImage = computed(() => {
    if (resolved.value.ogImage) return resolved.value.ogImage
    return getDefaultOgImageUrl() || undefined
  })

  const breadcrumbItems = computed(() => {
    const map = {
      'solution-browser-signage': [
        { name: 'Home', path: '/' },
        { name: 'Solutions', path: '/solutions/browser-based-digital-signage-software' },
      ],
      'guide-smart-tv-signboard': [
        { name: 'Home', path: '/' },
        { name: 'Guides', path: '/guides/turn-smart-tv-into-digital-signboard' },
      ],
      'solution-free-menu-boards': [
        { name: 'Home', path: '/' },
        { name: 'Solutions', path: '/solutions/free-digital-signage-menu-boards' },
      ],
      'solution-cloud-tv-browser': [
        { name: 'Home', path: '/' },
        { name: 'Solutions', path: '/solutions/cloud-digital-signage-tv-browser' },
      ],
      pricing: [
        { name: 'Home', path: '/' },
        { name: 'Pricing', path: '/pricing' },
      ],
    }
    return map[routeName.value] || []
  })

  useSeoMeta({
    title,
    description,
    robots,
    ogTitle: title,
    ogDescription: description,
    ogUrl: canonicalUrl,
    ogType: 'website',
    ogSiteName: SITE_NAME,
    ogLocale: DEFAULT_OG_LOCALE,
    ogImage,
    twitterCard: 'summary_large_image',
    twitterSite: DEFAULT_TWITTER_SITE,
    twitterTitle: title,
    twitterDescription: description,
    twitterImage: ogImage,
  })

  const jsonLd = computed(() => {
    const o = origin.value
    if (!o) return null
    const t = title.value
    const d = description.value
    const name = routeName.value

    if (name === 'blog') {
      const base = buildWebPageGraph(o, {
        path: '/blog',
        title: t,
        description: d,
        type: 'Blog',
      })
      return {
        '@context': 'https://schema.org',
        '@graph': [...base['@graph'], buildFaqNode(`${o}/blog`, BLOG_FAQ_ITEMS)],
      }
    }

    if (name === 'blog-post') {
      return null
    }

    if (robots.value.includes('noindex')) {
      return null
    }
    const path = canonicalPath.value || '/'
    const baseGraph = buildWebPageGraph(o, {
      path,
      title: t,
      description: d,
      type: 'WebPage',
    })
    const extraNodes = []

    if (breadcrumbItems.value.length) {
      extraNodes.push(buildBreadcrumbGraph(o, path, breadcrumbItems.value))
    }

    if (name === 'pricing') {
      extraNodes.push(
        buildSoftwareApplicationGraph(o, {
          path: '/pricing',
          name: 'PixelCast Cloud Digital Signage',
          description:
            'Cloud digital signage software for teams managing TV browsers, menu boards, and multi-location displays.',
          offers: [
            { name: 'Free plan', price: '0', currency: 'USD', path: '/pricing' },
            { name: 'Per-screen plan', price: '29', currency: 'USD', path: '/pricing' },
          ],
        })
      )
    }

    if (
      name === 'solution-browser-signage' ||
      name === 'guide-smart-tv-signboard' ||
      name === 'solution-free-menu-boards' ||
      name === 'solution-cloud-tv-browser'
    ) {
      extraNodes.push(buildFaqNode(`${o}${path === '/' ? '/' : path.replace(/\/$/, '')}`, BLOG_FAQ_ITEMS))
    }

    if (!extraNodes.length) {
      return baseGraph
    }
    return {
      '@context': 'https://schema.org',
      '@graph': [...baseGraph['@graph'], ...extraNodes],
    }
  })

  useHead({
    link: computed(() => {
      const href = canonicalUrl.value
      if (!href) return []
      return [{ rel: 'canonical', href }]
    }),
    script: computed(() => {
      const data = jsonLd.value
      if (!data) return []
      return [
        {
          key: 'pixelcast-jsonld',
          type: 'application/ld+json',
          children: JSON.stringify(data),
        },
      ]
    }),
  })
}
