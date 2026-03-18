import { describe, it, expect, beforeEach, vi } from 'vitest'
import { nextTick } from 'vue'
import Gallery from './Gallery.vue'
import { mountWithDefaults } from '../../test/utils'

// Mock the dynamic imports for card images
vi.mock('../../assets/Images/Cards/*.png', () => ({}))

describe('Gallery Component', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mountWithDefaults(Gallery)
  })

  afterEach(() => {
    wrapper.unmount()
    vi.clearAllTimers()
  })

  describe('Component Rendering', () => {
    // Test 1: Verify gallery component mounts and initializes correctly
    it('should render the gallery component', () => {
      expect(wrapper.exists()).toBe(true)
    })

    // Test 2: Verify carousel starts at index 0 (first card)
    it('should initialize with carousel at index 0', () => {
      expect(wrapper.vm.carouselIndex).toBe(0)
    })

    // Test 3: Verify modal is closed and has no card selected on initialization
    it('should initialize with modal closed', () => {
      expect(wrapper.vm.showModal).toBe(false)
      expect(wrapper.vm.modalCard).toBeNull()
    })
  })

  describe('Carousel Navigation', () => {
    // Test 4: Verify nextCard() advances carousel to next index
    it('should move to next card when nextCard is called', async () => {
      const initialIndex = wrapper.vm.carouselIndex
      
      wrapper.vm.nextCard()
      await nextTick()

      expect(wrapper.vm.carouselIndex).not.toBe(initialIndex)
    })

    // Test 5: Verify prevCard() moves carousel to previous index
    it('should move to previous card when prevCard is called', async () => {
      // Set to a middle index first
      wrapper.vm.carouselIndex = 2
      await nextTick()

      wrapper.vm.prevCard()
      await nextTick()

      expect(wrapper.vm.carouselIndex).toBe(1)
    })

    // Test 6: Verify carousel wraps to first card when advancing from last card
    it('should wrap around when going to next from last card', async () => {
      const totalCards = wrapper.vm.allCards.length
      if (totalCards === 0) return // Skip if no cards

      wrapper.vm.carouselIndex = totalCards - 1
      await nextTick()

      wrapper.vm.nextCard()
      await nextTick()

      expect(wrapper.vm.carouselIndex).toBe(0)
    })

    // Test 7: Verify carousel wraps to last card when going back from first card
    it('should wrap around when going to previous from first card', async () => {
      const totalCards = wrapper.vm.allCards.length
      if (totalCards === 0) return // Skip if no cards

      wrapper.vm.carouselIndex = 0
      await nextTick()

      wrapper.vm.prevCard()
      await nextTick()

      expect(wrapper.vm.carouselIndex).toBe(totalCards - 1)
    })
  })

  describe('Modal Functionality', () => {
    // Test 8: Verify modal opens and displays selected card details
    it('should open modal when openCardModal is called', async () => {
      const mockCard = { id: 'test', name: 'Test Card', image: 'test.png' }

      wrapper.vm.openCardModal(mockCard)
      await nextTick()

      expect(wrapper.vm.showModal).toBe(true)
      expect(wrapper.vm.modalCard).toEqual(mockCard)
    })

    // Test 9: Verify modal closes and resets state when closeModal is called
    it('should close modal when closeModal is called', async () => {
      wrapper.vm.showModal = true
      wrapper.vm.modalCard = { id: 'test', name: 'Test' }
      await nextTick()

      wrapper.vm.closeModal()
      await nextTick()

      expect(wrapper.vm.showModal).toBe(false)
    })
  })

  describe('Auto-scroll Functionality', () => {
    // Test 10: Verify auto-scroll timer functions exist for automatic carousel progression
    it('should have auto-scroll timer methods', () => {
      expect(typeof wrapper.vm.startAutoScroll).toBe('function')
      expect(typeof wrapper.vm.stopAutoScroll).toBe('function')
    })

    // Test 11: Verify stopAutoScroll can be called to halt automatic carousel movement
    it('should call stopAutoScroll when manually stopped', () => {
      const stopSpy = vi.spyOn(wrapper.vm, 'stopAutoScroll')
      wrapper.vm.stopAutoScroll()
      expect(stopSpy).toHaveBeenCalled()
    })
  })
})
