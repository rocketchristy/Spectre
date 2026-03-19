import { test, expect } from '@playwright/test'

test.describe('Gallery Page', () => {

  test('loads and displays gallery content', async ({ page }) => {
    await page.goto('/gallery')
    await expect(page.locator('h1, h2').first()).toBeVisible({ timeout: 10_000 })
  })

})
