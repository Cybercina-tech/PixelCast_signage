# SEO Measurement Mapping

`frontend/src/analytics/dataLayer.js` now emits two SEO-aware events:

- `virtual_page_view` with:
  - `seo_page_group`
  - `seo_intent_keyword` (only for intent pages)
- `seo_intent_page_view` for dedicated intent routes

## Page group mapping

- `/` -> `landing`
- `/pricing` -> `pricing`
- `/blog` and `/blog/:slug` -> `blog`
- `/solutions/*` -> `intent_solution`
- `/guides/*` -> `intent_guide`
- everything else -> `other`

## Intent keyword mapping

- `/solutions/browser-based-digital-signage-software`
- `/guides/turn-smart-tv-into-digital-signboard`
- `/solutions/free-digital-signage-menu-boards`
- `/solutions/cloud-digital-signage-tv-browser`

Each mapped route sends the exact target keyword string for SEO funnel reporting in GTM/GA4.
