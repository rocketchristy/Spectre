import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import Cart from './Cart.vue'
import { createMockRouter, createMockCartItems } from '../../test/utils'

describe('Cart Component', () => {
  let wrapper
  let mockRouter

  beforeEach(() => {
    mockRouter = createMockRouter()
    wrapper = mount(Cart, {
      global: {
        plugins: [mockRouter],
        stubs: {
          RouterLink: {
            template: '<a><slot /></a>',
            props: ['to']
          }
        }
      }
    })
  })

  afterEach(() => {
    wrapper.unmount()
  })

  describe('Component Rendering', () => {
    // Test 1: Verify cart component mounts and displays correct title
    it('should render the cart component', () => {
      expect(wrapper.exists()).toBe(true)
      expect(wrapper.find('h1.page-title').text()).toBe('Your Cart')
    })

    // Test 2: Verify empty state shows appropriate message and browse button
    it('should display empty cart message when no items', async () => {
      expect(wrapper.vm.cartItems).toHaveLength(0)
      
      const emptyState = wrapper.find('.empty-state')
      expect(emptyState.exists()).toBe(true)
      expect(emptyState.text()).toContain('Your cart is empty')
      
      const browseButton = wrapper.find('.action-btn')
      expect(browseButton.exists()).toBe(true)
      expect(browseButton.text()).toBe('Browse the Store')
    })

    // Test 3: Verify cart items render with correct information when populated
    it('should display cart items when items exist', async () => {
      const mockItems = createMockCartItems(2)
      wrapper.vm.cartItems = mockItems
      await nextTick()

      const cartItems = wrapper.findAll('.list-row')
      expect(cartItems).toHaveLength(2)
      
      // Check first item
      expect(cartItems[0].text()).toContain(mockItems[0].name)
      expect(cartItems[0].text()).toContain(`$${mockItems[0].price.toFixed(2)}`)
    })
  })

  describe('Cart Calculations', () => {
    // Test 4: Verify cart total is computed correctly (price × quantity summed)
    it('should calculate total price correctly', async () => {
      const mockItems = [
        { id: 1, name: 'Item 1', price: 10.00, quantity: 2, image: '📦', type: 'pack' },
        { id: 2, name: 'Item 2', price: 15.50, quantity: 1, image: '🎴', type: 'card' },
      ]
      wrapper.vm.cartItems = mockItems
      await nextTick()

      // Total should be: (10 * 2) + (15.50 * 1) = 35.50
      expect(wrapper.vm.cartTotal).toBe('35.50')
      
      const summaryBar = wrapper.find('.summary-bar__total')
      expect(summaryBar.text()).toContain('$35.50')
    })

    // Test 5: Verify total dynamically updates when quantities are modified
    it('should update total when item quantities change', async () => {
      const mockItems = [
        { id: 1, name: 'Item 1', price: 10, quantity: 1, image: '📦', type: 'pack' }
      ]
      wrapper.vm.cartItems = mockItems
      await nextTick()

      expect(wrapper.vm.cartTotal).toBe('10.00')

      // Increase quantity
      wrapper.vm.cartItems[0].quantity = 3
      await nextTick()

      expect(wrapper.vm.cartTotal).toBe('30.00')
    })
  })

  describe('Item Management', () => {
    // Test 6: Verify delete button removes items from cart
    it('should remove item from cart when delete is clicked', async () => {
      const mockItems = createMockCartItems(3)
      wrapper.vm.cartItems = mockItems
      await nextTick()

      expect(wrapper.vm.cartItems).toHaveLength(3)

      // Find and click the first delete button
      const deleteButtons = wrapper.findAll('.btn-danger')
      await deleteButtons[0].trigger('click')
      await nextTick()

      expect(wrapper.vm.cartItems).toHaveLength(2)
      expect(wrapper.vm.cartItems.find(item => item.id === 1)).toBeUndefined()
    })

    // Test 7: Verify plus button increments item quantity
    it('should increase quantity when plus button is clicked', async () => {
      const mockItems = [
        { id: 1, name: 'Item 1', price: 10, quantity: 2, image: '📦', type: 'pack' }
      ]
      wrapper.vm.cartItems = mockItems
      await nextTick()

      const quantityControls = wrapper.find('.quantity-control')
      const plusButton = quantityControls.findAll('button')[1] // Second button is plus
      
      await plusButton.trigger('click')
      await nextTick()

      expect(wrapper.vm.cartItems[0].quantity).toBe(3)
    })

    // Test 8: Verify minus button decrements item quantity
    it('should decrease quantity when minus button is clicked', async () => {
      const mockItems = [
        { id: 1, name: 'Item 1', price: 10, quantity: 3, image: '📦', type: 'pack' }
      ]
      wrapper.vm.cartItems = mockItems
      await nextTick()

      const quantityControls = wrapper.find('.quantity-control')
      const minusButton = quantityControls.findAll('button')[0] // First button is minus
      
      await minusButton.trigger('click')
      await nextTick()

      expect(wrapper.vm.cartItems[0].quantity).toBe(2)
    })

    // Test 9: Verify minimum quantity enforcement (button disabled at qty=1)
    it('should not decrease quantity below 1', async () => {
      const mockItems = [
        { id: 1, name: 'Item 1', price: 10, quantity: 1, image: '📦', type: 'pack' }
      ]
      wrapper.vm.cartItems = mockItems
      await nextTick()

      const quantityControls = wrapper.find('.quantity-control')
      const minusButton = quantityControls.findAll('button')[0]
      
      // Button should be disabled
      expect(minusButton.attributes('disabled')).toBeDefined()
      
      await minusButton.trigger('click')
      await nextTick()

      expect(wrapper.vm.cartItems[0].quantity).toBe(1)
    })

    // Test 10: Verify quantity value displays correctly in the UI
    it('should display correct quantity value', async () => {
      const mockItems = [
        { id: 1, name: 'Item 1', price: 10, quantity: 5, image: '📦', type: 'pack' }
      ]
      wrapper.vm.cartItems = mockItems
      await nextTick()

      const quantityValue = wrapper.find('.quantity-control__value')
      expect(quantityValue.text()).toBe('5')
    })
  })

  describe('Checkout Process', () => {
    // Test 11: Verify checkout button navigates to order history page
    it('should redirect to order history when checkout button is clicked', async () => {
      const mockItems = createMockCartItems(1)
      wrapper.vm.cartItems = mockItems
      await nextTick()

      const checkoutButton = wrapper.find('.summary-bar .action-btn')
      await checkoutButton.trigger('click')
      await nextTick()

      expect(mockRouter.push).toHaveBeenCalledWith({ name: 'orderHistory' })
    })

    // Test 12: Verify checkout button hidden when cart has no items
    it('should not show checkout button when cart is empty', () => {
      wrapper.vm.cartItems = []
      
      const checkoutButton = wrapper.find('.summary-bar .action-btn')
      expect(checkoutButton.exists()).toBe(false)
    })
  })

  describe('Loading State', () => {
    // Test 13: Verify loading indicator appears during data fetch
    it('should display loading message when loading is true', async () => {
      wrapper.vm.loading = true
      await nextTick()

      const loadingMessage = wrapper.find('.empty-state')
      expect(loadingMessage.exists()).toBe(true)
      expect(loadingMessage.text()).toBe('Loading…')
    })

    // Test 14: Verify cart items don't render during loading state
    it('should not display cart items when loading', async () => {
      wrapper.vm.loading = true
      wrapper.vm.cartItems = createMockCartItems(2)
      await nextTick()

      const cartItems = wrapper.findAll('.list-row')
      expect(cartItems).toHaveLength(0)
    })
  })

  describe('Item Display', () => {
    // Test 15: Verify all item properties (name, price, quantity, image) render correctly
    it('should display item properties correctly', async () => {
      const mockItems = [
        { 
          id: 1, 
          name: 'Rare Card Pack', 
          price: 25.99, 
          quantity: 2, 
          image: '📦',
          type: 'pack' 
        }
      ]
      wrapper.vm.cartItems = mockItems
      await nextTick()

      const listRow = wrapper.find('.list-row')
      
      // Check icon
      expect(listRow.find('.list-row__icon').text()).toBe('📦')
      
      // Check name
      expect(listRow.find('.list-row__info strong').text()).toBe('Rare Card Pack')
      
      // Check price per item
      expect(listRow.find('.text-muted').text()).toBe('$25.99 each')
      
      // Check total for this item (25.99 * 2 = 51.98)
      expect(listRow.find('.list-row__price').text()).toBe('$51.98')
    })

    // Test 16: Verify multiple cart items render in list format
    it('should show multiple items in the list', async () => {
      const mockItems = createMockCartItems(4)
      wrapper.vm.cartItems = mockItems
      await nextTick()

      const items = wrapper.findAll('.list-row')
      expect(items).toHaveLength(4)
      
      items.forEach((item, index) => {
        expect(item.find('strong').text()).toBe(mockItems[index].name)
      })
    })
  })

  describe('Business Requirements & Edge Cases', () => {
    // Test 17: REQUIREMENT - Cart total must always have exactly 2 decimal places
    it('should always format total with 2 decimal places', async () => {
      const mockItems = [
        { id: 1, name: 'Item', price: 10, quantity: 1, image: '📦', type: 'pack' }
      ]
      wrapper.vm.cartItems = mockItems
      await nextTick()

      const total = wrapper.vm.cartTotal
      expect(total).toMatch(/^\d+\.\d{2}$/)
      expect(total).toBe('10.00')
    })

    // Test 18: EDGE CASE - Cart should handle very large quantities correctly
    it('should handle large quantities without overflow', async () => {
      const mockItems = [
        { id: 1, name: 'Item', price: 100.00, quantity: 999, image: '📦', type: 'pack' }
      ]
      wrapper.vm.cartItems = mockItems
      await nextTick()

      // 100 * 999 = 99,900.00
      expect(wrapper.vm.cartTotal).toBe('99900.00')
    })

    // Test 19: EDGE CASE - Cart should handle very large prices correctly
    it('should handle expensive items without overflow', async () => {
      const mockItems = [
        { id: 1, name: 'Rare Item', price: 9999.99, quantity: 5, image: '🎴', type: 'card' }
      ]
      wrapper.vm.cartItems = mockItems
      await nextTick()

      // 9999.99 * 5 = 49,999.95
      expect(wrapper.vm.cartTotal).toBe('49999.95')
    })

    // Test 20: EDGE CASE - Cart should handle floating point precision correctly
    it('should handle decimal precision correctly', async () => {
      const mockItems = [
        { id: 1, name: 'Item 1', price: 0.10, quantity: 1, image: '📦', type: 'pack' },
        { id: 2, name: 'Item 2', price: 0.20, quantity: 1, image: '📦', type: 'pack' }
      ]
      wrapper.vm.cartItems = mockItems
      await nextTick()

      // Should be 0.30, not 0.30000000004
      expect(wrapper.vm.cartTotal).toBe('0.30')
    })

    // Test 21: REQUIREMENT - Cart total must never be negative
    it('should never have negative total', async () => {
      const mockItems = [
        { id: 1, name: 'Item', price: 10.00, quantity: 1, image: '📦', type: 'pack' }
      ]
      wrapper.vm.cartItems = mockItems
      await nextTick()

      const total = parseFloat(wrapper.vm.cartTotal)
      expect(total).toBeGreaterThanOrEqual(0)
    })

    // Test 22: EDGE CASE - Cart with single item at quantity 1 (boundary)
    it('should handle cart with single item at minimum quantity', async () => {
      const mockItems = [
        { id: 1, name: 'Single Item', price: 5.99, quantity: 1, image: '🎴', type: 'card' }
      ]
      wrapper.vm.cartItems = mockItems
      await nextTick()

      expect(wrapper.vm.cartTotal).toBe('5.99')
      expect(wrapper.vm.cartItems).toHaveLength(1)
      
      // Minus button should be disabled
      const minusButton = wrapper.find('.quantity-control button')
      expect(minusButton.attributes('disabled')).toBeDefined()
    })

    // Test 23: EDGE CASE - Removing last item should show empty state
    it('should show empty state after removing last item', async () => {
      const mockItems = [
        { id: 1, name: 'Only Item', price: 10, quantity: 1, image: '📦', type: 'pack' }
      ]
      wrapper.vm.cartItems = mockItems
      await nextTick()

      // Remove the item
      const deleteButton = wrapper.find('.btn-danger')
      await deleteButton.trigger('click')
      await nextTick()

      // Should show empty state
      expect(wrapper.vm.cartItems).toHaveLength(0)
      const emptyState = wrapper.find('.empty-state')
      expect(emptyState.exists()).toBe(true)
      expect(emptyState.text()).toContain('Your cart is empty')
    })

    // Test 24: REQUIREMENT - Prices should always display with 2 decimal places
    it('should always display prices with 2 decimal places', async () => {
      const mockItems = [
        { id: 1, name: 'Item 1', price: 5, quantity: 1, image: '📦', type: 'pack' },
        { id: 2, name: 'Item 2', price: 10.5, quantity: 1, image: '📦', type: 'pack' }
      ]
      wrapper.vm.cartItems = mockItems
      await nextTick()

      const rows = wrapper.findAll('.list-row')
      // Check that prices are formatted
      expect(rows[0].text()).toContain('$5.00')
      expect(rows[1].text()).toContain('$10.50')
    })

    // Test 25: EDGE CASE - Multiple identical items should be separate entries
    it('should handle multiple separate entries of same product', async () => {
      const mockItems = [
        { id: 1, name: 'Card Pack', price: 10, quantity: 2, image: '📦', type: 'pack' },
        { id: 2, name: 'Card Pack', price: 10, quantity: 3, image: '📦', type: 'pack' }
      ]
      wrapper.vm.cartItems = mockItems
      await nextTick()

      // Should show 2 separate rows
      const rows = wrapper.findAll('.list-row')
      expect(rows).toHaveLength(2)
      
      // Total should be (10*2) + (10*3) = 50
      expect(wrapper.vm.cartTotal).toBe('50.00')
    })
  })
})
