# End-to-end tests (Playwright)

1. Copy [`../../.env.e2e.example`](../../.env.e2e.example) to `frontend/.env.e2e` and set `E2E_USERNAME` and `E2E_PASSWORD` to a valid account on your dev stack.
2. Start the app (e.g. Docker Compose; default host port `4173` via `FRONTEND_HOST_PORT` in root `.env`).
3. Run: `npm run e2e` from the `frontend` directory.

`playwright.config.js` loads `frontend/.env.e2e` if present. You can override `E2E_BASE_URL` when the UI is not on `http://localhost:4173`.

Stripe checkout E2E is opt-in and runs only when `E2E_ENABLE_STRIPE_CHECKOUT=1`.
It expects a Stripe-ready environment (`STRIPE_*` + paid plan `price_...`) and validates that `/platform/billing/checkout-session/` returns a hosted URL containing `E2E_STRIPE_CHECKOUT_URL_CONTAINS` (default: `checkout.stripe.com`).
