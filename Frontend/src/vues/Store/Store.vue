<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getProducts, getInventory, addInventoryItem } from '@/utils/api.js'
import { prices, elements, elementEmoji, mysteryProductTypes } from '@/utils/prices.js'

const router = useRouter()
const products = ref([])
const inventory = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const [productsData, inventoryData] = await Promise.all([
      getProducts(),
      getInventory(),
    ])
    products.value = productsData
    inventory.value = inventoryData
    loading.value = false
  } catch (e) {
    router.push({ name: 'error', query: { message: e.message } })
  }
})

// ---------- Mystery products (7 elements × 3 tiers) ----------
const mysteryGrid = computed(() =>
  elements.map(el => ({
    element: el,
    emoji: elementEmoji[el],
    products: Object.entries(mysteryProductTypes).map(([key, p]) => ({
      id: `${el.toLowerCase()}-${key}`,
      routeType: `mystery-${key}`,
      routeId: el,
      name: `${el} ${p.name}`,
      cards: p.cards,
      price: prices[0][p.priceKey],
      emoji: elementEmoji[el],
    })),
  }))
)

// ---------- Products from API, deduplicated by PRODUCT_NAME ----------
const uniqueProducts = computed(() => {
  const map = new Map()
  for (const p of products.value) {
    const price = (p.BASE_PRICE_CENTS + p.PRICE_DELTA_CENTS) / 100
    if (!map.has(p.PRODUCT_NAME)) {
      map.set(p.PRODUCT_NAME, {
        name: p.PRODUCT_NAME,
        styleName: p.STYLE_NAME,
        seriesName: p.SERIES_NAME,
        price: price.toFixed(2),
        image: p.URL || null,
        sku: p.SKU,
      })
    } else {
      const existing = map.get(p.PRODUCT_NAME)
      if (price < parseFloat(existing.price)) {
        existing.price = price.toFixed(2)
      }
      if (!existing.image && p.URL) {
        existing.image = p.URL
      }
    }
  }
  return [...map.values()]
})

// All unique card names
const allCardNames = computed(() => uniqueProducts.value)

// Group by STYLE_NAME for category sections
const styleGroups = computed(() => {
  const groups = new Map()
  for (const p of uniqueProducts.value) {
    if (!groups.has(p.styleName)) {
      groups.set(p.styleName, [])
    }
    groups.get(p.styleName).push(p)
  }
  return groups
})

// ---------- Bargain Bin: cheapest seller listings ----------
const bargainCards = computed(() => {
  const withInventory = inventory.value
    .filter(i => i.QUANTITY_AVAILABLE && i.QUANTITY_AVAILABLE > 0 && i.UNIT_PRICE_CENTS)
    .sort((a, b) => a.UNIT_PRICE_CENTS - b.UNIT_PRICE_CENTS)
  const seen = new Set()
  return withInventory.filter(i => {
    if (seen.has(i.PRODUCT_NAME)) return false
    seen.add(i.PRODUCT_NAME)
    return true
  }).slice(0, 12)
})

// ---------- Rare Finds: most expensive seller listings ----------
const rareFinds = computed(() => {
  const withInventory = inventory.value
    .filter(i => i.QUANTITY_AVAILABLE && i.QUANTITY_AVAILABLE > 0 && i.UNIT_PRICE_CENTS)
    .sort((a, b) => b.UNIT_PRICE_CENTS - a.UNIT_PRICE_CENTS)
  const seen = new Set()
  return withInventory.filter(i => {
    if (seen.has(i.PRODUCT_NAME)) return false
    seen.add(i.PRODUCT_NAME)
    return true
  }).slice(0, 12)
})

// ---------- Search ----------
const searchQuery = ref('')
const searchResults = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return []
  return uniqueProducts.value
    .filter(p => p.name.toLowerCase().includes(q))
    .slice(0, 12)
})
function clearSearch() { searchQuery.value = '' }

// ---------- Sell a Card modal ----------
const showSellModal = ref(false)
const sellForm = ref({ productName: '', modifier: '', quantity: 1, price: '' })
const sellError = ref('')

const sellProductNames = computed(() => {
  return [...new Set(products.value.map(p => p.PRODUCT_NAME))].sort()
})

