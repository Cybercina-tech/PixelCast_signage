# Google Ads — conversion & remarketing readiness (PixelCast)

The app does **not** load `gtag` for Google Ads directly. Use **GTM** to add **Google Ads Conversion Tracking** and **Remarketing** tags, driven by the same `dataLayer` events as GA4.

**Placeholders (for GTM / Ads UI):**

- `GOOGLE_ADS_ID` — typically `AW-XXXXXXXXX`
- `GOOGLE_ADS_CONVERSION_LABEL` — per-conversion label string from Ads

## Primary conversions (suggested)

| Business action | dataLayer event | Suggested conversion name | Notes |
|------------------|-----------------|---------------------------|--------|
| Account created | `sign_up` | Sign-up | Fires on successful signup (`Signup.vue`) |
| User signed in | `login` | Login | Fires after password or 2FA success |
| High-intent CTA | `cta_click` with `cta_id` = `hero_primary` | Start trial / Install | Filter in GTM on `cta_id` |

Map each to a **Google Ads: Conversion** tag in GTM with your `GOOGLE_ADS_ID` and the correct **Conversion label** from Google Ads.

## Secondary / micro conversions

| Event | Use |
|-------|-----|
| `cta_click` (`hero_docs`, `hero_data_center`, `hero_explore`) | Micro-conversions or audiences |
| `virtual_page_view` on `/pricing` (if added later) | Funnel analysis |

## Suggested conversion values (optional)

Assign static values in GTM for `sign_up` (e.g. model LTV) if your media team uses value-based bidding. Keep conservative until analytics proves LTV.

## Remarketing audiences (suggested)

- All site visitors (tag-based remarketing via GTM).
- Visitors who fired `cta_click` with `cta_id` containing `hero_`.
- Visitors who reached `virtual_page_view` with `page_path` = `/signup` but did not fire `sign_up` (requires sequence trigger or GA4 audience export if using GA4-linked Ads).

## Implementation reference

- `frontend/src/analytics/dataLayer.js` — `pushDataLayerEvent`, `pushSignUp`, `pushLogin`, `pushCtaClick`
- `frontend/src/analytics/gtm.js` — GTM bootstrap
