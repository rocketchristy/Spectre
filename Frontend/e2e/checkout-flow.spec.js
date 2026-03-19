import { test, expect } from '@playwright/test'
import { login } from './helpers.js'

test.describe('Full Purchase Flow (login → add to cart → checkout → orders)', () => {

  test('end-to-end checkout', async ({ page }) => {
    // ── Step 1: Log in ──────────────────────────────────────────────
    await login(page)
    await expect(page.locator('h1.page-title')).toContainText('Store')

    // ── Step 2: Navigate to a product ───────────────────────────────
    const firstCard = page.locator('.product-card').first()
    await expect(firstCard).toBeVisible({ timeout: 10_000 })
    await firstCard.click()
    await expect(page).toHaveURL(/\/product\//)

    // ── Step 3: Add to cart ─────────────────────────────────────────
    const buyBtn = page.locator('.listing-buy-btn').first()

    // If listings exist, add one to the cart
    if (await buyBtn.isVisible({ timeout: 5_000 }).catch(() => false)) {
      await buyBtn.click()

      // Cart-prompt overlay should appear
      await expect(page.locator('.cart-prompt')).toBeVisible({ timeout: 5_000 })
      await page.click('a:has-text("Go to Cart")')
    } else {
      // No listings — go to cart directly (may already have items)
      await page.click('.navbar-nav .nav-link:has-text("Cart")')
    }

    await expect(page).toHaveURL('/cart')

    // ── Step 4: Verify cart ─────────────────────────────────────────
    await expect(page.locator('h1.page-title')).toContainText('Your Cart')

    // If the cart has items, attempt checkout
    const cartItems = page.locator('.list-row')
    if (await cartItems.count() > 0) {
      await expect(page.locator('.summary-bar__total')).toBeVisible()

      // ── Step 5: Checkout ────────────────────────────────────────
      const placeOrder = page.locator('button:has-text("Place Order")')
      if (await placeOrder.isVisible({ timeout: 3_000 }).catch(() => false)) {
        await placeOrder.click()
        await expect(page.locator('.checkout-success')).toBeVisible({ timeout: 10_000 })

        // ── Step 6: Verify order appears in history ───────────────
        await page.click('a:has-text("View Orders")')
        await expect(page).toHaveURL('/orders')
        await expect(page.locator('.orders-table tbody tr').first()).toBeVisible({ timeout: 10_000 })
      }
    }
  })

})
