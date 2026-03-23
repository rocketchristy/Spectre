import { defineConfig } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  fullyParallel: false,          // run tests in order (they share state like cart)
  workers: 1,
  retries: 0,
  timeout: 150_000,
  use: {
    baseURL: 'http://localhost:5173',
    headless: false,             // watch the browser while developing tests
    screenshot: 'only-on-failure',
    trace: 'retain-on-failure',
  },
  projects: [
    { name: 'chromium', use: { browserName: 'chromium' } },
  ],
  /* Start Vite dev server before tests run */
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: true,   // won't start a 2nd server if one is already running
    timeout: 15_000,
  },
})
