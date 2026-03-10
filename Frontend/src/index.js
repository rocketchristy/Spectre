import { createRouter, createWebHistory } from 'vue-router'
import homepage from '@/vues/HomePage/HomePage.vue'
import store from '@/vues/Store/Store.vue'
import product from '@/vues/Product/Product.vue'
// import OrderHistory from '@/vues/OrderHistory/OrderHistory.vue'
// import profile from '@/vues/Profile/Profile.vue'
// import checkout from '@/vues/Checkout/Checkout.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'homepage', component: homepage },
    { path: '/store', name: 'store', component: store },
    { path: '/product/:type/:id', name: 'product', component: product },

  ],
})

export default router
