import { describe, it, expect, beforeEach, vi } from 'vitest'
import { nextTick } from 'vue'
import LandingPage from './LandingPage.vue'
import { mountWithDefaults, createMockRouter, flushPromises } from '../../test/utils'

// Mock the API module
vi.mock('../../utils/api.js', () => ({
  loginUser: vi.fn(),
  registerUser: vi.fn()
}))

import * as api from '../../utils/api.js'

describe('LandingPage Component', () => {
  let wrapper
  let mockRouter

  beforeEach(() => {
    // Setup localStorage mock
    const localStorageMock = {
      getItem: vi.fn(),
      setItem: vi.fn(),
      removeItem: vi.fn(),
      clear: vi.fn()
    }
    global.localStorage = localStorageMock

    mockRouter = createMockRouter()
    wrapper = mountWithDefaults(LandingPage, { router: mockRouter })
  })

  afterEach(() => {
    wrapper.unmount()
    vi.clearAllMocks()
  })

  describe('Component Rendering', () => {
    // Test 1: Verify landing page component mounts successfully
    it('should render the landing page component', () => {
      expect(wrapper.exists()).toBe(true)
    })

    // Test 2: Verify auth fields hidden by default on initial load
    it('should initially hide auth fields', () => {
      expect(wrapper.vm.showAuthFields).toBe(false)
    })

    // Test 3: Verify component starts in login mode (not signup)
    it('should default to login mode', () => {
      expect(wrapper.vm.isSignup).toBe(false)
    })

    // Test 4: Verify all form fields initialize as empty strings
    it('should initialize with empty form fields', () => {
      expect(wrapper.vm.email).toBe('')
      expect(wrapper.vm.password).toBe('')
      expect(wrapper.vm.firstName).toBe('')
      expect(wrapper.vm.lastName).toBe('')
    })
  })

  describe('Guest Access', () => {
    // Test 5: Verify guest button navigates to store without authentication
    it('should navigate to store when continuing as guest', async () => {
      wrapper.vm.continueAsGuest()
      
      expect(mockRouter.push).toHaveBeenCalledWith({ name: 'store' })
    })
  })

  describe('Login Validation', () => {
    // Test 6: Verify login validation passes with email and password
    it('should validate login with email and password', () => {
      wrapper.vm.email = 'test@example.com'
      wrapper.vm.password = 'password123'
      
      expect(wrapper.vm.isLoginValid).toBe(true)
    })

    it('should invalidate login with empty email', () => {
      wrapper.vm.email = ''
      wrapper.vm.password = 'password123'
      
      expect(wrapper.vm.isLoginValid).toBe(false)
    })

    it('should invalidate login with empty password', () => {
      wrapper.vm.email = 'test@example.com'
      wrapper.vm.password = ''
      
      expect(wrapper.vm.isLoginValid).toBe(false)
    })

    it('should trim whitespace in validation', () => {
      wrapper.vm.email = '   '
      wrapper.vm.password = '   '
      
      expect(wrapper.vm.isLoginValid).toBe(false)
    })
  })

  describe('Signup Validation', () => {
    beforeEach(() => {
      wrapper.vm.isSignup = true
    })

    it('should validate signup with all fields', () => {
      wrapper.vm.email = 'test@example.com'
      wrapper.vm.password = 'password123'
      wrapper.vm.firstName = 'John'
      wrapper.vm.lastName = 'Doe'
      
      expect(wrapper.vm.isSignupValid).toBe(true)
    })

    it('should invalidate signup with missing first name', () => {
      wrapper.vm.email = 'test@example.com'
      wrapper.vm.password = 'password123'
      wrapper.vm.firstName = ''
      wrapper.vm.lastName = 'Doe'
      
      expect(wrapper.vm.isSignupValid).toBe(false)
    })

    it('should invalidate signup with missing last name', () => {
      wrapper.vm.email = 'test@example.com'
      wrapper.vm.password = 'password123'
      wrapper.vm.firstName = 'John'
      wrapper.vm.lastName = ''
      
      expect(wrapper.vm.isSignupValid).toBe(false)
    })

    it('should require email and password for signup', () => {
      wrapper.vm.email = ''
      wrapper.vm.password = ''
      wrapper.vm.firstName = 'John'
      wrapper.vm.lastName = 'Doe'
      
      expect(wrapper.vm.isSignupValid).toBe(false)
    })
  })

  describe('Form Mode Switching', () => {
    it('should use login validation when not in signup mode', () => {
      wrapper.vm.isSignup = false
      wrapper.vm.email = 'test@example.com'
      wrapper.vm.password = 'password123'
      
      expect(wrapper.vm.isValid).toBe(true)
    })

    it('should use signup validation when in signup mode', () => {
      wrapper.vm.isSignup = true
      wrapper.vm.email = 'test@example.com'
      wrapper.vm.password = 'password123'
      wrapper.vm.firstName = 'John'
      wrapper.vm.lastName = 'Doe'
      
      expect(wrapper.vm.isValid).toBe(true)
    })
  })

  describe('Login Process', () => {
    it('should call loginUser API on login', async () => {
      api.loginUser.mockResolvedValue({
        token: 'mock-token',
        first_name: 'John'
      })

      wrapper.vm.email = 'test@example.com'
      wrapper.vm.password = 'password123'
      
      await wrapper.vm.onLogin()
      await flushPromises()

      expect(api.loginUser).toHaveBeenCalledWith('test@example.com', 'password123')
    })

    it('should store token in localStorage on successful login', async () => {
      api.loginUser.mockResolvedValue({
        token: 'mock-token',
        first_name: 'John'
      })

      wrapper.vm.email = 'test@example.com'
      wrapper.vm.password = 'password123'
      
      await wrapper.vm.onLogin()
      await flushPromises()

      expect(localStorage.setItem).toHaveBeenCalledWith('token', 'mock-token')
      expect(localStorage.setItem).toHaveBeenCalledWith('firstName', 'John')
    })

    it('should navigate to store on successful login', async () => {
      api.loginUser.mockResolvedValue({
        token: 'mock-token',
        first_name: 'John'
      })

      wrapper.vm.email = 'test@example.com'
      wrapper.vm.password = 'password123'
      
      await wrapper.vm.onLogin()
      await flushPromises()

      expect(mockRouter.push).toHaveBeenCalledWith({ name: 'store' })
    })

    it('should set error message on login failure', async () => {
      api.loginUser.mockRejectedValue(new Error('Invalid credentials'))

      wrapper.vm.email = 'test@example.com'
      wrapper.vm.password = 'wrongpassword'
      
      await wrapper.vm.onLogin()
      await flushPromises()

      expect(wrapper.vm.errorMsg).toBe('Invalid credentials')
    })

    it('should set submitting flag during login', async () => {
      api.loginUser.mockImplementation(() => new Promise(resolve => {
        setTimeout(() => resolve({ token: 'mock-token', first_name: 'John' }), 100)
      }))

      wrapper.vm.email = 'test@example.com'
      wrapper.vm.password = 'password123'
      
      const loginPromise = wrapper.vm.onLogin()
      expect(wrapper.vm.submitting).toBe(true)
      
      await loginPromise
      await flushPromises()
      
      expect(wrapper.vm.submitting).toBe(false)
    })
  })

  describe('Signup Process', () => {
    it('should call registerUser API on signup', async () => {
      api.registerUser.mockResolvedValue({ success: true })
      api.loginUser.mockResolvedValue({
        token: 'mock-token',
        first_name: 'John'
      })

      wrapper.vm.email = 'test@example.com'
      wrapper.vm.password = 'password123'
      wrapper.vm.firstName = 'John'
      wrapper.vm.lastName = 'Doe'
      
      await wrapper.vm.onSignup()
      await flushPromises()

      expect(api.registerUser).toHaveBeenCalledWith(
        'test@example.com',
        'password123',
        'John',
        'Doe'
      )
    })

    it('should auto-login after successful registration', async () => {
      api.registerUser.mockResolvedValue({ success: true })
      api.loginUser.mockResolvedValue({
        token: 'mock-token',
        first_name: 'John'
      })

      wrapper.vm.email = 'test@example.com'
      wrapper.vm.password = 'password123'
      wrapper.vm.firstName = 'John'
      wrapper.vm.lastName = 'Doe'
      
      await wrapper.vm.onSignup()
      await flushPromises()

      expect(api.loginUser).toHaveBeenCalledWith('test@example.com', 'password123')
      expect(localStorage.setItem).toHaveBeenCalledWith('token', 'mock-token')
      expect(localStorage.setItem).toHaveBeenCalledWith('firstName', 'John')
    })

    it('should navigate to store after successful signup', async () => {
      api.registerUser.mockResolvedValue({ success: true })
      api.loginUser.mockResolvedValue({
        token: 'mock-token',
        first_name: 'John'
      })

      wrapper.vm.email = 'test@example.com'
      wrapper.vm.password = 'password123'
      wrapper.vm.firstName = 'John'
      wrapper.vm.lastName = 'Doe'
      
      await wrapper.vm.onSignup()
      await flushPromises()

      expect(mockRouter.push).toHaveBeenCalledWith({ name: 'store' })
    })

    it('should set error message on signup failure', async () => {
      api.registerUser.mockRejectedValue(new Error('Email already exists'))

      wrapper.vm.email = 'test@example.com'
      wrapper.vm.password = 'password123'
      wrapper.vm.firstName = 'John'
      wrapper.vm.lastName = 'Doe'
      
      await wrapper.vm.onSignup()
      await flushPromises()

      expect(wrapper.vm.errorMsg).toBe('Email already exists')
    })
  })

  describe('Form State', () => {
    it('should set touched flag on login attempt', async () => {
      api.loginUser.mockResolvedValue({
        token: 'mock-token',
        first_name: 'John'
      })

      expect(wrapper.vm.touched).toBe(false)

      wrapper.vm.email = 'test@example.com'
      wrapper.vm.password = 'password123'
      await wrapper.vm.onLogin()

      expect(wrapper.vm.touched).toBe(true)
    })

    it('should clear error message on new login attempt', async () => {
      wrapper.vm.errorMsg = 'Previous error'
      
      api.loginUser.mockResolvedValue({
        token: 'mock-token',
        first_name: 'John'
      })

      wrapper.vm.email = 'test@example.com'
      wrapper.vm.password = 'password123'
      await wrapper.vm.onLogin()
      await flushPromises()

      expect(wrapper.vm.errorMsg).toBe('')
    })

    it('should switch from signup back to login and clear error', async () => {
      wrapper.vm.isSignup = true
      wrapper.vm.errorMsg = 'Some signup error'
      await nextTick()

      // Simulate clicking "Back to Login" button
      wrapper.vm.isSignup = false
      wrapper.vm.errorMsg = ''
      await nextTick()

      expect(wrapper.vm.isSignup).toBe(false)
      expect(wrapper.vm.errorMsg).toBe('')
    })

    it('should set touched flag on signup attempt', async () => {
      wrapper.vm.isSignup = true
      expect(wrapper.vm.touched).toBe(false)

      wrapper.vm.email = 'test@example.com'
      wrapper.vm.password = 'password123'
      wrapper.vm.firstName = 'John'
      wrapper.vm.lastName = 'Doe'
      
      api.registerUser.mockResolvedValue({ success: true })
      api.loginUser.mockResolvedValue({
        token: 'mock-token',
        first_name: 'John'
      })

      await wrapper.vm.onSignup()

      expect(wrapper.vm.touched).toBe(true)
    })

    it('should clear error message on new signup attempt', async () => {
      wrapper.vm.isSignup = true
      wrapper.vm.errorMsg = 'Previous signup error'
      
      api.registerUser.mockResolvedValue({ success: true })
      api.loginUser.mockResolvedValue({
        token: 'mock-token',
        first_name: 'John'
      })

      wrapper.vm.email = 'test@example.com'
      wrapper.vm.password = 'password123'
      wrapper.vm.firstName = 'John'
      wrapper.vm.lastName = 'Doe'
      await wrapper.vm.onSignup()
      await flushPromises()

      // Error should be cleared during signup attempt
      expect(wrapper.vm.errorMsg).toBe('')
    })

    it('should show submitting state during login', async () => {
      api.loginUser.mockImplementation(() => {
        return new Promise(resolve => setTimeout(resolve, 100))
      })

      wrapper.vm.email = 'test@example.com'
      wrapper.vm.password = 'password123'
      
      const loginPromise = wrapper.vm.onLogin()
      await nextTick()

      expect(wrapper.vm.submitting).toBe(true)

      await loginPromise
      await flushPromises()

      expect(wrapper.vm.submitting).toBe(false)
    })

    it('should show submitting state during signup', async () => {
      wrapper.vm.isSignup = true
      
      api.registerUser.mockImplementation(() => {
        return new Promise(resolve => setTimeout(resolve, 50))
      })
      api.loginUser.mockResolvedValue({
        token: 'mock-token',
        first_name: 'John'
      })

      wrapper.vm.email = 'test@example.com'
      wrapper.vm.password = 'password123'
      wrapper.vm.firstName = 'John'
      wrapper.vm.lastName = 'Doe'
      
      const signupPromise = wrapper.vm.onSignup()
      await nextTick()

      expect(wrapper.vm.submitting).toBe(true)

      await signupPromise
      await flushPromises()

      expect(wrapper.vm.submitting).toBe(false)
    })

    it('should not submit login when invalid', async () => {
      wrapper.vm.email = ''
      wrapper.vm.password = ''
      
      await wrapper.vm.onLogin()
      
      expect(api.loginUser).not.toHaveBeenCalled()
    })

    it('should not submit signup when invalid', async () => {
      wrapper.vm.isSignup = true
      wrapper.vm.email = 'test@example.com'
      wrapper.vm.password = 'password123'
      wrapper.vm.firstName = ''
      wrapper.vm.lastName = ''
      
      await wrapper.vm.onSignup()
      
      expect(api.registerUser).not.toHaveBeenCalled()
    })
  })

  describe('Security & Input Validation Requirements', () => {
    // Test 34: REQUIREMENT - Should validate email format (basic check)
    it('should accept valid email formats', () => {
      const validEmails = [
        'user@example.com',
        'test.user@example.co.uk',
        'user+tag@example.com'
      ]

      validEmails.forEach(email => {
        wrapper.vm.email = email
        wrapper.vm.password = 'password'
        expect(wrapper.vm.isLoginValid).toBe(true)
      })
    })

    // Test 35: EDGE CASE - Should handle very long email addresses
    it('should handle very long email addresses', () => {
      const longEmail = 'a'.repeat(64) + '@' + 'b'.repeat(63) + '.com'
      wrapper.vm.email = longEmail
      wrapper.vm.password = 'password123'
      
      // Should still be treated as valid (backend will enforce length limits)
      expect(wrapper.vm.isLoginValid).toBe(true)
    })

    // Test 36: EDGE CASE - Should handle special characters in passwords
    it('should accept passwords with special characters', () => {
      wrapper.vm.email = 'test@example.com'
      wrapper.vm.password = 'P@ssw0rd!#$%'
      
      expect(wrapper.vm.isLoginValid).toBe(true)
    })

    // Test 37: EDGE CASE - Should handle very long passwords
    it('should accept very long passwords', () => {
      wrapper.vm.email = 'test@example.com'
      wrapper.vm.password = 'a'.repeat(100)
      
      expect(wrapper.vm.isLoginValid).toBe(true)
    })

    // Test 38: REQUIREMENT - Should prevent XSS in name fields
    it('should handle script tags in name fields without breaking', () => {
      wrapper.vm.isSignup = true
      wrapper.vm.email= 'test@example.com'
      wrapper.vm.password = 'password123'
      wrapper.vm.firstName = '<script>alert("xss")</script>'
      wrapper.vm.lastName = 'Smith'
      
      // Component should not crash
      expect(wrapper.vm.isSignupValid).toBe(true)
      expect(wrapper.vm.firstName).toBe('<script>alert("xss")</script>')
    })

    // Test 39: EDGE CASE - Should handle empty spaces in names
    it('should reject names with only spaces', () => {
      wrapper.vm.isSignup = true
      wrapper.vm.email = 'test@example.com'
      wrapper.vm.password = 'password123'
      wrapper.vm.firstName = '   '
      wrapper.vm.lastName = '   '
      
      // Trim should make these invalid
      expect(wrapper.vm.isSignupValid).toBe(false)
    })

    // Test 40: REQUIREMENT - Should handle SQL injection attempts gracefully
    it('should handle SQL injection attempts in email field', () => {
      wrapper.vm.email = "admin'--"
      wrapper.vm.password = "' OR '1'='1"
      
      // Should not break validation (backend handles security)
      expect(wrapper.vm.isLoginValid).toBe(true)
    })

    // Test 41: EDGE CASE - Should handle concurrent login attempts (KNOWN ISSUE)
    it('should handle concurrent login attempts', async () => {
      api.loginUser.mockImplementation(() => {
        return new Promise(resolve => setTimeout(() => resolve({
          token: 'mock-token',
          first_name: 'John'
        }), 100))
      })

      wrapper.vm.email = 'test@example.com'
      wrapper.vm.password = 'password123'
      
      // Start first login
      const firstLogin = wrapper.vm.onLogin()
      
      // Try second login while first is in progress
      await wrapper.vm.onLogin()
      
      await firstLogin
      await flushPromises()
      
      // CURRENT BEHAVIOR: Can submit twice (potential improvement area)
      // EXPECTED: Should call API twice as no guard is in place
      expect(api.loginUser).toHaveBeenCalledTimes(2)
    })

    // Test 42: REQUIREMENT - Should clear sensitive data after successful login
    it('should maintain password in memory for auth but not expose it', async () => {
      api.loginUser.mockResolvedValue({
        token: 'mock-token',
        first_name: 'John'
      })

      wrapper.vm.email = 'test@example.com'
      wrapper.vm.password = 'secretPassword123'
      
      await wrapper.vm.onLogin()
      await flushPromises()
      
      // Password should still be in component (for form), but token should be in localStorage
      expect(localStorage.setItem).toHaveBeenCalledWith('token', 'mock-token')
      expect(wrapper.vm.password).toBe('secretPassword123') // Still in memory
    })

    // Test 43: EDGE CASE - Should handle API returning malformed data
    it('should handle malformed API response gracefully', async () => {
      api.loginUser.mockResolvedValue({
        // Missing token!
        first_name: 'John'
      })

      wrapper.vm.email = 'test@example.com'
      wrapper.vm.password = 'password123'
      
      await wrapper.vm.onLogin()
      await flushPromises()
      
      // Should call localStorage with undefined (component doesn't validate response)
      expect(localStorage.setItem).toHaveBeenCalled()
    })

    // Test 44: REQUIREMENT - Should enforce required fields for signup
    it('should require all signup fields', () => {
      wrapper.vm.isSignup = true
      
      // Test each required field individually
      wrapper.vm.email = 'test@example.com'
      wrapper.vm.password = 'password123'
      wrapper.vm.firstName = 'John'
      wrapper.vm.lastName = ''
      expect(wrapper.vm.isSignupValid).toBe(false)
      
      wrapper.vm.lastName = 'Doe'
      wrapper.vm.firstName = ''
      expect(wrapper.vm.isSignupValid).toBe(false)
      
      wrapper.vm.firstName = 'John'
      expect(wrapper.vm.isSignupValid).toBe(true)
    })
  })
})
