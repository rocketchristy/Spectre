import { test, expect } from '@playwright/test'

test.describe('Product Page', () => {

  test('shows product details after navigating from store', async ({ page }) => {
    await page.goto('/store')
    const firstCard = page.locator('.product-card').first()
    await expect(firstCard).toBeVisible({ timeout: 10_000 })

    // Grab the name before clicking
    const cardName = await firstCard.locator('h3').innerText()
    await firstCard.click()

    await expect(page).toHaveURL(/\/product\//)
    await expect(page.locator('h1')).toContainText(cardName)
  })

  test('back link returns to store', async ({ page }) => {
    await page.goto('/store')
    const firstCard = page.locator('.product-card').first()
    await expect(firstCard).toBeVisible({ timeout: 10_000 })
    await firstCard.click()
    await expect(page).toHaveURL(/\/product\//)

    await page.click('.back-link')
    await expect(page).toHaveURL('/store')
  })

  test('listings are visible for a card product', async ({ page }) => {
    // Navigate into a card product from the store
    await page.goto('/store')
    const cardLink = page.locator('.product-card').last()
    await expect(cardLink).toBeVisible({ timeout: 10_000 })
    await cardLink.click()
    await expect(page).toHaveURL(/\/product\//)

    // Either listings or an empty state should be present
    const listings = page.locator('.listing-row')
    const emptyState = page.locator('.empty-state')
    await expect(listings.first().or(emptyState.first())).toBeVisible({ timeout: 10_000 })
  })

})
