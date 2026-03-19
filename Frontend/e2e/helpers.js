/**
 * Shared helpers for e2e tests.
 *
 * TEST_EMAIL / TEST_PASSWORD must point at an account that already exists
 * in your local DB2 backend.  Change them here once and every spec picks
 * them up.
 */

export const TEST_EMAIL    = 'beedle@gmail.com'
export const TEST_PASSWORD = 'Beedle1234'

/**
 * Log in through the landing-page UI and wait until the store loads.
 */
export async function login(page, email = TEST_EMAIL, password = TEST_PASSWORD) {
  await page.goto('/')
  await page.click('button:has-text("Login / Sign")')
  await page.fill('input[placeholder="Email"]', email)
  await page.fill('input[placeholder="Password"]', password)
  await page.click('button:has-text("Login")')
  await page.waitForURL('/store')
}
