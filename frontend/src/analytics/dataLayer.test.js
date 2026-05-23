import { beforeEach, describe, expect, it } from 'vitest'
import {
  getSeoIntentKeyword,
  getSeoPageGroup,
  pushVirtualPageView,
} from './dataLayer'

describe('dataLayer SEO mappings', () => {
  beforeEach(() => {
    window.dataLayer = []
  })

  it('maps intent pages to exact keywords', () => {
    expect(getSeoIntentKeyword('/solutions/browser-based-digital-signage-software')).toBe(
      'browser-based digital signage software'
    )
    expect(getSeoIntentKeyword('/guides/turn-smart-tv-into-digital-signboard')).toBe(
      'how to turn a smart TV into a digital signboard'
    )
  })

  it('maps routes to SEO page groups', () => {
    expect(getSeoPageGroup('/')).toBe('landing')
    expect(getSeoPageGroup('/blog/some-post')).toBe('blog')
    expect(getSeoPageGroup('/solutions/free-digital-signage-menu-boards')).toBe('intent_solution')
  })

  it('pushes seo intent view for intent routes', () => {
    pushVirtualPageView({
      path: '/solutions/cloud-digital-signage-tv-browser',
      fullPath: '/solutions/cloud-digital-signage-tv-browser',
    })
    expect(window.dataLayer).toHaveLength(2)
    expect(window.dataLayer[0]).toMatchObject({
      event: 'virtual_page_view',
      seo_page_group: 'intent_solution',
      seo_intent_keyword: 'cloud digital signage for running on TV browser',
    })
    expect(window.dataLayer[1]).toMatchObject({
      event: 'seo_intent_page_view',
      seo_page_group: 'intent_solution',
    })
  })
})
