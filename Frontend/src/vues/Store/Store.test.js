import { describe, it, expect, beforeEach, vi } from 'vitest'
import { nextTick } from 'vue'
import Store from './Store.vue'
import { mountWithDefaults, createMockRouter, flushPromises, createMockProducts } from '../../test/utils'

// Mock the API module
vi.mock('../../utils/api.js', () => ({
  getProducts: vi.fn(),
  getInventory: vi.fn(),
  addInventoryItem: vi.fn()
}))

import * as api from '../../utils/api.js'

describe('Store Component', () => {
  let wrapper
  let mockRouter

  beforeEach(() => {
    // Setup API mocks with default responses
    const mockProducts = [
      { '1': 'PROD-001', DESCRIPTION: 'Test Card', BASE_PRICE_CENTS: 1500 },
      { '1': 'PROD-002', DESCRIPTION: 'Mystery Pack', BASE_PRICE_CENTS: 2000 }
    ]

    const mockInventory = [
      {
        PRODUCT_NAME: 'Test Card',
        STYLE_NAME: 'Card Single',
        QUANTITY_AVAILABLE: 5,
        MODIFIER_NAME: 'English, Mint, Non-Foil'
      },
      {
        PRODUCT_NAME: 'Mystery Pack',
        STYLE_NAME: 'Mystery Pack',
        QUANTITY_AVAILABLE: 10,
        MODIFIER_NAME: ''
      }
    ]

    api.getProducts.mockResolvedValue(mockProducts)
    api.getInventory.mockResolvedValue(mockInventory)

    wrapper = mountWithDefaults(Store)
  })

  afterEach(() => {
    wrapper.unmount()
    vi.clearAllMocks()
  })

  describe('Component Rendering', () => {
    // Test 1: Verify store component mounts successfully
    it('should render the store component', () => {
      expect(wrapper.exists()).toBe(true)
    })

    // Test 2: Verify loading state is true when component first mounts
    it('should show loading state initially', () => {
      const newWrapper = mountWithDefaults(Store)
      expect(newWrapper.vm.loading).toBe(true)
      newWrapper.unmount()
    })

    // Test 3: Verify getProducts API is called to fetch catalog on mount
    it('should call getProducts on mount', async () => {
      await flushPromises()
      expect(api.getProducts).toHaveBeenCalled()
    })

    // Test 4: Verify getInventory API is called to fetch stock data on mount
    it('should call getInventory on mount', async () => {
      await flushPromises()
      expect(api.getInventory).toHaveBeenCalled()
    })
  })

  describe('Data Loading', () => {
    it('should load products from API', async () => {
      await flushPromises()
      await nextTick()

      expect(wrapper.vm.products).toHaveLength(2)
      expect(wrapper.vm.loading).toBe(false)
    })

    it('should load inventory from API', async () => {
      await flushPromises()
      await nextTick()

      expect(wrapper.vm.inventory).toHaveLength(2)
    })

    it('should set loading to false after data fetch', async () => {
      await flushPromises()
      await nextTick()

      expect(wrapper.vm.loading).toBe(false)
    })
  })

  describe('Product Cards Computed', () => {
    it('should transform products into card format', async () => {
      await flushPromises()
      await nextTick()

      const cards = wrapper.vm.productCards
      expect(cards).toHaveLength(2)
      expect(cards[0]).toHaveProperty('sku')
      expect(cards[0]).toHaveProperty('name')
      expect(cards[0]).toHaveProperty('price')
      expect(cards[0]).toHaveProperty('image')
    })

    it('should convert price from cents to dollars', async () => {
      await flushPromises()
      await nextTick()

      const cards = wrapper.vm.productCards
      expect(cards[0].price).toBe('15.00')
      expect(cards[1].price).toBe('20.00')
    })
  })

  describe('Inventory Cards Computed', () => {
    it('should filter out items with no stock', async () => {
      const mockInventoryWithEmpty = [
        {
          PRODUCT_NAME: 'In Stock',
          QUANTITY_AVAILABLE: 5,
          STYLE_NAME: 'Card Single'
        },
        {
          PRODUCT_NAME: 'Out of Stock',
          QUANTITY_AVAILABLE: 0,
          STYLE_NAME: 'Card Single'
        }
      ]

      api.getInventory.mockResolvedValue(mockInventoryWithEmpty)
      const newWrapper = mountWithDefaults(Store)
      
      await flushPromises()
      await nextTick()

      const inventoryCards = newWrapper.vm.inventoryCards
      expect(inventoryCards).toHaveLength(1)
      expect(inventoryCards[0].PRODUCT_NAME).toBe('In Stock')
      
      newWrapper.unmount()
    })
  })

  describe('Card Image Helper', () => {
    it('should have getCardImage function', async () => {
      await flushPromises()
      expect(typeof wrapper.vm.getCardImage).toBe('function')
    })

    it('should handle booster description', async () => {
      await flushPromises()
      const image = wrapper.vm.getCardImage('Booster Pack')
      // Should return some image or null
      expect(image === null || typeof image === 'string').toBe(true)
    })

    it('should handle mystery description', async () => {
      await flushPromises()
      const image = wrapper.vm.getCardImage('Mystery Box')
      expect(image === null || typeof image === 'string').toBe(true)
    })
  })

  describe('Error Handling', () => {
    it('should redirect to error page on API failure', async () => {
      api.getProducts.mockRejectedValue(new Error('API Error'))
      
      const testRouter = createMockRouter()
      const newWrapper = mountWithDefaults(Store, { router: testRouter })

      await flushPromises()
      await nextTick()

      expect(testRouter.push).toHaveBeenCalledWith({
        name: 'error',
        query: { message: 'API Error' }
      })

      newWrapper.unmount()
    })
  })

  describe('Helper Functions', () => {
    it('should have isSpecificCard function', async () => {
      await flushPromises()
      expect(typeof wrapper.vm.isSpecificCard).toBe('function')
    })

    it('should correctly identify specific cards', async () => {
      await flushPromises()
      
      const specificCard = {
        STYLE_NAME: 'Card Single',
        PRODUCT_NAME: 'Test Card'
      }
      
      const mysteryPack = {
        STYLE_NAME: 'Mystery Pack',
        PRODUCT_NAME: 'Mystery Single'
      }

      expect(wrapper.vm.isSpecificCard(specificCard)).toBe(true)
      expect(wrapper.vm.isSpecificCard(mysteryPack)).toBe(false)
    })
  })

  describe('Style Groups Computed', () => {
    it('should group inventory by STYLE_NAME excluding Card Single', async () => {
      const mockInventoryWithStyles = [
        {
          PRODUCT_NAME: 'Card A',
          STYLE_NAME: 'Card Single',
          QUANTITY_AVAILABLE: 5,
          UNIT_PRICE_CENTS: 100
        },
        {
          PRODUCT_NAME: 'Mystery A',
          STYLE_NAME: 'Mystery Single',
          QUANTITY_AVAILABLE: 3,
          UNIT_PRICE_CENTS: 500
        },
        {
          PRODUCT_NAME: 'Mystery B',
          STYLE_NAME: 'Mystery Pack',
          QUANTITY_AVAILABLE: 2,
          UNIT_PRICE_CENTS: 1000
        }
      ]

      api.getInventory.mockResolvedValue(mockInventoryWithStyles)
      const newWrapper = mountWithDefaults(Store)
      
      await flushPromises()
      await nextTick()

      const groups = newWrapper.vm.styleGroups
      expect(groups.has('Card Single')).toBe(false)
      expect(groups.has('Mystery Single')).toBe(true)
      expect(groups.has('Mystery Pack')).toBe(true)
      
      newWrapper.unmount()
    })

    it('should sort styles in correct order', async () => {
      const mockInventoryWithStyles = [
        { PRODUCT_NAME: 'Pack', STYLE_NAME: 'Mystery Pack', QUANTITY_AVAILABLE: 1, UNIT_PRICE_CENTS: 100 },
        { PRODUCT_NAME: 'Single', STYLE_NAME: 'Mystery Single', QUANTITY_AVAILABLE: 1, UNIT_PRICE_CENTS: 100 },
        { PRODUCT_NAME: 'Midi', STYLE_NAME: 'Mystery Midi', QUANTITY_AVAILABLE: 1, UNIT_PRICE_CENTS: 100 }
      ]

      api.getInventory.mockResolvedValue(mockInventoryWithStyles)
      const newWrapper = mountWithDefaults(Store)
      
      await flushPromises()
      await nextTick()

      const keys = [...newWrapper.vm.styleGroups.keys()]
      expect(keys.indexOf('Mystery Single')).toBeLessThan(keys.indexOf('Mystery Midi'))
      expect(keys.indexOf('Mystery Midi')).toBeLessThan(keys.indexOf('Mystery Pack'))
      
      newWrapper.unmount()
    })
  })

  describe('Bargain Cards Computed', () => {
    it('should filter cards under $1', async () => {
      const mockInventoryWithPrices = [
        {
          PRODUCT_NAME: 'Cheap Card 1',
          STYLE_NAME: 'Card Single',
          QUANTITY_AVAILABLE: 5,
          UNIT_PRICE_CENTS: 50
        },
        {
          PRODUCT_NAME: 'Cheap Card 2',
          STYLE_NAME: 'Card Single',
          QUANTITY_AVAILABLE: 3,
          UNIT_PRICE_CENTS: 75
        },
        {
          PRODUCT_NAME: 'Expensive Card',
          STYLE_NAME: 'Card Single',
          QUANTITY_AVAILABLE: 2,
          UNIT_PRICE_CENTS: 1500
        }
      ]

      api.getInventory.mockResolvedValue(mockInventoryWithPrices)
      const newWrapper = mountWithDefaults(Store)
      
      await flushPromises()
      await nextTick()

      const bargains = newWrapper.vm.bargainCards
      expect(bargains.length).toBeLessThanOrEqual(2)
      expect(bargains.every(c => c.UNIT_PRICE_CENTS < 100)).toBe(true)
      
      newWrapper.unmount()
    })

    it('should sort bargain cards by price ascending', async () => {
      const mockInventoryWithPrices = [
        { PRODUCT_NAME: 'Card B', STYLE_NAME: 'Card Single', QUANTITY_AVAILABLE: 1, UNIT_PRICE_CENTS: 90 },
        { PRODUCT_NAME: 'Card A', STYLE_NAME: 'Card Single', QUANTITY_AVAILABLE: 1, UNIT_PRICE_CENTS: 50 },
        { PRODUCT_NAME: 'Card C', STYLE_NAME: 'Card Single', QUANTITY_AVAILABLE: 1, UNIT_PRICE_CENTS: 75 }
      ]

      api.getInventory.mockResolvedValue(mockInventoryWithPrices)
      const newWrapper = mountWithDefaults(Store)
      
      await flushPromises()
      await nextTick()

      const bargains = newWrapper.vm.bargainCards
      expect(bargains[0].UNIT_PRICE_CENTS).toBeLessThanOrEqual(bargains[bargains.length - 1].UNIT_PRICE_CENTS)
      
      newWrapper.unmount()
    })

    it('should limit bargain cards to 12 items', async () => {
      const mockManyBargains = Array.from({ length: 20 }, (_, i) => ({
        PRODUCT_NAME: `Card ${i}`,
        STYLE_NAME: 'Card Single',
        QUANTITY_AVAILABLE: 1,
        UNIT_PRICE_CENTS: 50 + i
      }))

      api.getInventory.mockResolvedValue(mockManyBargains)
      const newWrapper = mountWithDefaults(Store)
      
      await flushPromises()
      await nextTick()

      const bargains = newWrapper.vm.bargainCards
      expect(bargains.length).toBeLessThanOrEqual(12)
      
      newWrapper.unmount()
    })
  })

  describe('Rare Finds Computed', () => {
    it('should filter cards over $10', async () => {
      const mockInventoryWithPrices = [
        {
          PRODUCT_NAME: 'Rare Card 1',
          STYLE_NAME: 'Card Single',
          QUANTITY_AVAILABLE: 1,
          UNIT_PRICE_CENTS: 1500
        },
        {
          PRODUCT_NAME: 'Rare Card 2',
          STYLE_NAME: 'Card Single',
          QUANTITY_AVAILABLE: 1,
          UNIT_PRICE_CENTS: 2000
        },
        {
          PRODUCT_NAME: 'Cheap Card',
          STYLE_NAME: 'Card Single',
          QUANTITY_AVAILABLE: 5,
          UNIT_PRICE_CENTS: 50
        }
      ]

      api.getInventory.mockResolvedValue(mockInventoryWithPrices)
      const newWrapper = mountWithDefaults(Store)
      
      await flushPromises()
      await nextTick()

      const rareFinds = newWrapper.vm.rareFinds
      expect(rareFinds.length).toBeGreaterThan(0)
      expect(rareFinds.every(c => c.UNIT_PRICE_CENTS > 1000)).toBe(true)
      
      newWrapper.unmount()
    })

    it('should sort rare finds by price descending', async () => {
      const mockInventoryWithPrices = [
        { PRODUCT_NAME: 'Card A', STYLE_NAME: 'Card Single', QUANTITY_AVAILABLE: 1, UNIT_PRICE_CENTS: 1500 },
        { PRODUCT_NAME: 'Card B', STYLE_NAME: 'Card Single', QUANTITY_AVAILABLE: 1, UNIT_PRICE_CENTS: 3000 },
        { PRODUCT_NAME: 'Card C', STYLE_NAME: 'Card Single', QUANTITY_AVAILABLE: 1, UNIT_PRICE_CENTS: 2000 }
      ]

      api.getInventory.mockResolvedValue(mockInventoryWithPrices)
      const newWrapper = mountWithDefaults(Store)
      
      await flushPromises()
      await nextTick()

      const rareFinds = newWrapper.vm.rareFinds
      expect(rareFinds[0].UNIT_PRICE_CENTS).toBeGreaterThanOrEqual(rareFinds[rareFinds.length - 1].UNIT_PRICE_CENTS)
      
      newWrapper.unmount()
    })

    it('should limit rare finds to 12 items', async () => {
      const mockManyRares = Array.from({ length: 20 }, (_, i) => ({
        PRODUCT_NAME: `Rare Card ${i}`,
        STYLE_NAME: 'Card Single',
        QUANTITY_AVAILABLE: 1,
        UNIT_PRICE_CENTS: 1100 + (i * 100)
      }))

      api.getInventory.mockResolvedValue(mockManyRares)
      const newWrapper = mountWithDefaults(Store)
      
      await flushPromises()
      await nextTick()

      const rareFinds = newWrapper.vm.rareFinds
      expect(rareFinds.length).toBeLessThanOrEqual(12)
      
      newWrapper.unmount()
    })
  })

  describe('Search Functionality', () => {
    it('should return empty results when search query is empty', async () => {
      await flushPromises()
      await nextTick()

      wrapper.vm.searchQuery = ''
      await nextTick()

      expect(wrapper.vm.searchResults).toEqual([])
    })

    it('should search products by name', async () => {
      const mockProducts = [
        { '1': 'PROD-001', DESCRIPTION: 'Test Card Alpha', BASE_PRICE_CENTS: 1000 },
        { '1': 'PROD-002', DESCRIPTION: 'Test Card Beta', BASE_PRICE_CENTS: 2000 },
        { '1': 'PROD-003', DESCRIPTION: 'Another Product', BASE_PRICE_CENTS: 1500 }
      ]

      api.getProducts.mockResolvedValue(mockProducts)
      const newWrapper = mountWithDefaults(Store)
      
      await flushPromises()
      await nextTick()

      newWrapper.vm.searchQuery = 'test card'
      await nextTick()

      const results = newWrapper.vm.searchResults
      expect(results.length).toBe(2)
      expect(results[0].name).toContain('Test Card')
      
      newWrapper.unmount()
    })

    it('should be case-insensitive when searching', async () => {
      const mockProducts = [
        { '1': 'PROD-001', DESCRIPTION: 'TEST CARD', BASE_PRICE_CENTS: 1000 }
      ]

      api.getProducts.mockResolvedValue(mockProducts)
      const newWrapper = mountWithDefaults(Store)
      
      await flushPromises()
      await nextTick()

      newWrapper.vm.searchQuery = 'test card'
      await nextTick()

      expect(newWrapper.vm.searchResults.length).toBe(1)
      
      newWrapper.unmount()
    })

    it('should limit search results to 12 items', async () => {
      const mockManyProducts = Array.from({ length: 20 }, (_, i) => ({
        '1': `PROD-00${i}`,
        DESCRIPTION: `Item ${i}`,
        BASE_PRICE_CENTS: 1000
      }))

      api.getProducts.mockResolvedValue(mockManyProducts)
      const newWrapper = mountWithDefaults(Store)
      
      await flushPromises()
      await nextTick()

      newWrapper.vm.searchQuery = 'item'
      await nextTick()

      expect(newWrapper.vm.searchResults.length).toBeLessThanOrEqual(12)
      
      newWrapper.unmount()
    })

    it('should clear search query', async () => {
      await flushPromises()
      
      wrapper.vm.searchQuery = 'test'
      await nextTick()
      
      wrapper.vm.clearSearch()
      await nextTick()
      
      expect(wrapper.vm.searchQuery).toBe('')
    })
  })

  describe('Sell Modal Functionality', () => {
    it('should open sell modal', async () => {
      await flushPromises()
      
      wrapper.vm.openSellModal()
      await nextTick()
      
      expect(wrapper.vm.showSellModal).toBe(true)
      expect(wrapper.vm.sellForm.productSku).toBe('')
    })

    it('should close sell modal', async () => {
      await flushPromises()
      
      wrapper.vm.showSellModal = true
      wrapper.vm.closeSellModal()
      await nextTick()
      
      expect(wrapper.vm.showSellModal).toBe(false)
    })

    it('should build modifier code from dropdowns', async () => {
      await flushPromises()
      
      wrapper.vm.sellForm.language = 'EN'
      wrapper.vm.sellForm.foil = 'NF'
      wrapper.vm.sellForm.condition = 'MT'
      await nextTick()
      
      expect(wrapper.vm.sellModifierCode).toBe('ENNFMT')
    })

    it('should build full SKU from base and modifier', async () => {
      await flushPromises()
      
      wrapper.vm.sellForm.productSku = 'BASESKU123'
      wrapper.vm.sellForm.language = 'EN'
      wrapper.vm.sellForm.foil = 'NF'
      wrapper.vm.sellForm.condition = 'MT'
      await nextTick()
      
      expect(wrapper.vm.sellFullSku).toBe('BASESKU123ENNFMT')
    })

    it('should return empty SKU when productSku is not set', async () => {
      await flushPromises()
      
      wrapper.vm.sellForm.productSku = ''
      await nextTick()
      
      expect(wrapper.vm.sellFullSku).toBe('')
    })

    it('should validate required fields in submitSell', async () => {
      await flushPromises()
      
      await wrapper.vm.submitSell()
      await nextTick()
      
      expect(wrapper.vm.sellError).toBeTruthy()
    })

    it('should submit sell form successfully', async () => {
      await flushPromises()
      
      api.addInventoryItem.mockResolvedValue({ success: true })
      api.getInventory.mockResolvedValue([])
      
      wrapper.vm.sellForm = {
        productSku: 'BASESKU123',
        language: 'EN',
        condition: 'MT',
        foil: 'NF',
        quantity: 2,
        price: '19.99'
      }
      
      await wrapper.vm.submitSell()
      await flushPromises()
      
      expect(api.addInventoryItem).toHaveBeenCalled()
      expect(wrapper.vm.showSellModal).toBe(false)
    })

    it('should handle sell form errors', async () => {
      await flushPromises()
      
      api.addInventoryItem.mockRejectedValue(new Error('Failed to list'))
      
      wrapper.vm.sellForm = {
        productSku: 'BASESKU123',
        language: 'EN',
        condition: 'MT',
        foil: 'NF',
        quantity: 1,
        price: '9.99'
      }
      
      await wrapper.vm.submitSell()
      await flushPromises()
      
      expect(wrapper.vm.sellError).toBe('Failed to list')
    })
  })
})
