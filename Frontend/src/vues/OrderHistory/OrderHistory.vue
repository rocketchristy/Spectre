<script setup>
import { ref, computed, onMounted } from 'vue'
import { getOrders } from '@/utils/api.js'

const rawOrders = ref([])
const loading = ref(true)
const errorMsg = ref('')

async function fetchOrders() {
  loading.value = true
  errorMsg.value = ''
  try {
    const data = await getOrders()
    rawOrders.value = data || []
  } catch (e) {
    errorMsg.value = e.message
  } finally {
    loading.value = false
  }
}

onMounted(fetchOrders)

// Group flat joined rows by ORDER_ID
const orders = computed(() => {
  const map = {}
  for (const row of rawOrders.value) {
    const id = row.ORDER_ID ?? row.ID
    if (!map[id]) {
      map[id] = {
        ID: id,
        CREATED_AT: row.CREATED_AT,
        STATUS: row.STATUS,
        items: []
      }
    }
    if (row.PRODUCT_NAME) {
      map[id].items.push({
        PRODUCT_NAME: row.PRODUCT_NAME,
        QUANTITY: row.QUANTITY,
        UNIT_PRICE_CENTS: row.UNIT_PRICE_CENTS,
      })
    }
  }
  return Object.values(map)
})

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function orderTotal(order) {
  const cents = order.items.reduce((sum, i) => sum + i.UNIT_PRICE_CENTS * i.QUANTITY, 0)
  return (cents / 100).toFixed(2)
}

function itemsSummary(order) {
  if (!order.items.length) return '—'
  return order.items.map(i => `${i.QUANTITY}× ${i.PRODUCT_NAME}`).join(', ')
}
import { ref, computed, onMounted } from 'vue'
import { getOrders } from '@/utils/api.js'

const rawOrders = ref([])
const loading = ref(true)
const errorMsg = ref('')

async function fetchOrders() {
  loading.value = true
  errorMsg.value = ''
  try {
    const data = await getOrders()
    rawOrders.value = data || []
  } catch (e) {
    errorMsg.value = e.message
  } finally {
    loading.value = false
  }
}

onMounted(fetchOrders)

// Group flat joined rows by ORDER_ID
const orders = computed(() => {
  const map = {}
  for (const row of rawOrders.value) {
    const id = row.ORDER_ID ?? row.ID
    if (!map[id]) {
      map[id] = {
        ID: id,
        CREATED_AT: row.CREATED_AT,
        STATUS: row.STATUS,
        items: []
      }
    }
    if (row.PRODUCT_NAME) {
      map[id].items.push({
        PRODUCT_NAME: row.PRODUCT_NAME,
        QUANTITY: row.QUANTITY,
        UNIT_PRICE_CENTS: row.UNIT_PRICE_CENTS,
      })
    }
  }
  return Object.values(map)
})

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function orderTotal(order) {
  const cents = order.items.reduce((sum, i) => sum + i.UNIT_PRICE_CENTS * i.QUANTITY, 0)
  return (cents / 100).toFixed(2)
}

function itemsSummary(order) {
  if (!order.items.length) return '—'
  return order.items.map(i => `${i.QUANTITY}× ${i.PRODUCT_NAME}`).join(', ')
}
</script>

<template>
  <main class="page-shell">
    <h1 class="page-title">Order History</h1>

    <p v-if="loading" class="empty-state">Loading…</p>

    <p v-if="errorMsg" class="empty-state" style="color: #f44336;">{{ errorMsg }}</p>

    <p v-if="errorMsg" class="empty-state" style="color: #f44336;">{{ errorMsg }}</p>

    <template v-else-if="orders.length">
      <div class="orders-table-wrapper">
        <table class="orders-table">
          <thead>
            <tr>
              <th>Order #</th>
              <th>Date / Time</th>
              <th>Items Purchased</th>
              <th>Cost</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="order in orders" :key="order.ID">
              <td class="col-order">{{ order.ID }}</td>
              <td class="col-date">{{ formatDate(order.CREATED_AT) }}</td>
              <td class="col-items">{{ itemsSummary(order) }}</td>
              <td class="col-cost">${{ orderTotal(order) }}</td>
              <td class="col-status">
                <span class="status-badge" :class="'status-' + (order.STATUS || 'completed').toLowerCase()">
                  {{ order.STATUS || 'Completed' }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      <div class="orders-table-wrapper">
        <table class="orders-table">
          <thead>
            <tr>
              <th>Order #</th>
              <th>Date / Time</th>
              <th>Items Purchased</th>
              <th>Cost</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="order in orders" :key="order.ID">
              <td class="col-order">{{ order.ID }}</td>
              <td class="col-date">{{ formatDate(order.CREATED_AT) }}</td>
              <td class="col-items">{{ itemsSummary(order) }}</td>
              <td class="col-cost">${{ orderTotal(order) }}</td>
              <td class="col-status">
                <span class="status-badge" :class="'status-' + (order.STATUS || 'completed').toLowerCase()">
                  {{ order.STATUS || 'Completed' }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>

    <div v-else-if="!loading" class="empty-state">
    <div v-else-if="!loading" class="empty-state">
      <h2>No orders yet</h2>
      <router-link to="/store" class="action-btn">Start Shopping</router-link>
    </div>
  </main>
</template>

<style scoped>
/* Override global page.css to make table opaque with retro tokens */
.orders-table th {
  background: linear-gradient(90deg, var(--water) 0%, #064a70 100%);
  color: #000;
  position: sticky;
  top: 0;
}

.orders-table tbody tr { background: var(--bg-panel); }
.orders-table tbody tr:hover { background: rgba(181, 216, 13, 0.06); }

.col-order { color: var(--shadow); }
.col-date { color: var(--neutral); white-space: nowrap; }
.col-items { max-width: 300px; }
.col-cost { color: var(--grass); }

.status-completed { background: rgba(181, 216, 13, 0.15); color: var(--grass); }
.status-pending   { background: rgba(255, 224, 151, 0.15); color: var(--stone); }
.status-cancelled { background: rgba(128, 21, 2, 0.15); color: var(--fire); }
.status-processing{ background: rgba(12, 157, 215, 0.15); color: var(--water); }

@media (max-width: 768px) {
  .orders-table th, .orders-table td { padding: 0.5rem; font-size: 0.85rem; }
  .col-items { max-width: 160px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
}
</style>
