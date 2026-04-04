# GA4 events map (PixelCast frontend)

Use this with **Google Tag Manager**: map `dataLayer` events to GA4 tags. Prefer a single GA4 Configuration tag in GTM fed by the same dataLayer (avoid duplicate GA4 if also using `VITE_GA4_MEASUREMENT_ID` in parallel).

**Placeholder:** `GA4_MEASUREMENT_ID` → replace with your **Measurement ID** (`G-XXXXXXXXXX`) in GTM.

## Automatic events

| Event name (dataLayer) | When it fires | Parameters | Business purpose |
|------------------------|----------------|------------|------------------|
| `virtual_page_view` | After every Vue Router navigation (`router.afterEach`), post-`nextTick` | `page_path`, `page_title`, `page_location` | SPA page views in GA4 (use GTM trigger on this event or History Change + vars below). |

**Implementation:** `frontend/src/router/index.js` + `frontend/src/analytics/dataLayer.js` (`pushVirtualPageView`).

## Engagement & conversion-oriented events

| Event name | When it fires | Parameters | GA4 recommended mapping |
|------------|---------------|------------|-------------------------|
| `cta_click` | Landing hero CTAs | `event: 'cta_click'`, `cta_id`, `cta_label`, `page` | Mark as key event; use `cta_id` as custom dimension |
| `login` | Successful password or 2FA login | `event: 'login'`, `method`: `'password'` \| `'2fa'` | Standard `login` |
| `sign_up` | Successful signup | `event: 'sign_up'`, `method`: `'email'` | Standard `sign_up` |

**Implementation:**  
- CTA: `frontend/src/pages/Landing.vue` → `pushCtaClick`  
- Login: `frontend/src/pages/Login.vue` → `pushLogin`  
- Signup: `frontend/src/pages/Signup.vue` → `pushSignUp`

## Future (not wired in UI)

| Suggested event | Trigger | Notes |
|-----------------|---------|--------|
| `generate_lead` | Ticket/contact form success (if exposed publicly) | Add when form exists |
| `phone_click` / `email_click` | `tel:` / `mailto:` in marketing pages | Add `click` listeners on footer/contact |

## GTM → GA4 tag settings (summary)

1. **Variables:** Data Layer Variable for `page_path`, `page_title`, `page_location`, `cta_id`, `method`.
2. **Triggers:** Custom Event `virtual_page_view`; Custom Event `cta_click`; `login`; `sign_up`.
3. **GA4 Event tag:** For `virtual_page_view`, send GA4 event `page_view` with page fields from DL, or use GA4’s enhanced measurement + History Change — **do not double-count**; pick one strategy.
