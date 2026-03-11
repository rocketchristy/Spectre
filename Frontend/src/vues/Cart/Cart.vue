<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// Cart items — will be populated via API; stubbed with reactive array for now
const cartItems = ref([
  // Example shape:
  // { id: 1, name: 'Booster Pack', type: 'pack', price: 10, quantity: 2, image: '📦' }
])
const loading = ref(false)

// TODO: replace with real API call
// async function fetchCart() { ... }

const cartTotal = computed(() =>
  cartItems.value.reduce((sum, item) => sum + item.price * item.quantity, 0).toFixed(2)
)

function removeItem(id) {
  // TODO: call DELETE /api/cart/:id
  cartItems.value = cartItems.value.filter(item => item.id !== id)
}

function updateQuantity(item, delta) {
  const next = item.quantity + delta
  if (next < 1) return
  // TODO: call PATCH /api/cart/:id
  item.quantity = next
}

function checkout() {
  // TODO: call POST /api/orders from cart
  router.push({ name: 'orderHistory' })
}
</script>

<template>
  <main class="page-shell">
    <h1 class="page-title">Your Cart</h1>

    <p v-if="loading" class="empty-state">Loading…</p>

    <template v-else-if="cartItems.length">
      <div class="card-list">
        <div v-for="item in cartItems" :key="item.id" class="list-row">
          <span class="list-row__icon">{{ item.image }}</span>

          <div class="list-row__info">
            <strong>{{ item.name }}</strong>
            <span class="text-muted">${{ item.price.toFixed(2) }} each</span>
          </div>

          <div class="quantity-control">
            <button @click="updateQuantity(item, -1)" :disabled="item.quantity <= 1">−</button>
            <span class="quantity-control__value">{{ item.quantity }}</span>
            <button @click="updateQuantity(item, 1)">+</button>
          </div>

          <span class="list-row__price">${{ (item.price * item.quantity).toFixed(2) }}</span>

          <button class="btn-icon btn-danger" @click="removeItem(item.id)" title="Remove">✕</button>
        </div>
      </div>

      <div class="summary-bar">
        <span class="summary-bar__total">Total: <strong>${{ cartTotal }}</strong></span>
        <button class="action-btn" @click="checkout">Checkout</button>
      </div>
    </template>

    <div v-else class="empty-state">
      <h2>Your cart is empty</h2>
      <router-link to="/store" class="action-btn">Browse the Store</router-link>
    </div>
  </main>
</template>

<style scoped>
/* Layout handled by shared page.css; only cart-specific tweaks here */
</style>
