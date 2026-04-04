# PixelCast / ScreenGram — SEO audit & implementation report

## 1. Project stack

| Layer | Technology |
|--------|------------|
| Frontend | Vue 3, Vue Router, Pinia, Vite |
| Head / meta | `@unhead/vue` (`useSeoMeta`, `useHead`) via `frontend/src/composables/useRouteHead.js` |
| Backend | Django (API, admin); SPA served by nginx in production |
| Build | `frontend/vite.config.js` — `seoStaticFilesPlugin` writes `robots.txt` and `sitemap.xml` into `dist/` |

## 2. SEO issues found (pre-work)

| Issue | Severity |
|--------|-----------|
| No `robots.txt` / `sitemap.xml` in production build | Critical |
| Inconsistent titles / descriptions (static `index.html` vs per-route) | Critical |
| No canonical, Open Graph, or Twitter tags globally | Important |
| No JSON-LD | Important |
| App and player routes should not compete in search | Important |
| No dedicated blog content for informational queries | Important |
| GA4 / GTM / dataLayer absent | Critical (measurement) |

## 3. Analytics / tracking issues found (pre-work)

- No GTM snippet or `dataLayer`.
- No SPA virtual page views for route changes.

## 4. Metadata & copy changes (implemented)

- **Central route SEO:** `frontend/src/seo/presets.js` — titles and descriptions keyed by route name (digital signage intent, soft UK phrasing where natural).
- **`index.html`:** Default title, description, basic OG/Twitter fallbacks for first paint.
- **Removed** imperative `document.title` / meta manipulation from Privacy, Terms, Data Center, Documentation, Docs Changelog (handled by `useRouteHead`).
- **Brand consistency:** “PicxelCast” → “PixelCast” in docs/changelog UI copy.

## 5. Digital signage keyword improvements

- Landing hero and feature-adjacent copy tuned for commercial displays, menu boards, LCD/LED, retail/hospitality without stuffing.
- Public presets use natural phrases: digital signage software, commercial displays, signage software, UK teams, etc.

## 6. Schema (JSON-LD)

- **Public indexable routes:** `Organization` + `WebSite` + `WebPage` graph via `buildWebPageGraph` in `frontend/src/seo/jsonLd.js`.
- **`/blog`:** `BlogPosting` + `WebPage` + `FAQPage` nodes via `buildBlogPostingWithFaq`.
- **`VITE_PUBLIC_REGION=UK`:** Adds `Organization.areaServed` for United Kingdom when set.

## 7. Blog

- **Route:** `/blog` → `frontend/src/pages/Blog.vue` (single long-form article + FAQ).
- **Internal links:** Landing nav/footer, Documentation intro; blog links to `/`, `/docs`, `/install`, `/signup`.

## 8. GA4 setup status

- **Not hard-coded.** Prefer GA4 **Configuration** tag inside **GTM** using `VITE_GTM_CONTAINER_ID`.
- Optional direct GA4 ID: `VITE_GA4_MEASUREMENT_ID` — document only; avoid loading GA4 twice (GTM + gtag).

## 9. GTM setup status

- **`frontend/src/analytics/gtm.js`** injects GTM when `VITE_GTM_CONTAINER_ID` matches `GTM-*`.
- **`frontend/src/analytics/dataLayer.js`** defines shared events.
- **`router.afterEach`** pushes `virtual_page_view` after navigation (see `docs/gtm-setup.md`).

## 10. Google Ads readiness

- Conversions should be wired in **GTM** using `dataLayer` events documented in `docs/google-ads-tracking.md` (placeholders `GOOGLE_ADS_ID`, `GOOGLE_ADS_CONVERSION_LABEL`).

## 11. Remaining TODOs (manual)

| Item | Action |
|------|--------|
| `VITE_PUBLIC_SITE_ORIGIN` | Set in production build environment to your live origin (matches canonicals + sitemap). |
| `VITE_GTM_CONTAINER_ID` | Set when GTM container is ready. |
| `VITE_OG_IMAGE_URL` | Add a 1200×630 image URL when available. |
| Search Console | Submit sitemap URL after deploy. |
| GA4 / Ads | Create properties and map tags in GTM per runbooks. |

## 12. Recommended next SEO actions (no new pages)

- Add a real **OG image** asset and set `VITE_OG_IMAGE_URL`.
- Monitor **Core Web Vitals**; optionally defer or lazy-load `html2canvas` only on routes that need it.
- Expand **internal links** from blog to specific `/docs` anchors as you add anchors.
