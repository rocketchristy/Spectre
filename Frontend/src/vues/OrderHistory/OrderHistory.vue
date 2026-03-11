<script setup>
import { ref } from 'vue'

const orders = ref([
  // Example shape:
  // { id: 101, date: '2026-03-10', items: [ { name: 'Booster Pack', qty: 2, price: 10 } ], total: 20 }
])
const loading = ref(false)

// TODO: replace with real API call
// async function fetchOrders() { ... }
</script>

<template>
  <main class="page-shell">
    <h1 class="page-title">Order History</h1>

    <p v-if="loading" class="empty-state">Loading…</p>

    <template v-else-if="orders.length">
      <div class="card-list">
        <details v-for="order in orders" :key="order.id" class="list-row list-row--expandable">
          <summary class="list-row__summary">
            <span><strong>Order #{{ order.id }}</strong></span>
            <span class="text-muted">{{ order.date }}</span>
            <span class="list-row__price">${{ order.total.toFixed(2) }}</span>
          </summary>

          <ul class="order-items">
            <li v-for="(item, idx) in order.items" :key="idx">
              {{ item.qty }}× {{ item.name }} — ${{ (item.qty * item.price).toFixed(2) }}
            </li>
          </ul>
        </details>
      </div>
    </template>

    <div v-else class="empty-state">
      <h2>No orders yet</h2>
      <router-link to="/store" class="action-btn">Start Shopping</router-link>
    </div>
  </main>
</template>

<style scoped>
.list-row--expandable {
  cursor: pointer;
}

.list-row__summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  list-style: none;
}

.list-row__summary::-webkit-details-marker {
  display: none;
}

.order-items {
  margin: 0.75rem 0 0 1.25rem;
  padding: 0;
  list-style: disc;
  color: var(--color-text, #ccc);
  font-size: 0.9rem;
}
</style>
