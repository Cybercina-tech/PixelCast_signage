import { expect, test } from '@playwright/test'
import { login } from './helpers/auth'

test('template editor balanced layout and basic interactions', async ({ page }) => {
  test.setTimeout(120000)
  await login(page)

  await page.goto('/templates/new/edit?name=E2E%20Template&width=1280&height=720')
  await expect(page.getByText('Widget Library')).toBeVisible()
  await expect(page.getByRole('button', { name: /save template/i })).toBeVisible()
  await expect(page.getByRole('button', { name: /export json/i })).toBeVisible()

  await page.getByRole('button', { name: /add text/i }).click()
  await expect(page.locator('.widget-element').first()).toBeVisible()

  await page.getByRole('button', { name: /layers/i }).click()
  await expect(page.getByText(/layers/i).first()).toBeVisible()

  await page.getByRole('button', { name: /properties/i }).click()
  await expect(page.getByText(/position & size/i)).toBeVisible()
})

test('template editor keyboard shortcuts do not interfere with input editing', async ({ page }) => {
  test.setTimeout(120000)
  await login(page)

  await page.goto('/templates/new/edit?name=Keyboard%20Safety&width=1280&height=720')
  await page.getByRole('button', { name: /add text/i }).click()

  const xInput = page.locator('input[type="number"]').first()
  const before = await xInput.inputValue()

  const textArea = page.locator('textarea').first()
  await textArea.click()
  await page.keyboard.press('ArrowRight')
  await page.keyboard.press('Delete')

  const after = await xInput.inputValue()
  expect(after).toBe(before)
})
