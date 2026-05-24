import { test, expect } from '@playwright/test'

const base = process.env.E2E_BASE_URL || 'http://localhost:4173'
const username = process.env.E2E_USERNAME || 'admin@pixelcast.com'
const password = process.env.E2E_PASSWORD || 'adminadmin'

const NAV_PATHS = [
  '/super-admin',
  '/super-admin/blog',
  '/super-admin/blog/ai',
  '/super-admin/reports',
  '/super-admin/customers',
  '/super-admin/users',
  '/super-admin/devices',
  '/super-admin/billing',
  '/super-admin/pricing',
  '/super-admin/self-hosted-licenses',
  '/super-admin/gateway-instances',
  '/super-admin/tickets',
  '/super-admin/tickets/analytics',
  '/super-admin/tickets/settings',
  '/super-admin/alerts',
  '/super-admin/capacity',
  '/super-admin/smtp',
  '/super-admin/flags',
  '/super-admin/audit-logs',
  '/super-admin/backups',
  '/super-admin/system',
]

test.describe('Super Admin smoke', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(`${base}/login`)
    await page.getByLabel(/username or email/i).fill(username)
    await page.getByLabel(/^password$/i).fill(password)
    await page.getByRole('button', { name: /sign in/i }).click()
    await page.waitForURL(/\/(dashboard|super-admin)/, { timeout: 30000 })
  })

  for (const path of NAV_PATHS) {
    test(`loads ${path}`, async ({ page }) => {
      await page.goto(`${base}${path}`)
      await expect(page.locator('h1').first()).toBeVisible({ timeout: 15000 })
      await expect(page.getByText(/403 forbidden|internal server error/i)).toHaveCount(0)
    })
  }

  test('tenant detail shows license tab', async ({ page }) => {
    await page.goto(`${base}/super-admin/customers`)
    const firstLink = page.locator('a[href*="/super-admin/customers/"]').first()
    if ((await firstLink.count()) === 0) {
      test.skip()
      return
    }
    await firstLink.click()
    await page.getByRole('button', { name: 'License' }).click()
    await expect(page.getByText(/SaaS tenant license/i)).toBeVisible()
  })

  test('settings billing tab is reachable', async ({ page }) => {
    await page.goto(`${base}/settings?tab=billing`)
    await expect(page.getByText(/Plan & Billing/i)).toBeVisible({ timeout: 15000 })
    await expect(page.getByRole('button', { name: /Upgrade plan/i })).toBeVisible()
  })

  test('super admin pricing exposes stripe runtime form', async ({ page }) => {
    await page.goto(`${base}/super-admin/pricing`)
    await expect(page.getByRole('heading', { name: /Pricing catalog/i })).toBeVisible({ timeout: 15000 })
    await expect(page.getByText(/Stripe runtime configuration/i)).toBeVisible({ timeout: 15000 })
    await expect(page.locator('input[placeholder="pk_live_..."]')).toBeVisible()
    await expect(page.locator('input[placeholder="whsec_..."]')).toBeVisible()
    await expect(page.getByRole('button', { name: /Run health check/i })).toBeVisible()
    await expect(page.getByRole('button', { name: /Save Stripe configuration/i })).toBeVisible()
  })

  test('public pricing page renders paid checkout actions', async ({ page }) => {
    await page.goto(`${base}/pricing`)
    await expect(page.getByRole('heading', { name: /Plans & pricing/i })).toBeVisible({ timeout: 15000 })
    const cta = page.getByRole('button', { name: /Continue with Stripe|Configure Stripe price/i }).first()
    await expect(cta).toBeVisible({ timeout: 15000 })
  })

  test('super admin header has plan shortcut', async ({ page }) => {
    await page.goto(`${base}/super-admin/users`)
    await expect(page.getByRole('link', { name: /Plan/i })).toBeVisible({ timeout: 15000 })
  })

  test('profile shows compact billing summary card', async ({ page }) => {
    await page.goto(`${base}/profile`)
    await expect(page.getByText(/^Billing Summary$/i)).toBeVisible({ timeout: 15000 })
    const hasPlaceholder = await page.getByText(/Billing summary is not available yet\./i).first().isVisible().catch(() => false)
    if (!hasPlaceholder) {
      await expect(page.getByRole('link', { name: /Manage/i })).toBeVisible({ timeout: 15000 })
      await expect(page.getByRole('link', { name: /Upgrade/i })).toBeVisible({ timeout: 15000 })
    }
  })

  test('dashboard shows compact billing summary card', async ({ page }) => {
    await page.goto(`${base}/dashboard`)
    const billingCard = page.locator('.card-base').filter({ hasText: /Billing summary is not available yet\.|Plan:/i }).first()
    await expect(billingCard).toBeVisible({ timeout: 15000 })
  })
})
