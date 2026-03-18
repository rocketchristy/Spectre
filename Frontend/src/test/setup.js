/**
 * Global test setup file for Vitest
 * Runs before all test files
 */

import { vi } from 'vitest'
import { config } from '@vue/test-utils'

// Mock window.matchMedia (used by some CSS-in-JS libraries)
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // deprecated
    removeListener: vi.fn(), // deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  takeRecords() {
    return []
  }
  unobserve() {}
}

// Mock scrollTo
window.scrollTo = vi.fn()

// Configure Vue Test Utils global options
config.global.mocks = {
  // Add any global mocks here
}

// Global test utilities can be added here
global.flushPromises = () => new Promise(resolve => setImmediate(resolve))
