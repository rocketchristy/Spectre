import { createRouter, createWebHistory } from 'vue-router'
import homepage from '@/vues/LandingPage/LandingPage.vue'
import store from '@/vues/Store/Store.vue'
import product from '@/vues/Product/Product.vue'
import cart from '@/vues/Cart/Cart.vue'
import OrderHistory from '@/vues/OrderHistory/OrderHistory.vue'
import UserProfile from '@/vues/UserProfile/UserProfile.vue'
import Gallery from '@/vues/Gallery/Gallery.vue'
import ErrorPage from '@/vues/Error/Error.vue'
import AboutUs from '@/vues/AboutUs/AboutUs.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'landing', component: homepage },
    { path: '/store', name: 'store', component: store },
    { path: '/gallery', name: 'gallery', component: Gallery },
    { path: '/product/:type/:id', name: 'product', component: product },
    { path: '/cart', name: 'cart', component: cart },
    { path: '/orders', name: 'orderHistory', component: OrderHistory },
    { path: '/profile', name: 'profile', component: UserProfile },
    { path: '/error', name: 'error', component: ErrorPage },
    { path: '/about', name: 'about', component: AboutUs }

  ],
})

const REQUIRED_CARDS = ['Claire', 'Ben', 'Bryce', 'Jessalyn', 'Christy']
router.beforeEach((to) => {
  if (to.name === 'about') {
    const found = JSON.parse(localStorage.getItem('nxtcg_found_cards') || '[]')
    if (!REQUIRED_CARDS.every(n => found.includes(n))) {
      return { name: 'store' }
    }
  }
})

export default router
