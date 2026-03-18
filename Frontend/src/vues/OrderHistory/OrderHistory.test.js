import { describe, it, expect, beforeEach } from 'vitest'
import { nextTick } from 'vue'
import OrderHistory from './OrderHistory.vue'
import { mountWithDefaults } from '../../test/utils'

describe('OrderHistory Component', () => {
  let wrapper

  beforeEach(() => {
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

    it('should display empty state when no orders', () => {
      expect(wrapper.vm.orders).toHaveLength(0)
      
      const emptyState = wrapper.find('.empty-state')
      expect(emptyState.exists()).toBe(true)
      expect(emptyState.text()).toContain('No orders yet')
    })

    it('should show link to store when no orders', () => {
      const storeLink = wrapper.find('.action-btn')
      expect(storeLink.exists()).toBe(true)
      expect(storeLink.text()).toBe('Start Shopping')
    })
  })

  describe('Orders Display', () => {
    it('should display orders when they exist', async () => {
      const mockOrders = [
        {
          id: 101,
          date: '2026-03-10',
          items: [
            { name: 'Booster Pack', qty: 2, price: 10 }
          ],
          total: 20
        },
        {
          id: 102,
          date: '2026-03-15',
          items: [
            { name: 'Rare Card', qty: 1, price: 25 }
          ],
          total: 25
        }
      ]

      wrapper.vm.orders = mockOrders
      await nextTick()

      const orderElements = wrapper.findAll('.list-row')
      expect(orderElements).toHaveLength(2)
    })

    it('should display order ID correctly', async () => {
      const mockOrders = [{
        id: 101,
        date: '2026-03-10',
        items: [{ name: 'Test', qty: 1, price: 10 }],
        total: 10
      }]

      wrapper.vm.orders = mockOrders
      await nextTick()

      const orderElement = wrapper.find('.list-row__summary')
      expect(orderElement.text()).toContain('Order #101')
    })

    it('should display order date', async () => {
      const mockOrders = [{
        id: 101,
        date: '2026-03-10',
        items: [{ name: 'Test', qty: 1, price: 10 }],
        total: 10
      }]

      wrapper.vm.orders = mockOrders
      await nextTick()

      const orderElement = wrapper.find('.list-row__summary')
      expect(orderElement.text()).toContain('2026-03-10')
    })

    it('should display order total', async () => {
      const mockOrders = [{
        id: 101,
        date: '2026-03-10',
        items: [{ name: 'Test', qty: 2, price: 15 }],
        total: 30
      }]

      wrapper.vm.orders = mockOrders
      await nextTick()

      const orderElement = wrapper.find('.list-row__price')
      expect(orderElement.text()).toBe('$30.00')
    })
  })

  describe('Order Items', () => {
    it('should display order items in details', async () => {
      const mockOrders = [{
        id: 101,
        date: '2026-03-10',
        items: [
          { name: 'Booster Pack', qty: 2, price: 10 },
          { name: 'Rare Card', qty: 1, price: 25 }
        ],
        total: 45
      }]

      wrapper.vm.orders = mockOrders
      await nextTick()

      const orderItems = wrapper.findAll('.order-items li')
      expect(orderItems).toHaveLength(2)
    })

    it('should display item details correctly', async () => {
      const mockOrders = [{
        id: 101,
        date: '2026-03-10',
        items: [
          { name: 'Booster Pack', qty: 2, price: 10 }
        ],
        total: 20
      }]

      wrapper.vm.orders = mockOrders
      await nextTick()

      const itemElement = wrapper.find('.order-items li')
      expect(itemElement.text()).toContain('2×')
      expect(itemElement.text()).toContain('Booster Pack')
      expect(itemElement.text()).toContain('$20.00')
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
      wrapper.vm.orders = [{ id: 1, date: '2026-03-10', items: [], total: 0 }]
      await nextTick()

      const orderElements = wrapper.findAll('.list-row')
      expect(orderElements).toHaveLength(0)
    })
  })

  describe('Expandable Orders', () => {
    it('should render orders as details elements', async () => {
      const mockOrders = [{
        id: 101,
        date: '2026-03-10',
        items: [{ name: 'Test', qty: 1, price: 10 }],
        total: 10
      }]

      wrapper.vm.orders = mockOrders
      await nextTick()

      const detailsElement = wrapper.find('details')
      expect(detailsElement.exists()).toBe(true)
      expect(detailsElement.classes()).toContain('list-row--expandable')
    })

    it('should have summary element for order header', async () => {
      const mockOrders = [{
        id: 101,
        date: '2026-03-10',
        items: [{ name: 'Test', qty: 1, price: 10 }],
        total: 10
      }]

      wrapper.vm.orders = mockOrders
      await nextTick()

      const summary = wrapper.find('summary')
      expect(summary.exists()).toBe(true)
      expect(summary.classes()).toContain('list-row__summary')
    })
  })
})