const sellModifiers = computed(() => {
  if (!sellForm.value.productName) return []
  return products.value
    .filter(p => p.PRODUCT_NAME === sellForm.value.productName)
    .map(p => ({
      sku: p.SKU,
      modifierName: p.MODIFIER_NAME,
      suggestedPrice: ((p.BASE_PRICE_CENTS + p.PRICE_DELTA_CENTS) / 100).toFixed(2),
    }))
})

const selectedVariant = computed(() => {
  return sellModifiers.value.find(m => m.sku === sellForm.value.modifier) || null
})

function openSellModal() {
  sellForm.value = { productName: '', modifier: '', quantity: 1, price: '' }
  sellError.value = ''
  showSellModal.value = true
}

function closeSellModal() { showSellModal.value = false }

async function submitSell() {
  const f = sellForm.value
  if (!f.productName || !f.modifier) {
    sellError.value = 'Please select a product and variant.'
    return
  }
  const price = parseFloat(f.price || selectedVariant.value?.suggestedPrice)
  if (!price || price <= 0) {
    sellError.value = 'Please enter a valid price.'
    return
  }
  const quantity = parseInt(f.quantity) || 1
  try {
    await addInventoryItem(f.modifier, quantity, Math.round(price * 100), 'USD')
    showSellModal.value = false
    inventory.value = await getInventory()
  } catch (e) {
    sellError.value = e.message || 'Failed to list item for sale.'
  }
}
</script>

