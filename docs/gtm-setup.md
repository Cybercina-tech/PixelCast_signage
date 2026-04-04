# Google Tag Manager — PixelCast frontend

**Placeholder:** `GTM_CONTAINER_ID` → use the same value as `VITE_GTM_CONTAINER_ID` in your Vite build (format `GTM-XXXXXXX`).

## Placement

- **Injection:** `frontend/src/analytics/gtm.js` (`bootGtm`) runs from `frontend/src/main.js` after `createHead()`, Pinia, and Router registration.
- **Condition:** Script + noscript iframe load **only** when `VITE_GTM_CONTAINER_ID` is set and matches `GTM-*`.
- **Order:** `window.dataLayer` is initialised before the GTM script runs (`frontend/src/analytics/dataLayer.js`).

## dataLayer contract

Default push shape:

```js
window.dataLayer = window.dataLayer || []
```

Events used today:

| Event name | Purpose |
|------------|---------|
| `virtual_page_view` | SPA route change (see `frontend/src/router/index.js`) |
| `cta_click` | Landing CTA tracking |
| `login` | Successful auth |
| `sign_up` | Successful registration |

## Recommended GTM workspace structure

- **Folder:** `PixelCast — GA4`
- **Folder:** `PixelCast — Ads` (remarketing / conversions)
- **Folder:** `PixelCast — Utilities` (constants, lookup tables)

## Recommended triggers

1. **CE — virtual_page_view** — Custom Event: `virtual_page_view`  
   - Use for GA4 **page_view** in SPA (map `page_path` / `page_title` to fields).
2. **CE — cta_click** — Custom Event: `cta_click`
3. **CE — login** — Custom Event: `login`
4. **CE — sign_up** — Custom Event: `sign_up`

## Recommended variables

| Variable name | Type | Data Layer key |
|---------------|------|----------------|
| DLV — page_path | Data Layer | `page_path` |
| DLV — page_title | Data Layer | `page_title` |
| DLV — page_location | Data Layer | `page_location` |
| DLV — cta_id | Data Layer | `cta_id` |
| DLV — cta_label | Data Layer | `cta_label` |
| DLV — method | Data Layer | `method` |

## GA4 via GTM (avoid duplicates)

- Configure **one** GA4 Configuration tag (your `GA4_MEASUREMENT_ID`).
- Do **not** also embed `gtag.js` for the same property unless you exclude overlap.
- Optional env `VITE_GA4_MEASUREMENT_ID` is for documentation / non-GTM setups only.

## Tag naming convention

`GA4 — Event — <event_name> — PixelCast`  
`Ads — Conversion — <goal> — PixelCast`
