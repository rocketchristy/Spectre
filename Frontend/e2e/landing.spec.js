import { test, expect } from '@playwright/test'

test.describe('Landing Page', () => {

  test('shows welcome screen with login and guest buttons', async ({ page }) => {
    await page.goto('/')
    await expect(page.locator('h1.landing__title')).toContainText('Welcome')
    await expect(page.locator('button:has-text("Login / Sign")')).toBeVisible()
    await expect(page.locator('button:has-text("Continue your adventure")')).toBeVisible()
  })

  test('guest button navigates to /store', async ({ page }) => {
    await page.goto('/')
    await page.click('button:has-text("Continue your adventure")')
    await expect(page).toHaveURL('/store')
    await expect(page.locator('h1.page-title')).toContainText('Store')
  })

  test('login fields appear after clicking Login / Sign-Up', async ({ page }) => {
    await page.goto('/')
    await page.click('button:has-text("Login / Sign")')
    await expect(page.locator('input[placeholder="Email"]')).toBeVisible()
    await expect(page.locator('input[placeholder="Password"]')).toBeVisible()
  })

})