<template>
  <main class="page-shell">
    <h1 class="page-title">Store</h1>

    <p v-if="loading" class="empty-state">Loading products…</p>

    <template v-else>
      <!-- Sell a Card -->
      <div class="sell-bar">
        <button class="action-btn sell-btn" @click="openSellModal">Sell a Card</button>
      </div>

      <!-- Search bar -->
      <div class="search-wrapper">
        <input v-model="searchQuery" class="search-input" type="text" placeholder="Search for a card…" />
        <div v-if="searchResults.length" class="search-results">
          <router-link
            v-for="card in searchResults" :key="card.name"
            :to="{ name: 'product', params: { type: 'card', id: card.name } }"
            @click="clearSearch"
          >{{ card.name }}</router-link>
        </div>
      </div>

      <!-- Mystery Products by Element -->
      <section v-for="group in mysteryGrid" :key="group.element" class="product-section">
        <h2 class="section-heading">{{ group.emoji }} {{ group.element }}</h2>
        <div class="product-grid">
          <router-link
            v-for="p in group.products" :key="p.id"
            :to="{ name: 'product', params: { type: p.routeType, id: p.routeId } }"
            class="product-card"
          >
            <div class="product-image">{{ p.emoji }}</div>
            <h3>{{ p.name }}</h3>
            <p class="product-description">{{ p.cards }} random card{{ p.cards > 1 ? 's' : '' }}</p>
            <p class="product-price">{{ p.price }}</p>
          </router-link>
        </div>
      </section>

      <!-- All Cards -->
      <section class="product-section">
        <h2 class="section-heading">All Cards</h2>
        <div class="product-grid product-grid--scroll">
          <router-link v-for="card in allCardNames" :key="card.name"
            :to="{ name: 'product', params: { type: 'card', id: card.name } }"
            class="product-card product-card--sm"
          >
            <div class="product-image">
              <img v-if="card.image" :src="card.image" :alt="card.name" class="card-img" />
              <span v-else>🃏</span>
            </div>
            <h3>{{ card.name }}</h3>
            <p class="product-price">From ${{ card.price }}</p>
          </router-link>
        </div>
      </section>

      <!-- Dynamic Category Sections by Style -->
      <section v-for="[styleName, cards] in styleGroups" :key="styleName" class="product-section">
        <h2 class="section-heading">{{ styleName }}</h2>
        <div class="product-grid product-grid--scroll">
          <router-link v-for="card in cards" :key="card.name"
            :to="{ name: 'product', params: { type: 'card', id: card.name } }"
            class="product-card product-card--sm"
          >
            <div class="product-image">
              <img v-if="card.image" :src="card.image" :alt="card.name" class="card-img" />
              <span v-else>🃏</span>
            </div>
            <h3>{{ card.name }}</h3>
            <p class="product-price">From ${{ card.price }}</p>
          </router-link>
        </div>
      </section>

      <!-- Bargain Bin -->
      <section v-if="bargainCards.length" class="product-section">
        <h2 class="section-heading">Bargain Bin</h2>
        <p class="text-muted" style="margin-bottom:1rem">Lowest priced listings from sellers</p>
        <div class="product-grid product-grid--scroll">
          <router-link v-for="card in bargainCards" :key="card.SKU + '-' + card.INVENTORY_ID"
            :to="{ name: 'product', params: { type: 'card', id: card.PRODUCT_NAME } }"
            class="product-card product-card--sm"
          >
            <div class="product-image">
              <img v-if="card.URL" :src="card.URL" :alt="card.PRODUCT_NAME" class="card-img" />
              <span v-else>🃏</span>
            </div>
            <h3>{{ card.PRODUCT_NAME }}</h3>
            <p class="product-description">{{ card.MODIFIER_NAME }}</p>
            <p class="product-price">${{ (card.UNIT_PRICE_CENTS / 100).toFixed(2) }}</p>
          </router-link>
        </div>
      </section>

      <!-- Rare Finds -->
      <section v-if="rareFinds.length" class="product-section">
        <h2 class="section-heading">Rare Finds</h2>
        <p class="text-muted" style="margin-bottom:1rem">Premium listings from sellers</p>
        <div class="product-grid product-grid--scroll">
          <router-link v-for="card in rareFinds" :key="card.SKU + '-' + card.INVENTORY_ID"
            :to="{ name: 'product', params: { type: 'card', id: card.PRODUCT_NAME } }"
            class="product-card product-card--sm"
          >
            <div class="product-image">
              <img v-if="card.URL" :src="card.URL" :alt="card.PRODUCT_NAME" class="card-img" />
              <span v-else>🃏</span>
            </div>
            <h3>{{ card.PRODUCT_NAME }}</h3>
            <p class="product-description">{{ card.MODIFIER_NAME }}</p>
            <p class="product-price">${{ (card.UNIT_PRICE_CENTS / 100).toFixed(2) }}</p>
          </router-link>
        </div>
      </section>

      <!-- Sell a Card Modal -->
      <div v-if="showSellModal" class="modal-overlay" @click="closeSellModal">
        <div class="modal" @click.stop>
          <div class="modal-header">
            <h2>Sell a Card</h2>
            <button class="modal-close" @click="closeSellModal">&times;</button>
          </div>
          <form @submit.prevent="submitSell" class="modal-form">
            <div class="form-group">
              <label class="form-label">Card Name</label>
              <select v-model="sellForm.productName" class="form-input" @change="sellForm.modifier = ''">
                <option value="">Select a card…</option>
                <option v-for="n in sellProductNames" :key="n" :value="n">{{ n }}</option>
              </select>
            </div>
            <div v-if="sellModifiers.length" class="form-group">
              <label class="form-label">Variant</label>
              <select v-model="sellForm.modifier" class="form-input">
                <option value="">Select variant…</option>
                <option v-for="m in sellModifiers" :key="m.sku" :value="m.sku">{{ m.modifierName }}</option>
              </select>
            </div>
            <div v-if="selectedVariant" class="form-group">
              <label class="form-label">Suggested Price</label>
              <p class="suggested-price">${{ selectedVariant.suggestedPrice }}</p>
            </div>
            <div class="form-group">
              <label class="form-label">Quantity</label>
              <input v-model.number="sellForm.quantity" type="number" min="1" class="form-input" placeholder="1" />
            </div>
            <div class="form-group">
              <label class="form-label">Your Price ($)</label>
              <input v-model="sellForm.price" type="number" step="0.01" min="0.01" class="form-input"
                :placeholder="selectedVariant ? selectedVariant.suggestedPrice : 'Enter price'" />
            </div>
            <p v-if="sellError" class="modal-error">{{ sellError }}</p>
            <div class="modal-actions">
              <button type="button" class="btn btn-secondary" @click="closeSellModal">Cancel</button>
              <button type="submit" class="btn btn-primary">List for Sale</button>
            </div>
          </form>
        </div>
      </div>
    </template>
  </main>
</template>

<style scoped>
.product-section {
  margin-bottom: 3rem;
}
.card-img {
  width: 100%;
  max-width: 120px;
  height: auto;
  border-radius: 6px;
}
</style>
