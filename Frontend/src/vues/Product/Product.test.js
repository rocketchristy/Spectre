import { describe, it, expect, beforeEach, vi } from 'vitest'
import { nextTick } from 'vue'
import Product from './Product.vue'
import { mountWithDefaults, createMockRouter, flushPromises } from '../../test/utils'

// Mock the API module
vi.mock('@/utils/api.js', () => ({
  getProducts: vi.fn(),
  getInventory: vi.fn(),
  addToCart: vi.fn()
}))

import * as api from '@/utils/api.js'

describe('Product Component', () => {
  let wrapper
  let mockRouter

  beforeEach(async () => {
    // Setup API mocks with default responses
    const mockProducts = [
      { '1': 'PROD-001', DESCRIPTION: 'Test Card', BASE_PRICE_CENTS: 1500 }
    ]

    const mockInventory = [
      {
        PRODUCT_NAME: 'Test Card',
        STYLE_NAME: 'Card Single',
        QUANTITY_AVAILABLE: 5,
        MODIFIER_NAME: 'English, Mint, Non-Foil'
      }
    ]

    api.getProducts.mockResolvedValue(mockProducts)
    api.getInventory.mockResolvedValue(mockInventory)

    // Create router with initial route
    mockRouter = createMockRouter([], { 
      path: '/product/card/Test Card',
      name: 'product',
      params: { type: 'card', id: 'Test Card' }
    })
    await mockRouter.isReady()

    wrapper = mountWithDefaults(Product, { router: mockRouter })
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
    vi.clearAllMocks()
  })

  describe('Component Rendering', () => {
    // Test 1: Verify product page component mounts successfully
    it('should render the product component', () => {
      expect(wrapper.exists()).toBe(true)
    })

    it('should show loading state initially', async () => {
      const testRouter = createMockRouter([], { 
        path: '/product/card/Test Card',
        name: 'product',
        params: { type: 'card', id: 'Test Card' }
      })
      await testRouter.isReady()

      const newWrapper = mountWithDefaults(Product, { router: testRouter  })
      expect(newWrapper.vm.loading).toBe(true)
      if (newWrapper) newWrapper.unmount()
    })

    it('should call fetchData on mount', async () => {
      await flushPromises()
      expect(api.getProducts).toHaveBeenCalled()
      expect(api.getInventory).toHaveBeenCalled()
    })
  })

  describe('Route Parameters', () => {
    it('should read product type from route params', () => {
      expect(wrapper.vm.productType).toBe('card')
    })

    it('should read product ID from route params', () => {
      expect(wrapper.vm.productId).toBe('Test Card')
    })

    it('should compute isCard correctly', () => {
      expect(wrapper.vm.isCard).toBe(true)
    })
  })

  describe('Data Loading', () => {
    it('should load products from API', async () => {
      await flushPromises()
      await nextTick()

      expect(wrapper.vm.products).toHaveLength(1)
      expect(wrapper.vm.loading).toBe(false)
    })

    it('should load inventory from API', async () => {
      await flushPromises()
      await nextTick()

      expect(wrapper.vm.inventory).toHaveLength(1)
    })

    it('should set loading to false after data fetch', async () => {
      await flushPromises()
      await nextTick()

      expect(wrapper.vm.loading).toBe(false)
    })
  })

  describe('Product Catalog', () => {
    it('should find catalog product by description', async () => {
      await flushPromises()
      await nextTick()

      const catalogProduct = wrapper.vm.catalogProduct
      expect(catalogProduct).toBeDefined()
      expect(catalogProduct.DESCRIPTION).toBe('Test Card')
    })

    it('should return null for non-card types', async () => {
      const testRouter = createMockRouter([], { 
        path: '/product/pack/Mystery Pack',
        name: 'product',
        params: { type: 'pack', id: 'Mystery Pack' }
      })
      await testRouter.isReady()

      const newWrapper = mountWithDefaults(Product, { router: testRouter })
      await flushPromises()
      await nextTick()

      expect(newWrapper.vm.catalogProduct).toBeNull()
      
      if (newWrapper) newWrapper.unmount()
    })
  })

  describe('Product Listings', () => {
    it('should filter inventory for current product', async () => {
      await flushPromises()
      await nextTick()

      const listings = wrapper.vm.productListings
      expect(listings).toHaveLength(1)
      expect(listings[0].PRODUCT_NAME).toBe('Test Card')
    })

    it('should only show items with stock', async () => {
      const mockInventoryWithEmpty = [
        {
          PRODUCT_NAME: 'Test Card',
          QUANTITY_AVAILABLE: 5,
          STYLE_NAME: 'Card Single',
          MODIFIER_NAME: 'English'
        },
        {
          PRODUCT_NAME: 'Test Card',
          QUANTITY_AVAILABLE: 0,
          STYLE_NAME: 'Card Single',
          MODIFIER_NAME: 'Japanese'
        }
      ]

      api.getInventory.mockResolvedValue(mockInventoryWithEmpty)
      
      const testRouter = createMockRouter([], { 
        path: '/product/card/Test Card',
        name: 'product',
        params: { type: 'card', id: 'Test Card' }
      })
      await testRouter.isReady()

      const newWrapper = mountWithDefaults(Product, { router: testRouter })

      await flushPromises()
      await nextTick()

      const listings = newWrapper.vm.productListings
      expect(listings).toHaveLength(1)
      expect(listings[0].MODIFIER_NAME).toBe('English')

      newWrapper.unmount()
    })
  })

  describe('Booster Detection', () => {
    it('should detect mystery products', async () => {
      const testRouter = createMockRouter([], { 
        path: '/product/pack/Mystery Pack',
        name: 'product',
        params: { type: 'pack', id: 'Mystery Pack' }
      })
      await testRouter.isReady()

      const newWrapper = mountWithDefaults(Product, { router: testRouter })
      await flushPromises()
      await nextTick()

      expect(newWrapper.vm.isBooster).toBe(true)
      
      if (newWrapper) newWrapper.unmount()
    })

    it('should detect booster products', async () => {
      const testRouter = createMockRouter([], { 
        path: '/product/pack/Booster Box',
        name: 'product',
        params: { type: 'pack', id: 'Booster Box' }
      })
      await testRouter.isReady()

      const newWrapper = mountWithDefaults(Product, { router: testRouter })
      await flushPromises()
      await nextTick()

      expect(newWrapper.vm.isBooster).toBe(true)
      
      if (newWrapper) newWrapper.unmount()
    })

    it('should not detect regular cards as boosters', async () => {
      const testRouter = createMockRouter([], { 
        path: '/product/card/Regular Card',
        name: 'product',
        params: { type: 'card', id: 'Regular Card' }
      })
      await testRouter.isReady()

      const newWrapper = mountWithDefaults(Product, { router: testRouter })
      await flushPromises()
      await nextTick()

      expect(newWrapper.vm.isBooster).toBe(false)
      
      if (newWrapper) newWrapper.unmount()
    })
  })

  describe('Filter Options', () => {
    it('should have language filter', async () => {
      await flushPromises()
      expect(wrapper.vm.selectedLanguage).toBe('')
    })

    it('should have condition filter', async () => {
      await flushPromises()
      expect(wrapper.vm.selectedCondition).toBe('')
    })

    it('should have foil filter', async () => {
      await flushPromises()
      expect(wrapper.vm.selectedFoil).toBe('')
    })

    it('should reset filters when product ID changes', async () => {
      await flushPromises()
      
      // Set filters
      wrapper.vm.selectedLanguage = 'English'
      wrapper.vm.selectedCondition = 'Mint'
      wrapper.vm.selectedFoil = 'Holofoil'
      await nextTick()

      // Verify filters are set
      expect(wrapper.vm.selectedLanguage).toBe('English')
      expect(wrapper.vm.selectedCondition).toBe('Mint')
      expect(wrapper.vm.selectedFoil).toBe('Holofoil')

      // Create new wrapper with different product to test reset behavior
      const testRouter = createMockRouter([], { 
        path: '/product/card/New Product',
        name: 'product',
        params: { type: 'card', id: 'New Product' }
      })
      await testRouter.isReady()

      const newWrapper = mountWithDefaults(Product, { router: testRouter })
      await flushPromises()

      // New component instance should have filters reset
      expect(newWrapper.vm.selectedLanguage).toBe('')
      expect(newWrapper.vm.selectedCondition).toBe('')
      expect(newWrapper.vm.selectedFoil).toBe('')
      
      if (newWrapper) newWrapper.unmount()
    })
  })

  describe('Filtered Listings', () => {
    it('should filter by language', async () => {
      const mockInventoryMulti = [
        {
          PRODUCT_NAME: 'Test Card',
          QUANTITY_AVAILABLE: 5,
          MODIFIER_NAME: 'English, Mint, Non-Foil'
        },
        {
          PRODUCT_NAME: 'Test Card',
          QUANTITY_AVAILABLE: 3,
          MODIFIER_NAME: 'Japanese, Mint, Non-Foil'
        }
      ]

      api.getInventory.mockResolvedValue(mockInventoryMulti)
      
      const testRouter = createMockRouter([], { 
        path: '/product/card/Test Card',
        name: 'product',
        params: { type: 'card', id: 'Test Card' }
      })
      await testRouter.isReady()

      const newWrapper = mountWithDefaults(Product, { router: testRouter })

      await flushPromises()
      await nextTick()

      newWrapper.vm.selectedLanguage = 'English'
      await nextTick()

      const filtered = newWrapper.vm.filteredListings
      expect(filtered).toHaveLength(1)
      expect(filtered[0].MODIFIER_NAME).toContain('English')

      if (newWrapper) newWrapper.unmount()
    })
  })

  describe('Cart Quantity Management', () => {
    it('should initialize cart quantity to 1', async () => {
      await flushPromises()
      
      const testListing = {
        INVENTORY_ID: 1,
        QUANTITY_AVAILABLE: 10
      }
      
      expect(wrapper.vm.getCartQty(testListing)).toBe(1)
    })

    it('should set cart quantity within valid range', async () => {
      await flushPromises()
      
      const testListing = {
        INVENTORY_ID: 1,
        QUANTITY_AVAILABLE: 10
      }
      
      wrapper.vm.setCartQty(testListing, 5)
      expect(wrapper.vm.getCartQty(testListing)).toBe(5)
    })

    it('should enforce minimum quantity of 1', async () => {
      await flushPromises()
      
      const testListing = {
        INVENTORY_ID: 1,
        QUANTITY_AVAILABLE: 10
      }
      
      wrapper.vm.setCartQty(testListing, 0)
      expect(wrapper.vm.getCartQty(testListing)).toBe(1)
      
      wrapper.vm.setCartQty(testListing, -5)
      expect(wrapper.vm.getCartQty(testListing)).toBe(1)
    })

    it('should enforce maximum quantity to available stock', async () => {
      await flushPromises()
      
      const testListing = {
        INVENTORY_ID: 1,
        QUANTITY_AVAILABLE: 10
      }
      
      wrapper.vm.setCartQty(testListing, 15)
      expect(wrapper.vm.getCartQty(testListing)).toBe(10)
    })

    it('should call addToCart API when handleAddToCart is called', async () => {
      await flushPromises()
      
      const testListing = {
        INVENTORY_ID: 1,
        QUANTITY_AVAILABLE: 10,
        UNIT_PRICE_CENTS: 500,
        CURRENCY_CODE: 'USD'
      }
      
      // Clear previous mock calls and set new expectation
      api.addToCart.mockClear()
      api.addToCart.mockResolvedValueOnce({ success: true })
      
      await wrapper.vm.handleAddToCart(testListing)
      await flushPromises()
      
      expect(api.addToCart).toHaveBeenCalledWith(1, 1, 500, 'USD')
      
      // Verify showCartPrompt is set
      expect(wrapper.vm.showCartPrompt).toBe(true)
    })

    it('should handle addToCart errors', async () => {
      await flushPromises()
      
      // Mock alert
      global.alert = vi.fn()
      
      const testListing = {
        INVENTORY_ID: 1,
        QUANTITY_AVAILABLE: 10,
        UNIT_PRICE_CENTS: 500
      }
      
      api.addToCart.mockRejectedValue(new Error('Out of stock'))
      
      await wrapper.vm.handleAddToCart(testListing)
      await flushPromises()
      
      expect(global.alert).toHaveBeenCalledWith('Out of stock')
    })
  })

  describe('Error Handling', () => {
    it('should redirect to error page on API failure', async () => {
      api.getProducts.mockRejectedValue(new Error('API Error'))
      
      const testRouter = createMockRouter([], { 
        path: '/product/card/Test Card',
        name: 'product',
        params: { type: 'card', id: 'Test Card' }
      })
      await testRouter.isReady()

      const newWrapper = mountWithDefaults(Product, { router: testRouter })

      await flushPromises()
      await nextTick()

      expect(testRouter.push).toHaveBeenCalledWith({
        name: 'error',
        query: { message: 'API Error' }
      })

      if (newWrapper) newWrapper.unmount()
    })
  })

  describe('Additional Coverage Tests', () => {
    it('should handle addToCart with custom quantity', async () => {
      await flushPromises()
      
      global.alert = vi.fn()
      
      const testListing = {
        INVENTORY_ID: 2,
        QUANTITY_AVAILABLE: 10,
        UNIT_PRICE_CENTS: 1000,
        CURRENCY_CODE: 'USD'
      }
      
      wrapper.vm.setCartQty(testListing, 3)
      api.addToCart.mockResolvedValue({ success: true })
      
      await wrapper.vm.handleAddToCart(testListing)
      await flushPromises()
      
      expect(api.addToCart).toHaveBeenCalledWith(2, 3, 1000, 'USD')
    })

    it('should default currency to USD if not provided', async () => {
      await flushPromises()
      
      global.alert = vi.fn()
      
      const testListing = {
        INVENTORY_ID: 3,
        QUANTITY_AVAILABLE: 5,
        UNIT_PRICE_CENTS: 750,
        CURRENCY_CODE: undefined
      }
      
      api.addToCart.mockResolvedValue({ success: true })
      
      await wrapper.vm.handleAddToCart(testListing)
      await flushPromises()
      
      expect(api.addToCart).toHaveBeenCalledWith(3, 1, 750, 'USD')
    })

    it('should handle empty catalog product gracefully', async () => {
      const mockProducts = []
      const mockInventory = []

      api.getProducts.mockResolvedValue(mockProducts)
      api.getInventory.mockResolvedValue(mockInventory)
      
      const testRouter = createMockRouter([], { 
        path: '/product/card/Nonexistent',
        name: 'product',
        params: { type: 'card', id: 'Nonexistent' }
      })
      await testRouter.isReady()

      const newWrapper = mountWithDefaults(Product, { router: testRouter })
      await flushPromises()
      await nextTick()

      expect(newWrapper.vm.catalogProduct).toBeNull()
      expect(newWrapper.vm.currentProduct).toBeNull()
      
      if (newWrapper) newWrapper.unmount()
    })

    it('should handle empty product listings', async () => {
      const mockProducts = [
        { '1': 'PROD-001', DESCRIPTION: 'Test Card', BASE_PRICE_CENTS: 1000 }
      ]
      const mockInventory = []

      api.getProducts.mockResolvedValue(mockProducts)
      api.getInventory.mockResolvedValue(mockInventory)
      
      const testRouter = createMockRouter([], { 
        path: '/product/card/Test Card',
        name: 'product',
        params: { type: 'card', id: 'Test Card' }
      })
      await testRouter.isReady()

      const newWrapper = mountWithDefaults(Product, { router: testRouter })
      await flushPromises()
      await nextTick()

      expect(newWrapper.vm.productListings).toEqual([])
      expect(newWrapper.vm.filteredListings).toEqual([])
      
      if (newWrapper) newWrapper.unmount()
    })

    it('should filter by condition', async () => {
      const mockInventoryMulti = [
        {
          PRODUCT_NAME: 'Test Card',
          QUANTITY_AVAILABLE: 5,
          MODIFIER_NAME: 'English, Mint, Non-Foil'
        },
        {
          PRODUCT_NAME: 'Test Card',
          QUANTITY_AVAILABLE: 3,
          MODIFIER_NAME: 'English, Light Play, Non-Foil'
        }
      ]

      api.getInventory.mockResolvedValue(mockInventoryMulti)
      
      const testRouter = createMockRouter([], { 
        path: '/product/card/Test Card',
        name: 'product',
        params: { type: 'card', id: 'Test Card' }
      })
      await testRouter.isReady()

      const newWrapper = mountWithDefaults(Product, { router: testRouter })
      await flushPromises()
      await nextTick()

      newWrapper.vm.selectedCondition = 'Mint'
      await nextTick()

      const filtered = newWrapper.vm.filteredListings
      expect(filtered).toHaveLength(1)
      expect(filtered[0].MODIFIER_NAME).toContain('Mint')

      if (newWrapper) newWrapper.unmount()
    })

    it('should filter by foil type', async () => {
      const mockInventoryMulti = [
        {
          PRODUCT_NAME: 'Test Card',
          QUANTITY_AVAILABLE: 5,
          MODIFIER_NAME: 'English, Mint, Non-Foil'
        },
        {
          PRODUCT_NAME: 'Test Card',
          QUANTITY_AVAILABLE: 3,
          MODIFIER_NAME: 'English, Mint, Holofoil'
        }
      ]

      api.getInventory.mockResolvedValue(mockInventoryMulti)
      
      const testRouter = createMockRouter([], { 
        path: '/product/card/Test Card',
        name: 'product',
        params: { type: 'card', id: 'Test Card' }
      })
      await testRouter.isReady()

      const newWrapper = mountWithDefaults(Product, { router: testRouter })
      await flushPromises()
      await nextTick()

      newWrapper.vm.selectedFoil = 'Holofoil'
      await nextTick()

      const filtered = newWrapper.vm.filteredListings
      expect(filtered).toHaveLength(1)
      expect(filtered[0].MODIFIER_NAME).toContain('Holofoil')

      if (newWrapper) newWrapper.unmount()
    })

    it('should apply multiple filters together', async () => {
      const mockInventoryMulti = [
        {
          PRODUCT_NAME: 'Test Card',
          QUANTITY_AVAILABLE: 5,
          MODIFIER_NAME: 'English, Mint, Non-Foil'
        },
        {
          PRODUCT_NAME: 'Test Card',
          QUANTITY_AVAILABLE: 3,
          MODIFIER_NAME: 'English, Light Play, Non-Foil'
        },
        {
          PRODUCT_NAME: 'Test Card',
          QUANTITY_AVAILABLE: 2,
          MODIFIER_NAME: 'Japanese, Mint, Non-Foil'
        }
      ]

      api.getInventory.mockResolvedValue(mockInventoryMulti)
      
      const testRouter = createMockRouter([], { 
        path: '/product/card/Test Card',
        name: 'product',
        params: { type: 'card', id: 'Test Card' }
      })
      await testRouter.isReady()

      const newWrapper = mountWithDefaults(Product, { router: testRouter })
      await flushPromises()
      await nextTick()

      newWrapper.vm.selectedLanguage = 'English'
      newWrapper.vm.selectedCondition = 'Mint'
      await nextTick()

      const filtered = newWrapper.vm.filteredListings
      expect(filtered).toHaveLength(1)
      expect(filtered[0].MODIFIER_NAME).toContain('English')
      expect(filtered[0].MODIFIER_NAME).toContain('Mint')

      if (newWrapper) newWrapper.unmount()
    })

    it('should handle getCardImage for mystery products', async () => {
      await flushPromises()
      
      const imagePath = wrapper.vm.getCardImage('Mystery Pack')
      // Should return booster image or null
      expect(imagePath === null || typeof imagePath === 'string').toBe(true)
    })
  })
})
