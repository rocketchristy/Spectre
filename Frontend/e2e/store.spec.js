import { test, expect } from '@playwright/test'

test.describe('Store Page (guest)', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/store')
  })

  test('displays page title', async ({ page }) => {
    await expect(page.locator('h1.page-title')).toContainText('Store')
  })

  test('shows product cards after data loads', async ({ page }) => {
    const cards = page.locator('.product-card')
    await expect(cards.first()).toBeVisible({ timeout: 10_000 })
    await expect(cards).not.toHaveCount(0)
  })

  test('search bar filters results', async ({ page }) => {
    const searchInput = page.locator('.search-input')
    await expect(searchInput).toBeVisible()

    // Type a partial name — results should appear
    await searchInput.fill('a')
    await expect(page.locator('.search-results').first()).toBeVisible({ timeout: 5_000 })
  })

  test('clicking a product card navigates to product page', async ({ page }) => {
    const firstCard = page.locator('.product-card').first()
    await expect(firstCard).toBeVisible({ timeout: 10_000 })
    await firstCard.click()
    await expect(page).toHaveURL(/\/product\//)
  })

  test('navbar links are present', async ({ page }) => {
    for (const label of ['Store', 'Gallery', 'Cart', 'Orders', 'Profile']) {
      await expect(
        page.locator('.navbar-nav .nav-link', { hasText: label })
      ).toBeVisible()
    }
  })

})
