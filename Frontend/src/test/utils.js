/**
 * Test utility functions and helpers for component testing
 */

import { mount, shallowMount } from '@vue/test-utils'
import { vi } from 'vitest'
import { createRouter, createMemoryHistory } from 'vue-router'

/**
 * Creates a mock Vue Router instance for testing
 * @param {Array} routes - Optional custom routes
 * @param {Object} initialRoute Optional initial route with params/query
 * @returns {Router} Mock router instance
 */
export function createMockRouter(routes = [], initialRoute = null) {
  const defaultRoutes = [
    { path: '/', name: 'home', component: { template: '<div>Home</div>' } },
    { path: '/store', name: 'store', component: { template: '<div>Store</div>' } },
    { path: '/cart', name: 'cart', component: { template: '<div>Cart</div>' } },
    { path: '/gallery', name: 'gallery', component: { template: '<div>Gallery</div>' } },
    { path: '/profile', name: 'profile', component: { template: '<div>Profile</div>' } },
    { path: '/orders', name: 'orderHistory', component: { template: '<div>Orders</div>' } },
    { path: '/about', name: 'about', component: { template: '<div>About</div>' } },
    { path: '/product/:type/:id', name: 'product', component: { template: '<div>Product</div>' } },
    { path: '/error', name: 'error', component: { template: '<div>Error</div>' } },
  ]

  const router = createRouter({
    history: createMemoryHistory(),
    routes: routes.length > 0 ? routes : defaultRoutes,
  })

  // Set initial route if provided
  if (initialRoute) {
    router.push(initialRoute)
  }

  // Mock router methods (but keep originals for pushes to work)
  const originalPush = router.push
  const originalReplace = router.replace
  
  router.push = vi.fn((...args) => originalPush.apply(router, args))
  router.replace = vi.fn((...args) => originalReplace.apply(router, args))
  router.go = vi.fn()
  router.back = vi.fn()
  router.forward = vi.fn()

  return router
}

/**
 * Creates a wrapper with common test defaults
 * @param {Component} component - Vue component to mount
 * @param {Object} options - Mount options
 * @returns {Wrapper} Vue Test Utils wrapper
 */
export function mountWithDefaults(component, options = {}) {
  const router = options.router || createMockRouter()
  
  return mount(component, {
    global: {
      plugins: [router],
      stubs: {
        RouterLink: {
          template: '<a><slot /></a>',
          props: ['to']
        },
        RouterView: true,
        ...options.global?.stubs,
      },
      mocks: {
        ...options.global?.mocks,
      },
    },
    ...options,
  })
}

/**
 * Creates a shallow wrapper with common test defaults
 * @param {Component} component - Vue component to shallow mount
 * @param {Object} options - Mount options
 * @returns {Wrapper} Vue Test Utils wrapper
 */
export function shallowMountWithDefaults(component, options = {}) {
  const router = options.router || createMockRouter()
  
  return shallowMount(component, {
    global: {
      plugins: [router],
      stubs: {
        RouterLink: true,
        RouterView: true,
        ...options.global?.stubs,
      },
      mocks: {
        ...options.global?.mocks,
      },
    },
    ...options,
  })
}

/**
 * Creates mock cart data for testing
 * @param {number} count - Number of items to create
 * @returns {Array} Array of cart items
 */
export function createMockCartItems(count = 3) {
  return Array.from({ length: count }, (_, i) => ({
    id: i + 1,
    name: `Product ${i + 1}`,
    type: i % 2 === 0 ? 'pack' : 'card',
    price: 10 + i * 5,
    quantity: i + 1,
    image: i % 2 === 0 ? '📦' : '🎴',
  }))
}

/**
 * Creates mock product data for testing
 * @param {number} count - Number of products to create
 * @returns {Array} Array of products
 */
export function createMockProducts(count = 5) {
  return Array.from({ length: count }, (_, i) => ({
    id: i + 1,
    name: `Card ${i + 1}`,
    category: i % 2 === 0 ? 'rare' : 'common',
    price: 5 + i * 2,
    description: `Description for card ${i + 1}`,
    image: `card-${i + 1}.jpg`,
    inStock: i % 3 !== 0,
  }))
}

/**
 * Creates a mock user object for testing
 * @param {Object} overrides - Properties to override
 * @returns {Object} Mock user object
 */
export function createMockUser(overrides = {}) {
  return {
    id: 1,
    username: 'testuser',
    email: 'test@example.com',
    firstName: 'Test',
    lastName: 'User',
    ...overrides,
  }
}

/**
 * Waits for all promises to resolve
 * Useful for waiting for async operations in tests
 */
export async function flushPromises() {
  return new Promise(resolve => {
    setTimeout(resolve, 0)
  })
}

/**
 * Creates a mock fetch response
 * @param {any} data - Data to return
 * @param {boolean} ok - Whether the response is successful
 * @param {number} status - HTTP status code
 * @returns {Promise} Mock fetch response
 */
export function createMockFetchResponse(data, ok = true, status = 200) {
  return Promise.resolve({
    ok,
    status,
    json: () => Promise.resolve(data),
    text: () => Promise.resolve(JSON.stringify(data)),
    headers: new Headers(),
  })
}

/**
 * Mocks the global fetch function
 * @param {any} data - Data to return from fetch
 * @param {boolean} ok - Whether the response is successful
 */
export function mockFetchSuccess(data, ok = true) {
  global.fetch = vi.fn(() => createMockFetchResponse(data, ok))
  return global.fetch
}

/**
 * Mocks a failed fetch request
 * @param {string} error - Error message
 */
export function mockFetchError(error = 'Network error') {
  global.fetch = vi.fn(() => Promise.reject(new Error(error)))
  return global.fetch
}

/**
 * Helper to find element by test id
 * @param {Wrapper} wrapper - Vue Test Utils wrapper
 * @param {string} testId - Test ID to find
 * @returns {Wrapper} Found element wrapper
 */
export function findByTestId(wrapper, testId) {
  return wrapper.find(`[data-testid="${testId}"]`)
}

/**
 * Helper to find all elements by test id
 * @param {Wrapper} wrapper - Vue Test Utils wrapper
 * @param {string} testId - Test ID to find
 * @returns {Array} Array of element wrappers
 */
export function findAllByTestId(wrapper, testId) {
  return wrapper.findAll(`[data-testid="${testId}"]`)
}
