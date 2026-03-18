/**
 * API mocking utilities for testing
 * Provides helpers to mock API responses and test API interactions
 */

import { vi } from 'vitest'

/**
 * Mock API responses for common endpoints
 */
export const mockApiResponses = {
  // Cart endpoints
  getCart: (items = []) => ({
    success: true,
    data: { items, total: items.reduce((sum, item) => sum + item.price * item.quantity, 0) },
  }),
  
  addToCart: (item) => ({
    success: true,
    data: item,
    message: 'Item added to cart',
  }),
  
  removeFromCart: (id) => ({
    success: true,
    data: { id },
    message: 'Item removed from cart',
  }),
  
  updateCartItem: (item) => ({
    success: true,
    data: item,
    message: 'Cart item updated',
  }),

  // Product endpoints
  getProducts: (products = []) => ({
    success: true,
    data: products,
    total: products.length,
  }),
  
  getProduct: (product) => ({
    success: true,
    data: product,
  }),

  // Order endpoints
  createOrder: (order) => ({
    success: true,
    data: { ...order, id: Date.now() },
    message: 'Order created successfully',
  }),
  
  getOrders: (orders = []) => ({
    success: true,
    data: orders,
  }),
  
  getOrder: (order) => ({
    success: true,
    data: order,
  }),

  // User endpoints
  getUser: (user) => ({
    success: true,
    data: user,
  }),
  
  updateUser: (user) => ({
    success: true,
    data: user,
    message: 'User updated successfully',
  }),
  
  login: (user, token = 'mock-jwt-token') => ({
    success: true,
    data: { user, token },
    message: 'Login successful',
  }),
  
  register: (user, token = 'mock-jwt-token') => ({
    success: true,
    data: { user, token },
    message: 'Registration successful',
  }),

  // Error responses
  error: (message = 'An error occurred', status = 500) => ({
    success: false,
    error: message,
    status,
  }),
  
  notFound: (resource = 'Resource') => ({
    success: false,
    error: `${resource} not found`,
    status: 404,
  }),
  
  unauthorized: () => ({
    success: false,
    error: 'Unauthorized',
    status: 401,
  }),
  
  validationError: (fields = {}) => ({
    success: false,
    error: 'Validation failed',
    fields,
    status: 422,
  }),
}

/**
 * Creates a mock fetch implementation
 * @param {Object} responses - Map of URL patterns to responses
 * @returns {Function} Mock fetch function
 */
export function createMockFetch(responses = {}) {
  return vi.fn((url, options = {}) => {
    // Find matching response
    for (const [pattern, response] of Object.entries(responses)) {
      if (url.includes(pattern)) {
        const data = typeof response === 'function' ? response(url, options) : response
        
        return Promise.resolve({
          ok: data.success !== false,
          status: data.status || (data.success !== false ? 200 : 500),
          statusText: data.success !== false ? 'OK' : 'Error',
          json: () => Promise.resolve(data),
          text: () => Promise.resolve(JSON.stringify(data)),
          headers: new Headers({ 'Content-Type': 'application/json' }),
        })
      }
    }
    
    // Default 404 response
    return Promise.resolve({
      ok: false,
      status: 404,
      statusText: 'Not Found',
      json: () => Promise.resolve(mockApiResponses.notFound()),
      text: () => Promise.resolve(JSON.stringify(mockApiResponses.notFound())),
      headers: new Headers(),
    })
  })
}

/**
 * Sets up API mocks for testing
 * @param {Object} config - Configuration object with endpoint mocks
 */
export function setupApiMocks(config = {}) {
  const defaultConfig = {
    '/api/cart': mockApiResponses.getCart([]),
    '/api/products': mockApiResponses.getProducts([]),
    '/api/orders': mockApiResponses.getOrders([]),
    '/api/user': mockApiResponses.getUser({}),
    ...config,
  }
  
  global.fetch = createMockFetch(defaultConfig)
  return global.fetch
}

/**
 * Simulates API delay for testing loading states
 * @param {any} response - Response to return after delay
 * @param {number} delay - Delay in milliseconds
 * @returns {Promise} Promise that resolves after delay
 */
export function mockApiWithDelay(response, delay = 100) {
  return new Promise(resolve => {
    setTimeout(() => {
      resolve({
        ok: response.success !== false,
        status: response.status || 200,
        json: () => Promise.resolve(response),
        text: () => Promise.resolve(JSON.stringify(response)),
        headers: new Headers(),
      })
    }, delay)
  })
}

/**
 * Mocks a failing API request
 * @param {string} message - Error message
 * @param {number} status - HTTP status code
 * @returns {Promise} Rejected promise
 */
export function mockApiError(message = 'Network error', status = 500) {
  return Promise.reject({
    message,
    status,
    response: {
      status,
      data: mockApiResponses.error(message, status),
    },
  })
}

/**
 * Creates a spy on fetch for testing API calls
 * @returns {Function} Spy function
 */
export function spyOnFetch() {
  return vi.spyOn(global, 'fetch')
}

/**
 * Verifies that fetch was called with specific parameters
 * @param {Function} fetchSpy - Spy on fetch function
 * @param {string} url - Expected URL
 * @param {Object} options - Expected fetch options
 */
export function expectFetchCalledWith(fetchSpy, url, options = {}) {
  expect(fetchSpy).toHaveBeenCalledWith(
    expect.stringContaining(url),
    expect.objectContaining(options)
  )
}
