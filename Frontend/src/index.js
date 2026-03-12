import { createRouter, createWebHistory } from 'vue-router'
import homepage from '@/vues/LandingPage/LandingPage.vue'
import store from '@/vues/Store/Store.vue'
import product from '@/vues/Product/Product.vue'
import cart from '@/vues/Cart/Cart.vue'
import orderHistory from '@/vues/OrderHistory/OrderHistory.vue'
// import profile from '@/vues/UserProfile/UserProfile.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'landing', component: homepage },
    { path: '/store', name: 'store', component: store },
    { path: '/product/:type/:id', name: 'product', component: product },
    { path: '/cart', name: 'cart', component: cart },
    { path: '/orders', name: 'orderHistory', component: orderHistory },
    // { path: '/profile', name: 'profile', component: profile },
  ],
})

export default router
