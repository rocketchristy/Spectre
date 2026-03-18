import { describe, it, expect, beforeEach, vi } from 'vitest'
import { nextTick } from 'vue'
import Navbar from './Navbar.vue'
import { mountWithDefaults } from '../../test/utils'

describe('Navbar Component', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mountWithDefaults(Navbar)
  })

  afterEach(() => {
    wrapper.unmount()
  })

  describe('Component Rendering', () => {
    it('should render the navbar component', () => {
      expect(wrapper.exists()).toBe(true)
      expect(wrapper.find('.navbar').exists()).toBe(true)
    })

    it('should display navigation links', () => {
      const navLinks = wrapper.findAll('.nav-link')
      expect(navLinks.length).toBeGreaterThan(0)
      
      // Check for expected navigation items
      const linkTexts = navLinks.map(link => link.text())
      expect(linkTexts).toContain('Store')
      expect(linkTexts).toContain('Gallery')
      expect(linkTexts).toContain('Cart')
    })

    it('should display logo', () => {
      const logo = wrapper.find('.logo')
      expect(logo.exists()).toBe(true)
      expect(logo.attributes('alt')).toBe('NXTCG Logo')
    })

    it('should display brand text', () => {
      const brandText = wrapper.find('.brand-text')
      expect(brandText.exists()).toBe(true)
      expect(brandText.text()).toBe('NXTCG')
    })
  })

  describe('Navigation Links', () => {
    it('should have correct navigation structure', () => {
      const navItems = wrapper.findAll('.nav-item')
      expect(navItems.length).toBeGreaterThanOrEqual(5)
    })

    it('should render RouterLink components', () => {
      const routerLinks = wrapper.findAll('.nav-link')
      expect(routerLinks.length).toBeGreaterThan(0)
    })

    it('should display all expected navigation items', () => {
      const expectedLinks = ['Store', 'Gallery', 'Cart', 'Orders', 'Profile']
      const navLinks = wrapper.findAll('.nav-item')
      
      expectedLinks.forEach(linkText => {
        const hasLink = navLinks.some(item => item.text().includes(linkText))
        expect(hasLink).toBe(true)
      })
    })
  })

  describe('Brand Section', () => {
    it('should have home link on brand', () => {
      const brandLink = wrapper.find('.brand-link')
      expect(brandLink.exists()).toBe(true)
    })

    it('should display brand with logo and text', () => {
      const brand = wrapper.find('.navbar-brand')
      expect(brand.exists()).toBe(true)
      expect(brand.find('.logo').exists()).toBe(true)
      expect(brand.find('.brand-text').exists()).toBe(true)
    })
  })
})
