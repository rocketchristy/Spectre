import { describe, it, expect, beforeEach, vi } from 'vitest'
import { nextTick } from 'vue'
import UserProfile from './UserProfile.vue'
import { mountWithDefaults, flushPromises } from '../../test/utils'
import { setupApiMocks, mockApiResponses } from '../../test/api-mocks'

// Mock the API module
vi.mock('../../utils/api.js', () => ({
  getUser: vi.fn(),
  updateUser: vi.fn(),
  addAddress: vi.fn(),
  deleteAddress: vi.fn(),
  getUserInventory: vi.fn()
}))

import * as api from '../../utils/api.js'

describe('UserProfile Component', () => {
  let wrapper

  beforeEach(() => {
    // Setup localStorage mock
    const localStorageMock = {
      getItem: vi.fn(),
      setItem: vi.fn(),
      removeItem: vi.fn(),
      clear: vi.fn()
    }
    global.localStorage = localStorageMock
    localStorageMock.getItem.mockReturnValue('mock-token')

    // Setup API mocks with default responses
    api.getUser.mockResolvedValue({
      info: [{
        FIRST_NAME: 'Test',
        LAST_NAME: 'User',
        EMAIL: 'test@example.com'
      }],
      addresses: []
    })
    api.getUserInventory.mockResolvedValue([
      {
        PRODUCT_NAME: 'Test Card',
        QUANTITY_AVAILABLE: 5,
        UNIT_PRICE_CENTS: 1000,
        URL: 'test.jpg',
        MODIFIER_NAME: 'Mint',
        SKU: 'SKU-001',
        INVENTORY_ID: 1
      }
    ])

    wrapper = mountWithDefaults(UserProfile)
  })

  afterEach(() => {
    wrapper.unmount()
    vi.clearAllMocks()
  })

  describe('Component Rendering', () => {
    // Test 1: Verify user profile component mounts correctly
    it('should render the user profile component', () => {
      expect(wrapper.exists()).toBe(true)
    })

    // Test 2: Verify loading state is true on component initialization
    it('should show loading state initially', () => {
      const newWrapper = mountWithDefaults(UserProfile)
      expect(newWrapper.vm.loading).toBe(true)
      newWrapper.unmount()
    })

    // Test 3: Verify getUser API is called on component mount
    it('should call getUser on mount', async () => {
      await flushPromises()
      expect(api.getUser).toHaveBeenCalled()
    })

    // Test 4: Verify getUserInventory API is called on component mount
    it('should call getUserInventory on mount', async () => {
      await flushPromises()
      expect(api.getUserInventory).toHaveBeenCalled()
    })
  })

  describe('User Information Display', () => {
    // Test 5: Verify user information displays after API data loads
    it('should display user information after loading', async () => {
      await flushPromises()
      await nextTick()

      expect(wrapper.vm.userInfo).toBeDefined()
      expect(wrapper.vm.userInfo.FIRST_NAME).toBe('Test')
      expect(wrapper.vm.userInfo.LAST_NAME).toBe('User')
    })

    // Test 6: Verify loading state becomes false after data fetch completes
    it('should set loading to false after data fetch', async () => {
      await flushPromises()
      await nextTick()

      expect(wrapper.vm.loading).toBe(false)
    })
  })

  describe('Modal Management', () => {
    it('should open update modal when openUpdateModal is called', async () => {
      await flushPromises()
      await nextTick()

      wrapper.vm.openUpdateModal()
      await nextTick()

      expect(wrapper.vm.showUpdateModal).toBe(true)
    })

    it('should close update modal when closeUpdateModal is called', async () => {
      wrapper.vm.showUpdateModal = true
      await nextTick()

      wrapper.vm.closeUpdateModal()
      await nextTick()

      expect(wrapper.vm.showUpdateModal).toBe(false)
    })

    it('should open password modal when openPasswordModal is called', () => {
      wrapper.vm.openPasswordModal()
      expect(wrapper.vm.showPasswordModal).toBe(true)
    })

    it('should open address modal when openAddressModal is called', () => {
      wrapper.vm.openAddressModal()
      expect(wrapper.vm.showAddressModal).toBe(true)
    })
  })

  describe('Profile Updates', () => {
    it('should populate update form with current user data', async () => {
      await flushPromises()
      await nextTick()

      wrapper.vm.openUpdateModal()
      await nextTick()

      expect(wrapper.vm.updateFormData.firstName).toBe('Test')
      expect(wrapper.vm.updateFormData.lastName).toBe('User')
      expect(wrapper.vm.updateFormData.email).toBe('test@example.com')
    })

    it('should call updateUser API when submitting update form', async () => {
      await flushPromises()
      
      api.updateUser.mockResolvedValue({ success: true })
      
      wrapper.vm.openUpdateModal()
      await nextTick()

      await wrapper.vm.submitUpdateForm()
      await flushPromises()

      expect(api.updateUser).toHaveBeenCalled()
    })

    it('should close update modal when closeUpdateModal is called', async () => {
      await flushPromises()
      wrapper.vm.showUpdateModal = true
      await nextTick()

      wrapper.vm.closeUpdateModal()
      await nextTick()

      expect(wrapper.vm.showUpdateModal).toBe(false)
    })
  })

  describe('Password Management', () => {
    it('should open password modal', async () => {
      await flushPromises()
      
      wrapper.vm.openPasswordModal()
      expect(wrapper.vm.showPasswordModal).toBe(true)
      expect(wrapper.vm.passwordFormData.newPassword).toBe('')
      expect(wrapper.vm.passwordFormData.confirmPassword).toBe('')
    })

    it('should close password modal', async () => {
      await flushPromises()
      wrapper.vm.showPasswordModal = true
      
      wrapper.vm.closePasswordModal()
      expect(wrapper.vm.showPasswordModal).toBe(false)
    })

    it('should update password successfully when passwords match', async () => {
      await flushPromises()
      await nextTick()
      
      api.updateUser.mockResolvedValue({ success: true })
      
      wrapper.vm.openPasswordModal()
      wrapper.vm.passwordFormData = {
        newPassword: 'newpassword123',
        confirmPassword: 'newpassword123'
      }

      await wrapper.vm.submitPasswordForm()
      await flushPromises()

      expect(api.updateUser).toHaveBeenCalled()
      expect(wrapper.vm.showPasswordModal).toBe(false)
    })
  })

  describe('Address Management', () => {
    it('should open address modal with empty form', async () => {
      await flushPromises()
      
      wrapper.vm.openAddressModal()
      
      expect(wrapper.vm.showAddressModal).toBe(true)
      expect(wrapper.vm.addressFormData.full_name).toBe('')
      expect(wrapper.vm.addressFormData.line1).toBe('')
    })

    it('should close address modal', async () => {
      await flushPromises()
      wrapper.vm.showAddressModal = true
      
      wrapper.vm.closeAddressModal()
      expect(wrapper.vm.showAddressModal).toBe(false)
    })

    it('should submit address form successfully', async () => {
      await flushPromises()
      
      api.addAddress.mockResolvedValue({ success: true })
      
      wrapper.vm.openAddressModal()
      wrapper.vm.addressFormData = {
        full_name: 'John Doe',
        line1: '123 Main St',
        line2: 'Apt 4',
        city: 'City',
        region: 'State',
        postal_code: '12345',
        country_code: 'US',
        phone: '555-1234'
      }

      await wrapper.vm.submitAddressForm()
      await flushPromises()

      expect(api.addAddress).toHaveBeenCalled()
      expect(wrapper.vm.showAddressModal).toBe(false)
    })

    it('should handle address submission error', async () => {
      await flushPromises()
      
      const errorMsg = 'Failed to add address'
      api.addAddress.mockRejectedValue(new Error(errorMsg))
      
      wrapper.vm.openAddressModal()
      await wrapper.vm.submitAddressForm()
      await flushPromises()

      expect(wrapper.vm.errorMsg).toBe(errorMsg)
    })

    it('should remove address successfully', async () => {
      await flushPromises()
      
      api.deleteAddress.mockResolvedValue({ success: true })
      
      await wrapper.vm.removeAddress(1)
      await flushPromises()

      expect(api.deleteAddress).toHaveBeenCalledWith(1)
      expect(api.getUser).toHaveBeenCalled()
    })

    it('should handle remove address error', async () => {
      await flushPromises()
      
      const errorMsg = 'Failed to delete address'
      api.deleteAddress.mockRejectedValue(new Error(errorMsg))
      
      await wrapper.vm.removeAddress(1)
      await flushPromises()

      expect(wrapper.vm.errorMsg).toBe(errorMsg)
    })
  })

  describe('User Cards', () => {
    it('should fetch user cards on mount', async () => {
      await flushPromises()
      await nextTick()

      expect(api.getUserInventory).toHaveBeenCalled()
      expect(wrapper.vm.currentUserCards.length).toBeGreaterThan(0)
    })

    it('should handle fetch user cards error gracefully', async () => {
      api.getUserInventory.mockRejectedValue(new Error('Failed to fetch'))
      
      const newWrapper = mountWithDefaults(UserProfile)

      await flushPromises()
      
      expect(newWrapper.vm.currentUserCards).toEqual([])
      newWrapper.unmount()
    })
  })

  describe('Logout and Redirect', () => {
    it('should logout and clear token from localStorage', async () => {
      await flushPromises()
      
      wrapper.vm.logout()
      
      expect(localStorage.removeItem).toHaveBeenCalledWith('token')
      expect(localStorage.removeItem).toHaveBeenCalledWith('firstName')
    })

    it('should redirect to login page', async () => {
      await flushPromises()
      
      wrapper.vm.redirectToLogin()
      
      expect(wrapper.vm.$router.push).toHaveBeenCalledWith('/')
    })
  })

  describe('Error Handling', () => {
    it('should display error message when fetch fails', async () => {
      const errorMessage = 'Failed to fetch user data'
      api.getUser.mockRejectedValue(new Error(errorMessage))

      const newWrapper = mountWithDefaults(UserProfile)
      await flushPromises()
      await nextTick()

      expect(newWrapper.vm.errorMsg).toBe(errorMessage)
      newWrapper.unmount()
    })

    it('should show error when passwords do not match', async () => {
      await flushPromises()
      
      wrapper.vm.openPasswordModal()
      wrapper.vm.passwordFormData = {
        newPassword: 'password123',
        confirmPassword: 'different456'
      }

      await wrapper.vm.submitPasswordForm()

      expect(wrapper.vm.errorMsg).toBe('Passwords do not match')
    })

    it('should handle update form errors', async () => {
      await flushPromises()
      
      const errorMsg = 'Update failed'
      api.updateUser.mockRejectedValue(new Error(errorMsg))
      
      wrapper.vm.openUpdateModal()
      await wrapper.vm.submitUpdateForm()
      await flushPromises()

      expect(wrapper.vm.errorMsg).toBe(errorMsg)
    })

    it('should handle password update errors', async () => {
      await flushPromises()
      
      const errorMsg = 'Password update failed'
      api.updateUser.mockRejectedValue(new Error(errorMsg))
      
      wrapper.vm.openPasswordModal()
      wrapper.vm.passwordFormData = {
        newPassword: 'newpass123',
        confirmPassword: 'newpass123'
      }
      
      await wrapper.vm.submitPasswordForm()
      await flushPromises()

      expect(wrapper.vm.errorMsg).toBe(errorMsg)
    })
  })

  describe('Form Interactions', () => {
    it('should populate address form correctly when opened', async () => {
      await flushPromises()
      
      wrapper.vm.openAddressModal()
      
      expect(wrapper.vm.addressFormData.full_name).toBe('')
      expect(wrapper.vm.addressFormData.line1).toBe('')
      expect(wrapper.vm.addressFormData.line2).toBe('')
      expect(wrapper.vm.addressFormData.city).toBe('')
      expect(wrapper.vm.addressFormData.region).toBe('')
      expect(wrapper.vm.addressFormData.postal_code).toBe('')
      expect(wrapper.vm.addressFormData.country_code).toBe('')
      expect(wrapper.vm.addressFormData.phone).toBe('')
      expect(wrapper.vm.showAddressModal).toBe(true)
    })

    it('should populate password form correctly when opened', async () => {
      await flushPromises()
      
      wrapper.vm.openPasswordModal()
      
      expect(wrapper.vm.passwordFormData.newPassword).toBe('')
      expect(wrapper.vm.passwordFormData.confirmPassword).toBe('')
      expect(wrapper.vm.showPasswordModal).toBe(true)
      expect(wrapper.vm.errorMsg).toBe('')
    })

    it('should reset error when opening update modal', async () => {
      await flushPromises()
      
      wrapper.vm.errorMsg = 'Some error'
      wrapper.vm.openUpdateModal()
      
      expect(wrapper.vm.errorMsg).toBe('')
    })

    it('should reset error when opening password modal', async () => {
      await flushPromises()
      
      wrapper.vm.errorMsg = 'Some error'
      wrapper.vm.openPasswordModal()
      
      expect(wrapper.vm.errorMsg).toBe('')
    })

    it('should reset error when opening address modal', async () => {
      await flushPromises()
      
      wrapper.vm.errorMsg = 'Some error'
      wrapper.vm.openAddressModal()
      
      expect(wrapper.vm.errorMsg).toBe('')
    })

    it('should set submitting state during update', async () => {
      await flushPromises()
      
      api.updateUser.mockImplementation(() => {
        return new Promise(resolve => setTimeout(resolve, 50))
      })
      
      wrapper.vm.openUpdateModal()
      const updatePromise = wrapper.vm.submitUpdateForm()
      await nextTick()
      
      expect(wrapper.vm.submitting).toBe(true)
      
      await updatePromise
      await flushPromises()
      
      expect(wrapper.vm.submitting).toBe(false)
    })

    it('should set submitting state during password update', async () => {
      await flushPromises()
      
      api.updateUser.mockImplementation(() => {
        return new Promise(resolve => setTimeout(resolve, 50))
      })
      
      wrapper.vm.openPasswordModal()
      wrapper.vm.passwordFormData = {
        newPassword: 'test123',
        confirmPassword: 'test123'
      }
      
      const passwordPromise = wrapper.vm.submitPasswordForm()
      await nextTick()
      
      expect(wrapper.vm.submitting).toBe(true)
      
      await passwordPromise
      await flushPromises()
      
      expect(wrapper.vm.submitting).toBe(false)
    })

    it('should set submitting state during address submission', async () => {
      await flushPromises()
      
      api.addAddress.mockImplementation(() => {
        return new Promise(resolve => setTimeout(resolve, 50))
      })
      
      wrapper.vm.openAddressModal()
      wrapper.vm.addressFormData = {
        full_name: 'Test User',
        line1: '123 St',
        line2: '',
        city: 'City',
        region: 'ST',
        postal_code: '12345',
        country_code: 'US',
        phone: '555-1234'
      }
      
      const addressPromise = wrapper.vm.submitAddressForm()
      await nextTick()
      
      expect(wrapper.vm.submitting).toBe(true)
      
      await addressPromise
      await flushPromises()
      
      expect(wrapper.vm.submitting).toBe(false)
    })

    it('should refresh profile after successful update', async () => {
      await flushPromises()
      
      api.updateUser.mockResolvedValue({ success: true })
      api.getUser.mockResolvedValue({
        info: [{
          FIRST_NAME: 'Updated',
          LAST_NAME: 'Name',
          EMAIL: 'updated@example.com'
        }],
        addresses: []
      })
      
      wrapper.vm.openUpdateModal()
      await wrapper.vm.submitUpdateForm()
      await flushPromises()
      
      expect(api.getUser).toHaveBeenCalledTimes(2) // Once on mount, once after update
    })

    it('should refresh profile after adding address', async () => {
      await flushPromises()
      
      api.addAddress.mockResolvedValue({ success: true })
      
      wrapper.vm.openAddressModal()
      wrapper.vm.addressFormData = {
        full_name: 'Test',
        line1: '123 St',
        line2: '',
        city: 'City',
        region: 'ST',
        postal_code: '12345',
        country_code: 'US',
        phone: '555-1234'
      }
      
      await wrapper.vm.submitAddressForm()
      await flushPromises()
      
      expect(api.getUser).toHaveBeenCalledTimes(2) // Once on mount, once after address add
    })

    it('should refresh profile after removing address', async () => {
      await flushPromises()
      
      api.deleteAddress.mockResolvedValue({ success: true })
      
      await wrapper.vm.removeAddress(1)
      await flushPromises()
      
      expect(api.getUser).toHaveBeenCalledTimes(2) // Once on mount, once after address removal
    })
  })

  describe('Component State', () => {
    it('should determine login state from localStorage', () => {
      localStorage.getItem.mockReturnValue('mock-token')
      const newWrapper = mountWithDefaults(UserProfile)
      
      expect(newWrapper.vm.isLoggedIn).toBe(true)
      
      newWrapper.unmount()
    })

    it('should show not logged in when no token', () => {
      localStorage.getItem.mockReturnValue(null)
      const newWrapper = mountWithDefaults(UserProfile)
      
      expect(newWrapper.vm.isLoggedIn).toBe(false)
      
      newWrapper.unmount()
    })

    it('should prevent password update when passwords do not match', async () => {
      await flushPromises()
      
      wrapper.vm.openPasswordModal()
      wrapper.vm.passwordFormData = {
        newPassword: 'password123',
        confirmPassword: 'different'
      }

      await wrapper.vm.submitPasswordForm()
      await nextTick()

      expect(wrapper.vm.errorMsg).toBe('Passwords do not match')
      expect(api.updateUser).not.toHaveBeenCalled()
    })
  })
})
