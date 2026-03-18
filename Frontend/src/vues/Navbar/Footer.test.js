import { describe, it, expect, beforeEach } from 'vitest'
import Footer from './Footer.vue'
import { mountWithDefaults } from '../../test/utils'

describe('Footer Component', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mountWithDefaults(Footer)
  })

  afterEach(() => {
    wrapper.unmount()
  })

  describe('Component Rendering', () => {
    it('should render the footer component', () => {
      expect(wrapper.exists()).toBe(true)
      expect(wrapper.find('.main-footer').exists()).toBe(true)
    })

    it('should display footer content section', () => {
      const footerContent = wrapper.find('.footer-content')
      expect(footerContent.exists()).toBe(true)
    })

    it('should display footer bottom section', () => {
      const footerBottom = wrapper.find('.footer-bottom')
      expect(footerBottom.exists()).toBe(true)
    })
  })

  describe('Logo Section', () => {
    it('should display the footer logo', () => {
      const logo = wrapper.find('.footer-logo-image')
      expect(logo.exists()).toBe(true)
      expect(logo.attributes('alt')).toBe('NXT TCG')
    })

    it('should display brand name', () => {
      const footerLogo = wrapper.find('.footer-logo')
      expect(footerLogo.text()).toContain('NXT TCG')
    })

    it('should display brand tagline', () => {
      const footerInfo = wrapper.find('.footer-info')
      expect(footerInfo.text()).toContain('Collect, play, and enjoy.')
    })
  })

  describe('Resource Links', () => {
    it('should display Resources section', () => {
      const sections = wrapper.findAll('.footer-col h4')
      const resourcesSection = sections.find(s => s.text() === 'Resources')
      expect(resourcesSection).toBeDefined()
    })

    it('should display resource links', () => {
      const footerLinks = wrapper.findAll('.footer-links')
      const resourceLinks = footerLinks[0]
      
      expect(resourceLinks.text()).toContain('Docs')
      expect(resourceLinks.text()).toContain('Tutorials')
      expect(resourceLinks.text()).toContain('Community')
    })

    it('should have correct number of resource links', () => {
      const footerLinks = wrapper.findAll('.footer-links')
      const resourceLinks = footerLinks[0].findAll('li')
      expect(resourceLinks).toHaveLength(3)
    })
  })

  describe('Company Links', () => {
    it('should display Company section', () => {
      const sections = wrapper.findAll('.footer-col h4')
      const companySection = sections.find(s => s.text() === 'Company')
      expect(companySection).toBeDefined()
    })

    it('should display company links', () => {
      const footerLinks = wrapper.findAll('.footer-links')
      const companyLinks = footerLinks[1]
      
      expect(companyLinks.text()).toContain('About')
      expect(companyLinks.text()).toContain('Careers')
      expect(companyLinks.text()).toContain('Contact')
    })

    it('should have correct number of company links', () => {
      const footerLinks = wrapper.findAll('.footer-links')
      const companyLinks = footerLinks[1].findAll('li')
      expect(companyLinks).toHaveLength(3)
    })
  })

  describe('Footer Bottom', () => {
    it('should display copyright notice', () => {
      const copyright = wrapper.find('.copyright')
      expect(copyright.exists()).toBe(true)
      expect(copyright.text()).toContain('© 2026 NXTCG')
    })

    it('should display footer navigation', () => {
      const footerNav = wrapper.find('.footer-nav')
      expect(footerNav.exists()).toBe(true)
    })

    it('should have Privacy link', () => {
      const footerNav = wrapper.find('.footer-nav')
      expect(footerNav.text()).toContain('Privacy')
    })

    it('should have Terms link', () => {
      const footerNav = wrapper.find('.footer-nav')
      expect(footerNav.text()).toContain('Terms')
    })

    it('should have Contact link', () => {
      const footerNav = wrapper.find('.footer-nav')
      expect(footerNav.text()).toContain('Contact')
    })
  })

  describe('Link Elements', () => {
    it('should have clickable links in Resources', () => {
      const footerLinks = wrapper.findAll('.footer-links')
      const resourceLinks = footerLinks[0].findAll('a')
      expect(resourceLinks.length).toBeGreaterThan(0)
    })

    it('should have clickable links in Company', () => {
      const footerLinks = wrapper.findAll('.footer-links')
      const companyLinks = footerLinks[1].findAll('a')
      expect(companyLinks.length).toBeGreaterThan(0)
    })

    it('should have clickable links in footer navigation', () => {
      const footerNavLinks = wrapper.find('.footer-nav').findAll('a')
      expect(footerNavLinks).toHaveLength(3)
    })
  })

  describe('Footer Structure', () => {
    it('should have multiple footer columns', () => {
      const columns = wrapper.findAll('.footer-col')
      expect(columns.length).toBeGreaterThanOrEqual(2)
    })

    it('should have footer info section', () => {
      const footerInfo = wrapper.find('.footer-info')
      expect(footerInfo.exists()).toBe(true)
    })

    it('should properly structure footer content', () => {
      const footerContent = wrapper.find('.footer-content')
      const children = footerContent.element.children
      expect(children.length).toBeGreaterThan(0)
    })
  })
})
