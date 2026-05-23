import { expect, test } from '@playwright/test'
import { login } from './helpers/auth'

const enabled = process.env.E2E_ENABLE_STRIPE_CHECKOUT === '1'
const checkoutUrlContains = process.env.E2E_STRIPE_CHECKOUT_URL_CONTAINS || 'checkout.stripe.com'

test.describe('Stripe checkout', () => {
  test('billing center opens a Stripe checkout session', async ({ page }) => {
    if (!enabled) {
      test.skip(true, 'Set E2E_ENABLE_STRIPE_CHECKOUT=1 to run Stripe checkout E2E.')
      return
    }

    await login(page)
    await page.goto('/super-admin/billing')

    const checkoutButton = page.getByRole('button', { name: /stripe checkout/i })
    await expect(checkoutButton).toBeVisible({ timeout: 15000 })

    const disabled = await checkoutButton.isDisabled()
    if (disabled) {
      await expect(
        page.getByText(/stripe actions are currently blocked|configure stripe in super admin/i).first()
      ).toBeVisible({ timeout: 10000 })
      test.skip(true, 'Stripe checkout button is disabled; verify STRIPE_* env and pricing catalog.')
      return
    }

    const checkoutResponsePromise = page.waitForResponse(
      (response) =>
        response.url().includes('/platform/billing/checkout-session/') &&
        response.request().method() === 'POST'
    )

    await checkoutButton.click()
    const checkoutResponse = await checkoutResponsePromise
    expect(checkoutResponse.ok()).toBeTruthy()

    const payload = await checkoutResponse.json()
    expect(typeof payload.url).toBe('string')
    expect(payload.url).toContain(checkoutUrlContains)
  })
})
