import { describe, it, expect, beforeEach } from 'vitest'
import Error from './Error.vue'
import { mountWithDefaults, createMockRouter } from '../../test/utils'

describe('Error Component', () => {
  let wrapper

  beforeEach(async () => {
    const mockRouter = createMockRouter([], {
      path: '/error',
      name: 'error',
      query: {}
    })
    await mockRouter.isReady()
    
    wrapper = mountWithDefaults(Error, { router: mockRouter })
  })

  afterEach(() => {
    wrapper.unmount()
  })

  describe('Component Rendering', () => {
    // Test 1: Verify error component mounts with proper structure
    it('should render the error component', () => {
      expect(wrapper.exists()).toBe(true)
      expect(wrapper.find('.error-container').exists()).toBe(true)
    })

    // Test 2: Verify error title displays standard message
    it('should display error title', () => {
      const title = wrapper.find('.error-title')
      expect(title.exists()).toBe(true)
      expect(title.text()).toBe('Something went wrong')
    })

    // Test 3: Verify action buttons section is present
    it('should display error actions', () => {
      const actions = wrapper.find('.error-actions')
      expect(actions.exists()).toBe(true)
    })
  })

  describe('Error Message', () => {
    // Test 4: Verify default message when no error details provided
    it('should display default error message when no query param', () => {
      const message = wrapper.find('.error-message')
      expect(message.exists()).toBe(true)
      expect(message.text()).toBe('An unexpected error occurred.')
    })

    // Test 5: Verify custom error messages from route query parameters
    it('should display custom error message from route query', async () => {
      const mockRouter = createMockRouter([], {
        path: '/error',
        name: 'error',
        query: { message: 'Custom error message' }
      })
      await mockRouter.isReady()

      const customWrapper = mountWithDefaults(Error, { router: mockRouter })

      const message = customWrapper.find('.error-message')
      expect(message.text()).toBe('Custom error message')

      customWrapper.unmount()
    })

    // Test 6: Verify API error messages display correctly
    it('should handle API error messages', async () => {
      const mockRouter = createMockRouter([], {
        path: '/error',
        name: 'error',
        query: { message: 'Failed to fetch data from server' }
      })
      await mockRouter.isReady()

      const customWrapper = mountWithDefaults(Error, { router: mockRouter })

      const message = customWrapper.find('.error-message')
      expect(message.text()).toBe('Failed to fetch data from server')

      customWrapper.unmount()
    })

    // Test 7: Verify network error messages display correctly
    it('should handle network error messages', async () => {
      const mockRouter = createMockRouter([], {
        path: '/error',
        name: 'error',
        query: { message: 'Network request failed' }
      })
      await mockRouter.isReady()

      const customWrapper = mountWithDefaults(Error, { router: mockRouter })

      const message = customWrapper.find('.error-message')
      expect(message.text()).toBe('Network request failed')

      customWrapper.unmount()
    })
  })

  describe('Navigation Actions', () => {
    // Test 8: Verify "Back to Store" link exists and has correct text
    it('should have link to store', () => {
      const storeLink = wrapper.findAll('.action-btn')[0]
      expect(storeLink.exists()).toBe(true)
      expect(storeLink.text()).toBe('Back to Store')
    })

    // Test 9: Verify "Return Home" link exists and has correct text
    it('should have link to home', () => {
      const homeLink = wrapper.findAll('.action-btn')[1]
      expect(homeLink.exists()).toBe(true)
      expect(homeLink.text()).toBe('Return Home')
    })

    // Test 10: Verify RouterLink components are properly rendered
    it('should render RouterLink components', () => {
      const links = wrapper.findAll('.action-btn')
      expect(links).toHaveLength(2)
    })
  })

  describe('Error Container Structure', () => {
    // Test 11: Verify error container has correct CSS class for styling
    it('should have centered layout class', () => {
      const container = wrapper.find('.error-container')
      expect(container.classes()).toContain('error-container')
    })

    // Test 12: Verify all required sections (title, message, actions) exist
    it('should contain all required sections', () => {
      expect(wrapper.find('.error-title').exists()).toBe(true)
      expect(wrapper.find('.error-message').exists()).toBe(true)
      expect(wrapper.find('.error-actions').exists()).toBe(true)
    })
  })

  describe('Computed Properties', () => {
    // Test 13: Verify errorMessage computed property reads from route
    it('should compute error message from route', async () => {
      const mockRouter = createMockRouter([], {
        path: '/error',
        name: 'error',
        query: { message: 'Test error' }
      })
      await mockRouter.isReady()

      const customWrapper = mountWithDefaults(Error, { router: mockRouter })

      expect(customWrapper.vm.errorMessage).toBe('Test error')

      customWrapper.unmount()
    })

    // Test 14: Verify default message when route query is empty
    it('should use default message when route query is empty', async () => {
      const mockRouter = createMockRouter([], {
        path: '/error',
        name: 'error',
        query: {}
      })
      await mockRouter.isReady()

      const customWrapper = mountWithDefaults(Error, { router: mockRouter })

      expect(customWrapper.vm.errorMessage).toBe('An unexpected error occurred.')

      customWrapper.unmount()
    })
  })

  describe('Page Shell', () => {
    // Test 15: Verify component is wrapped in page-shell container
    it('should be wrapped in page-shell', () => {
      const pageShell = wrapper.find('.page-shell')
      expect(pageShell.exists()).toBe(true)
    })

    // Test 16: Verify proper nesting of error container within page shell
    it('should contain error container', () => {
      const pageShell = wrapper.find('.page-shell')
      expect(pageShell.find('.error-container').exists()).toBe(true)
    })
  })

  describe('Error Scenarios', () => {
    // Test 17: Verify 404-style "Page not found" errors display correctly
    it('should handle 404-like errors', async () => {
      const mockRouter = createMockRouter([], {
        path: '/error',
        name: 'error',
        query: { message: 'Page not found' }
      })
      await mockRouter.isReady()

      const customWrapper = mountWithDefaults(Error, { router: mockRouter })

      expect(customWrapper.find('.error-message').text()).toBe('Page not found')

      customWrapper.unmount()
    })

    // Test 18: Verify authentication error messages display correctly
    it('should handle authentication errors', async () => {
      const mockRouter = createMockRouter([], {
        path: '/error',
        name: 'error',
        query: { message: 'Authentication required' }
      })
      await mockRouter.isReady()

      const customWrapper = mountWithDefaults(Error, { router: mockRouter })

      expect(customWrapper.find('.error-message').text()).toBe('Authentication required')

      customWrapper.unmount()
    })

    // Test 19: Verify permission/access denied errors display correctly
    it('should handle permission errors', async () => {
      const mockRouter = createMockRouter([], {
        path: '/error',
        name: 'error',
        query: { message: 'Access denied' }
      })
      await mockRouter.isReady()

      const customWrapper = mountWithDefaults(Error, { router: mockRouter })

      expect(customWrapper.find('.error-message').text()).toBe('Access denied')

      customWrapper.unmount()
    })
  })
})
