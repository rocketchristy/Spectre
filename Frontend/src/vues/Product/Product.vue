<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getProducts, getInventory, addToCart } from '@/utils/api.js'
import { prices, mysteryProductTypes, elementEmoji } from '@/utils/prices.js'

const route = useRoute()
const router = useRouter()

const productType = computed(() => route.params.type)
const productId   = computed(() => route.params.id)

const products = ref([])
const inventory = ref([])
const loading = ref(true)

async function fetchData() {
  loading.value = true
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
}

onMounted(fetchData)

// ---------- Mystery products ----------
const isMystery = computed(() => productType.value?.startsWith('mystery-'))

const mysteryProduct = computed(() => {
  if (!isMystery.value) return null
  const tier = productType.value.replace('mystery-', '')
  const element = productId.value
  const info = mysteryProductTypes[tier]
  if (!info) return null
  return {
    name: `${element} ${info.name}`,
    description: `${info.cards} random ${element} card${info.cards > 1 ? 's' : ''}`,
    price: prices[0][info.priceKey],
    image: elementEmoji[element] || '🎴',
    stock: 50,
  }
})

const quantity = ref(1)

// ---------- Card data from API ----------
const isCard = computed(() => productType.value === 'card')

// All variants of this product from the products catalog
const productVariants = computed(() => {
  if (!isCard.value) return []
  return products.value.filter(p => p.PRODUCT_NAME === productId.value)
})

// Unique modifier names for filtering
const availableModifiers = computed(() => {
  return [...new Set(productVariants.value.map(p => p.MODIFIER_NAME))]
})

// Product info from the first variant
const productInfo = computed(() => {
  if (!productVariants.value.length) return null
  const first = productVariants.value[0]
  return {
    name: first.PRODUCT_NAME,
    styleName: first.STYLE_NAME,
    seriesName: first.SERIES_NAME,
    image: first.URL || null,
  }
})

// Inventory listings for this product (only items with stock)
const productListings = computed(() => {
  if (!isCard.value) return []
  return inventory.value.filter(i =>
    i.PRODUCT_NAME === productId.value &&
    i.QUANTITY_AVAILABLE && i.QUANTITY_AVAILABLE > 0
  )
})

// Filter state
const selectedModifier = ref('')

watch(productId, () => {
  selectedModifier.value = ''
  quantity.value = 1
})

// Filtered listings
const filteredListings = computed(() => {
  return productListings.value.filter(i => {
    if (selectedModifier.value && i.MODIFIER_NAME !== selectedModifier.value) return false
    return true
  })
})

// ---------- Current product (for the header area) ----------
const currentProduct = computed(() => {
  if (isMystery.value) return mysteryProduct.value
  if (isCard.value && productInfo.value) {
    return {
      name: productInfo.value.name,
      description: `${productInfo.value.styleName} · ${productInfo.value.seriesName}`,
      imageUrl: productInfo.value.image,
      image: productInfo.value.image ? null : '🃏',
    }
  }
  if (isCard.value && !loading.value) return null
  return null
})

// Mystery product price helpers
const mysteryTotalPrice = computed(() => {
  if (!mysteryProduct.value) return null
  const base = parseFloat(mysteryProduct.value.price.replace('$', ''))
  return (base * quantity.value).toFixed(2)
})

// Add to cart handler
async function handleAddToCart(listing) {
  try {
    await addToCart(
      listing.INVENTORY_ID,
      1,
      listing.UNIT_PRICE_CENTS,
      listing.CURRENCY_CODE || 'USD'
    )
  } catch (e) {
    alert(e.message || 'Failed to add to cart')
  }
}
</script>

<template>
  <main class="page-shell product-page">
    <router-link to="/store" class="back-link">← Back to Store</router-link>

    <p v-if="loading && isCard" class="empty-state">Loading product…</p>

    <div v-else-if="currentProduct" class="product-container">
      <div class="product-image-section">
        <div class="product-image-large">
          <img v-if="currentProduct.imageUrl" :src="currentProduct.imageUrl" :alt="currentProduct.name" class="product-img" />
          <span v-else>{{ currentProduct.image }}</span>
        </div>
      </div>

      <div class="product-details">
        <h1>{{ currentProduct.name }}</h1>
        <p class="description">{{ currentProduct.description }}</p>

        <!-- Mystery product -->
        <template v-if="isMystery && mysteryProduct">
          <div class="price-section">
            <span class="price">${{ mysteryTotalPrice }}</span>
            <span class="stock">{{ mysteryProduct.stock }} in stock</span>
          </div>
          <div class="quantity-control">
            <button @click="quantity = Math.max(1, quantity - 1)" :disabled="quantity <= 1">−</button>
            <input type="number" v-model.number="quantity" :min="1" :max="mysteryProduct.stock"
              @change="quantity = Math.min(Math.max(1, quantity), mysteryProduct.stock)" />
            <button @click="quantity = Math.min(quantity + 1, mysteryProduct.stock)"
              :disabled="quantity >= mysteryProduct.stock">+</button>
          </div>
          <button class="action-btn buy-btn" :disabled="mysteryProduct.stock === 0">
            Add {{ quantity }} to Cart
          </button>
        </template>

        <!-- Card product: filter + seller listings -->
        <template v-else-if="isCard">
          <div v-if="availableModifiers.length > 1" class="filters">
            <div class="filter-group">
              <label>Variant</label>
              <select v-model="selectedModifier">
                <option value="">All variants</option>
                <option v-for="m in availableModifiers" :key="m" :value="m">{{ m }}</option>
              </select>
            </div>
          </div>

          <!-- Seller listings table -->
          <h2 class="section-heading">Listings ({{ filteredListings.length }})</h2>

          <div v-if="filteredListings.length" class="seller-listings">
            <div class="listing-header">
              <span>Seller</span>
              <span>Variant</span>
              <span>Qty</span>
              <span>Price</span>
              <span></span>
            </div>
            <div v-for="listing in filteredListings" :key="listing.INVENTORY_ID" class="listing-row">
              <span class="listing-seller">Seller #{{ listing.SELLER_ID }}</span>
              <span>{{ listing.MODIFIER_NAME }}</span>
              <span>{{ listing.QUANTITY_AVAILABLE }}</span>
              <span class="listing-price">${{ (listing.UNIT_PRICE_CENTS / 100).toFixed(2) }}</span>
              <button class="action-btn listing-buy-btn" @click="handleAddToCart(listing)">Add to Cart</button>
            </div>
          </div>
          <p v-else class="text-muted">No listings available for this product.</p>
        </template>
      </div>
    </div>

    <div v-else-if="!loading" class="empty-state">
      <h2>Product not found</h2>
      <router-link to="/store">Return to store</router-link>
    </div>
  </main>
</template>

<style scoped>
.product-page {
  max-width: 1000px;
}

.product-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 3rem;
}

@media (max-width: 768px) {
  .product-container {
    grid-template-columns: 1fr;
  }
}

.product-image-section {
  display: flex;
  justify-content: center;
  align-items: center;
}

.product-image-large {
  font-size: 12rem;
  background: var(--color-background-soft, #1a1a2e);
  border-radius: 12px;
  padding: 3rem;
  border: 1px solid var(--color-border, #333);
}

.product-details h1 {
  margin: 0 0 1rem;
  color: var(--color-heading, #fff);
}

.product-img {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
}

.buy-btn {
  width: 100%;
}
</style>
