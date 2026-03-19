import { test, expect } from '@playwright/test'
import { login } from './helpers.js'

test.describe('User Profile', () => {

  test('profile page requires login', async ({ page }) => {
    await page.goto('/profile')
    await expect(page.locator('.login-prompt')).toBeVisible()
  })

  test('shows user info after login', async ({ page }) => {
    await login(page)
    await page.click('.navbar-nav .nav-link:has-text("Profile")')
    await expect(page).toHaveURL('/profile')

    await expect(page.locator('.profile-header')).toBeVisible({ timeout: 10_000 })
    await expect(page.locator('.profile-title')).not.toBeEmpty()
    await expect(page.locator('.info-value').first()).toBeVisible()
  })

  test('logout returns to landing page', async ({ page }) => {
    await login(page)
    await page.click('.navbar-nav .nav-link:has-text("Profile")')
    await expect(page).toHaveURL('/profile')

    await page.click('button:has-text("Log Out")')
    await expect(page).toHaveURL('/')
  })

})
