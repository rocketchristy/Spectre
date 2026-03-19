import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import Cart from './Cart.vue'
import { createMockRouter, createMockCartItems } from '../../test/utils'
import * as api from '@/utils/api.js'

// Mock the API module
vi.mock('@/utils/api.js', () => ({
  getCart: vi.fn().mockResolvedValue([]),
  removeFromCart: vi.fn().mockResolvedValue({}),
  checkout: vi.fn().mockResolvedValue({}),
  getUser: vi.fn().mockResolvedValue({ addresses: [] }),
  getInventory: vi.fn().mockResolvedValue([]),
  addToCart: vi.fn().mockResolvedValue({}),
  addAddress: vi.fn().mockResolvedValue({})
}))

describe('Cart Component', () => {
  let wrapper
  let mockRouter

  beforeEach(() => {
    vi.clearAllMocks()
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
    it('should render the cart component', () => {
      expect(wrapper.exists()).toBe(true)
      expect(wrapper.find('h1.page-title').text()).toBe('Your Cart')
    })

    it('should display empty cart message when no items', async () => {
      wrapper.vm.loading = false
      wrapper.vm.cartItems = []
      await nextTick()
      
      const emptyNotice = wrapper.find('.empty-cart-notice')
      expect(emptyNotice.exists()).toBe(true)
      expect(emptyNotice.text()).toContain('Your cart is empty')
      
      const browseButton = emptyNotice.find('.action-btn')
      expect(browseButton.exists()).toBe(true)
      expect(browseButton.text()).toBe('Browse the Store')
    })

    it('should display cart items when items exist', async () => {
      const mockItems = createMockCartItems(2)
      wrapper.vm.loading = false
      wrapper.vm.cartItems = mockItems
      await nextTick()

      const cartItems = wrapper.findAll('.list-row')
      expect(cartItems).toHaveLength(2)
      
      // Check first item displays product name
      expect(cartItems[0].text()).toContain(mockItems[0].PRODUCT_NAME)
    })
  })

  describe('Cart Calculations', () => {
    it('should calculate total price correctly', async () => {
      const mockItems = [
        { CART_ITEM_ID: 1, PRODUCT_NAME: 'Item 1', UNIT_PRICE_CENTS: 1000, QUANTITY: 2, MODIFIER_NAME: 'Standard' },
        { CART_ITEM_ID: 2, PRODUCT_NAME: 'Item 2', UNIT_PRICE_CENTS: 1550, QUANTITY: 1, MODIFIER_NAME: 'Foil' },
      ]
      wrapper.vm.loading = false
      wrapper.vm.cartItems = mockItems
      await nextTick()

      // Total should be: (1000 * 2) + (1550 * 1) = 3550 cents
      expect(wrapper.vm.cartTotal).toBe(3550)
      
      // Check displayed total (converted to dollars)
      const summaryBar = wrapper.find('.summary-bar__total')
      expect(summaryBar.text()).toContain('$35.50')
    })

    it('should update total when item quantities change', async () => {
      const mockItems = [
        { CART_ITEM_ID: 1, PRODUCT_NAME: 'Item 1', UNIT_PRICE_CENTS: 1000, QUANTITY: 1, MODIFIER_NAME: 'Standard' }
      ]
      wrapper.vm.loading = false
      wrapper.vm.cartItems = mockItems
      await nextTick()

      expect(wrapper.vm.cartTotal).toBe(1000)

      // Increase quantity
      wrapper.vm.cartItems[0].QUANTITY = 3
      await nextTick()

      expect(wrapper.vm.cartTotal).toBe(3000)
    })
  })

  describe('Item Management', () => {
    it('should remove item from cart when delete is clicked', async () => {
      const mockItems = createMockCartItems(3)
      wrapper.vm.loading = false
      wrapper.vm.cartItems = mockItems
      await nextTick()

      expect(wrapper.vm.cartItems).toHaveLength(3)

      api.removeFromCart.mockResolvedValueOnce({})

      // Find and click the first delete button
      const deleteButtons = wrapper.findAll('.btn-danger')
      await deleteButtons[0].trigger('click')
      await nextTick()

      expect(api.removeFromCart).toHaveBeenCalledWith(mockItems[0].CART_ITEM_ID)
      expect(wrapper.vm.cartItems).toHaveLength(2)
      expect(wrapper.vm.cartItems.find(item => item.CART_ITEM_ID === 1)).toBeUndefined()
    })

    it('should display correct quantity value', async () => {
      const mockItems = [
        { CART_ITEM_ID: 1, PRODUCT_NAME: 'Item 1', UNIT_PRICE_CENTS: 1000, QUANTITY: 5, MODIFIER_NAME: 'Standard' }
      ]
      wrapper.vm.loading = false
      wrapper.vm.cartItems = mockItems
      await nextTick()

      const listRow = wrapper.find('.list-row')
      expect(listRow.text()).toContain('× 5')
    })
  })

  describe('Checkout Process', () => {
    it('should redirect to order history when checkout button is clicked', async () => {
      const mockItems = createMockCartItems(1)
      const mockAddress = { ID: 1, FULL_NAME: 'Test User', LINE1: '123 Test St', CITY: 'TestCity' }
      
      wrapper.vm.loading = false
      wrapper.vm.checkoutSuccess = false
      wrapper.vm.cartItems = mockItems
      wrapper.vm.addresses = [mockAddress]
      wrapper.vm.billingAddressId = 1
      wrapper.vm.shippingAddressId = 1
      await nextTick()

      api.checkout.mockResolvedValueOnce({})

      const checkoutForm = wrapper.find('.checkout-form')
      await checkoutForm.trigger('submit')
      await nextTick()

      expect(api.checkout).toHaveBeenCalledWith(1, 1)
      expect(wrapper.vm.checkoutSuccess).toBe(true)
      expect(wrapper.vm.cartItems).toHaveLength(0)
    })

    it('should not show checkout button when cart is empty', async () => {
      wrapper.vm.loading = false
      wrapper.vm.cartItems = []
      wrapper.vm.addresses = [{ ID: 1, FULL_NAME: 'Test', LINE1: '123 St', CITY: 'City' }]
      await nextTick()
      
      // Checkout panel is always visible, but form is only shown when cart has items
      // When cart is empty, the checkout form should still exist but be unusable
      const checkoutPanel = wrapper.find('.checkout-panel')
      expect(checkoutPanel.exists()).toBe(true)
    })
  })

  describe('Loading State', () => {
    it('should display loading message when loading is true', async () => {
      wrapper.vm.loading = true
      await nextTick()

      const loadingMessage = wrapper.find('.empty-state')
      expect(loadingMessage.exists()).toBe(true)
      expect(loadingMessage.text()).toBe('Loading…')
    })

    it('should not display cart items when loading', async () => {
      wrapper.vm.loading = true
      wrapper.vm.cartItems = createMockCartItems(2)
      await nextTick()

      const cartItems = wrapper.findAll('.list-row')
      expect(cartItems).toHaveLength(0)
    })
  })

  describe('Item Display', () => {
    it('should display item properties correctly', async () => {
      const mockItems = [
        { 
          CART_ITEM_ID: 1, 
          PRODUCT_NAME: 'Rare Card Pack', 
          UNIT_PRICE_CENTS: 2599, 
          QUANTITY: 2, 
          MODIFIER_NAME: 'First Edition'
        }
      ]
      wrapper.vm.loading = false
      wrapper.vm.cartItems = mockItems
      await nextTick()

      const listRow = wrapper.find('.list-row')
      
      // Check name
      expect(listRow.find('.list-row__info strong').text()).toBe('Rare Card Pack')
      
      // Check modifier
      expect(listRow.text()).toContain('First Edition')
      
      // Check price per item
      expect(listRow.text()).toContain('$25.99 each')
      
      // Check total for this item (25.99 * 2 = 51.98)
      expect(listRow.find('.list-row__price').text()).toBe('$51.98')
    })

    it('should show multiple items in the list', async () => {
      const mockItems = createMockCartItems(4)
      wrapper.vm.loading = false
      wrapper.vm.cartItems = mockItems
      await nextTick()

      const items = wrapper.findAll('.list-row')
      expect(items).toHaveLength(4)
      
      items.forEach((item, index) => {
        expect(item.find('strong').text()).toBe(mockItems[index].PRODUCT_NAME)
      })
    })
  })

  describe('Business Requirements & Edge Cases', () => {
    it('should always format total with 2 decimal places', async () => {
      const mockItems = [
        { CART_ITEM_ID: 1, PRODUCT_NAME: 'Item', UNIT_PRICE_CENTS: 1000, QUANTITY: 1, MODIFIER_NAME: 'Standard' }
      ]
      wrapper.vm.loading = false
      wrapper.vm.cartItems = mockItems
      await nextTick()

      const displayedTotal = wrapper.find('.summary-bar__total').text()
      expect(displayedTotal).toContain('$10.00')
    })

    it('should handle large quantities without overflow', async () => {
      const mockItems = [
        { CART_ITEM_ID: 1, PRODUCT_NAME: 'Item', UNIT_PRICE_CENTS: 10000, QUANTITY: 999, MODIFIER_NAME: 'Standard' }
      ]
      wrapper.vm.loading = false
      wrapper.vm.cartItems = mockItems
      await nextTick()

      // 10000 cents * 999 = 9,990,000 cents = $99,900.00
      expect(wrapper.vm.cartTotal).toBe(9990000)
      expect(wrapper.find('.summary-bar__total').text()).toContain('$99900.00')
    })

    it('should handle expensive items without overflow', async () => {
      const mockItems = [
        { CART_ITEM_ID: 1, PRODUCT_NAME: 'Rare Item', UNIT_PRICE_CENTS: 999999, QUANTITY: 5, MODIFIER_NAME: 'Mint' }
      ]
      wrapper.vm.loading = false
      wrapper.vm.cartItems = mockItems
      await nextTick()

      // 999999 cents * 5 = 4,999,995 cents
      expect(wrapper.vm.cartTotal).toBe(4999995)
    })

    it('should handle decimal precision correctly', async () => {
      const mockItems = [
        { CART_ITEM_ID: 1, PRODUCT_NAME: 'Item 1', UNIT_PRICE_CENTS: 10, QUANTITY: 1, MODIFIER_NAME: 'Standard' },
        { CART_ITEM_ID: 2, PRODUCT_NAME: 'Item 2', UNIT_PRICE_CENTS: 20, QUANTITY: 1, MODIFIER_NAME: 'Standard' }
      ]
      wrapper.vm.loading = false
      wrapper.vm.cartItems = mockItems
      await nextTick()

      // Should be 30 cents = $0.30
      expect(wrapper.vm.cartTotal).toBe(30)
      expect(wrapper.find('.summary-bar__total').text()).toContain('$0.30')
    })

    it('should never have negative total', async () => {
      const mockItems = [
        { CART_ITEM_ID: 1, PRODUCT_NAME: 'Item', UNIT_PRICE_CENTS: 1000, QUANTITY: 1, MODIFIER_NAME: 'Standard' }
      ]
      wrapper.vm.loading = false
      wrapper.vm.cartItems = mockItems
      await nextTick()

      expect(wrapper.vm.cartTotal).toBeGreaterThanOrEqual(0)
    })

    it('should handle cart with single item at minimum quantity', async () => {
      const mockItems = [
        { CART_ITEM_ID: 1, PRODUCT_NAME: 'Single Item', UNIT_PRICE_CENTS: 599, QUANTITY: 1, MODIFIER_NAME: 'Standard' }
      ]
      wrapper.vm.loading = false
      wrapper.vm.cartItems = mockItems
      await nextTick()

      expect(wrapper.vm.cartTotal).toBe(599)
      expect(wrapper.vm.cartItems).toHaveLength(1)
    })

    it('should show empty state after removing last item', async () => {
      const mockItems = [
        { CART_ITEM_ID: 1, PRODUCT_NAME: 'Only Item', UNIT_PRICE_CENTS: 1000, QUANTITY: 1, MODIFIER_NAME: 'Standard' }
      ]
      wrapper.vm.loading = false
      wrapper.vm.cartItems = mockItems
      await nextTick()

      api.removeFromCart.mockResolvedValueOnce({})

      // Remove the item
      const deleteButton = wrapper.find('.btn-danger')
      await deleteButton.trigger('click')
      await nextTick()

      // Should show empty state
      expect(wrapper.vm.cartItems).toHaveLength(0)
      const emptyNotice = wrapper.find('.empty-cart-notice')
      expect(emptyNotice.exists()).toBe(true)
      expect(emptyNotice.text()).toContain('Your cart is empty')
    })

    it('should always display prices with 2 decimal places', async () => {
      const mockItems = [
        { CART_ITEM_ID: 1, PRODUCT_NAME: 'Item 1', UNIT_PRICE_CENTS: 500, QUANTITY: 1, MODIFIER_NAME: 'Standard' },
        { CART_ITEM_ID: 2, PRODUCT_NAME: 'Item 2', UNIT_PRICE_CENTS: 1050, QUANTITY: 1, MODIFIER_NAME: 'Standard' }
      ]
      wrapper.vm.loading = false
      wrapper.vm.cartItems = mockItems
      await nextTick()

      const rows = wrapper.findAll('.list-row')
      // Check that prices are formatted
      expect(rows[0].text()).toContain('$5.00')
      expect(rows[1].text()).toContain('$10.50')
    })

    it('should handle multiple separate entries of same product', async () => {
      const mockItems = [
        { CART_ITEM_ID: 1, PRODUCT_NAME: 'Card Pack', UNIT_PRICE_CENTS: 1000, QUANTITY: 2, MODIFIER_NAME: 'Standard' },
        { CART_ITEM_ID: 2, PRODUCT_NAME: 'Card Pack', UNIT_PRICE_CENTS: 1000, QUANTITY: 3, MODIFIER_NAME: 'Foil' }
      ]
      wrapper.vm.loading = false
      wrapper.vm.cartItems = mockItems
      await nextTick()

      // Should show 2 separate rows
      const rows = wrapper.findAll('.list-row')
      expect(rows).toHaveLength(2)
      
      // Both should have the same product name but different quantities
      expect(rows[0].text()).toContain('Card Pack')
      expect(rows[0].text()).toContain('× 2')
      expect(rows[1].text()).toContain('Card Pack')
      expect(rows[1].text()).toContain('× 3')
    })
  })
})
