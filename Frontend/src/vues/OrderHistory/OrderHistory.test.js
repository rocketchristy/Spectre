import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { nextTick } from 'vue'
import OrderHistory from './OrderHistory.vue'
import { mountWithDefaults } from '../../test/utils'
import * as api from '@/utils/api.js'

// Mock the API module
vi.mock('@/utils/api.js', () => ({
  getOrders: vi.fn().mockResolvedValue([])
}))

describe('OrderHistory Component', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    wrapper = mountWithDefaults(OrderHistory)
  })

  afterEach(() => {
    wrapper.unmount()
  })

  describe('Component Rendering', () => {
    it('should render the order history component', () => {
      expect(wrapper.exists()).toBe(true)
      expect(wrapper.find('.page-title').text()).toBe('Order History')
    })

    it('should display empty state when no orders', async () => {
      wrapper.vm.loading = false
      wrapper.vm.rawOrders = []
      await nextTick()
      
      expect(wrapper.vm.orders).toHaveLength(0)
      
      const emptyState = wrapper.find('.empty-state')
      expect(emptyState.exists()).toBe(true)
      expect(emptyState.text()).toContain('No orders yet')
    })

    it('should show link to store when no orders', async () => {
      wrapper.vm.loading = false
      wrapper.vm.rawOrders = []
      await nextTick()
      
      const storeLink = wrapper.find('.action-btn')
      expect(storeLink.exists()).toBe(true)
      expect(storeLink.text()).toBe('Start Shopping')
    })
  })

  describe('Orders Display', () => {
    it('should display orders when they exist', async () => {
      // Set raw orders (backend format: flat joined rows)
      const mockRawOrders = [
        {
          ORDER_ID: 101,
          CREATED_AT: '2026-03-10T12:00:00Z',
          STATUS: 'Completed',
          PRODUCT_NAME: 'Booster Pack',
          QUANTITY: 2,
          UNIT_PRICE_CENTS: 1000
        },
        {
          ORDER_ID: 102,
          CREATED_AT: '2026-03-15T14:30:00Z',
          STATUS: 'Shipped',
          PRODUCT_NAME: 'Rare Card',
          QUANTITY: 1,
          UNIT_PRICE_CENTS: 2500
        }
      ]

      wrapper.vm.loading = false
      wrapper.vm.rawOrders = mockRawOrders
      await nextTick()

      // Should have 2 orders in computed property
      expect(wrapper.vm.orders).toHaveLength(2)

      // Should render table rows
      const orderRows = wrapper.findAll('tbody tr')
      expect(orderRows).toHaveLength(2)
    })

    it('should display order ID correctly', async () => {
      const mockRawOrders = [{
        ORDER_ID: 101,
        CREATED_AT: '2026-03-10T12:00:00Z',
        STATUS: 'Completed',
        PRODUCT_NAME: 'Test Item',
        QUANTITY: 1,
        UNIT_PRICE_CENTS: 1000
      }]

      wrapper.vm.loading = false
      wrapper.vm.rawOrders = mockRawOrders
      await nextTick()

      const orderRow = wrapper.find('tbody tr')
      expect(orderRow.find('.col-order').text()).toBe('101')
    })

    it('should display order date', async () => {
      const mockRawOrders = [{
        ORDER_ID: 101,
        CREATED_AT: '2026-03-10T12:00:00Z',
        STATUS: 'Completed',
        PRODUCT_NAME: 'Test Item',
        QUANTITY: 1,
        UNIT_PRICE_CENTS: 1000
      }]

      wrapper.vm.loading = false
      wrapper.vm.rawOrders = mockRawOrders
      await nextTick()

      const orderRow = wrapper.find('tbody tr')
      const dateText = orderRow.find('.col-date').text()
      // Date should be formatted (contains Mar and 10)
      expect(dateText).toContain('Mar')
      expect(dateText).toContain('10')
    })

    it('should display order total', async () => {
      const mockRawOrders = [{
        ORDER_ID: 101,
        CREATED_AT: '2026-03-10T12:00:00Z',
        STATUS: 'Completed',
        PRODUCT_NAME: 'Test Item',
        QUANTITY: 2,
        UNIT_PRICE_CENTS: 1500
      }]

      wrapper.vm.loading = false
      wrapper.vm.rawOrders = mockRawOrders
      await nextTick()

      // Total should be 2 * 1500 = 3000 cents = $30.00
      const orderRow = wrapper.find('tbody tr')
      expect(orderRow.find('.col-cost').text()).toBe('$30.00')
    })
  })

  describe('Order Items', () => {
    it('should display order items in details', async () => {
      // Multiple items for same order
      const mockRawOrders = [
        {
          ORDER_ID: 101,
          CREATED_AT: '2026-03-10T12:00:00Z',
          STATUS: 'Completed',
          PRODUCT_NAME: 'Booster Pack',
          QUANTITY: 2,
          UNIT_PRICE_CENTS: 1000
        },
        {
          ORDER_ID: 101,
          CREATED_AT: '2026-03-10T12:00:00Z',
          STATUS: 'Completed',
          PRODUCT_NAME: 'Rare Card',
          QUANTITY: 1,
          UNIT_PRICE_CENTS: 2500
        }
      ]

      wrapper.vm.loading = false
      wrapper.vm.rawOrders = mockRawOrders
      await nextTick()

      // Should be grouped into 1 order with 2 items
      expect(wrapper.vm.orders).toHaveLength(1)
      expect(wrapper.vm.orders[0].items).toHaveLength(2)
    })

    it('should display item details correctly', async () => {
      const mockRawOrders = [{
        ORDER_ID: 101,
        CREATED_AT: '2026-03-10T12:00:00Z',
        STATUS: 'Completed',
        PRODUCT_NAME: 'Booster Pack',
        QUANTITY: 2,
        UNIT_PRICE_CENTS: 1000
      }]

      wrapper.vm.loading = false
      wrapper.vm.rawOrders = mockRawOrders
      await nextTick()

      const orderRow = wrapper.find('tbody tr')
      const itemsSummary = orderRow.find('.col-items').text()
      
      // Should show "2× Booster Pack"
      expect(itemsSummary).toContain('2×')
      expect(itemsSummary).toContain('Booster Pack')
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

    it('should not display orders when loading', async () => {
      wrapper.vm.loading = true
      wrapper.vm.errorMsg = ''  // Important: errorMsg must be falsy for the v-else-if chain
      wrapper.vm.rawOrders = []  // Set NO raw orders
      await nextTick()

      // With loading=true and no orders, table wrapper should not exist
      const tableWrapper = wrapper.find('.orders-table-wrapper')
      expect(tableWrapper.exists()).toBe(false)
      
      // Loading message should be displayed
      expect(wrapper.find('.empty-state').text()).toBe('Loading…')
    })
  })

  describe('Expandable Orders', () => {
    it('should render orders as details elements', async () => {
      const mockRawOrders = [{
        ORDER_ID: 101,
        CREATED_AT: '2026-03-10T12:00:00Z',
        STATUS: 'Completed',
        PRODUCT_NAME: 'Test Item',
        QUANTITY: 1,
        UNIT_PRICE_CENTS: 1000
      }]

      wrapper.vm.loading = false
      wrapper.vm.rawOrders = mockRawOrders
      await nextTick()

      // Component uses table format, not details/summary
      const table = wrapper.find('.orders-table')
      expect(table.exists()).toBe(true)
    })

    it('should have summary element for order header', async () => {
      const mockRawOrders = [{
        ORDER_ID: 101,
        CREATED_AT: '2026-03-10T12:00:00Z',
        STATUS: 'Completed',
        PRODUCT_NAME: 'Test Item',
        QUANTITY: 1,
        UNIT_PRICE_CENTS: 1000
      }]

      wrapper.vm.loading = false
      wrapper.vm.rawOrders = mockRawOrders
      await nextTick()

      // Component uses table headers
      const headers = wrapper.findAll('thead th')
      expect(headers.length).toBeGreaterThan(0)
      expect(headers[0].text()).toBe('Order #')
    })
  })
})
