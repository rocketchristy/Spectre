<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getProducts, getInventory, addToCart } from '@/utils/api.js'

const route = useRoute()
const router = useRouter()

const productType = computed(() => route.params.type)
const productId   = computed(() => route.params.id)

const products = ref([])
const inventory = ref([])
const loading = ref(true)

// Dynamically import all card images
const cardImageFiles = import.meta.glob('@/assets/Images/Cards/*.png', { eager: true })

function getCardImage(description) {
  const lowerDesc = description.toLowerCase()
  if (lowerDesc.includes('mystery') || lowerDesc.includes('booster')) {
    const boosterKey = Object.keys(cardImageFiles).find(k => k.toLowerCase().endsWith('booster.png'))
    if (boosterKey) return cardImageFiles[boosterKey].default
  }
  for (const [path, mod] of Object.entries(cardImageFiles)) {
    const fileName = path.split('/').pop().replace('.png', '')
    if (fileName === description || fileName === description.replace(/\./g, '')) return mod.default
  }
  const blankKey = Object.keys(cardImageFiles).find(k => k.endsWith('Blank.png'))
  return blankKey ? cardImageFiles[blankKey].default : null
}

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

const isCard = computed(() => productType.value === 'card')

// Find the product from the catalog by DESCRIPTION
const catalogProduct = computed(() => {
  if (!isCard.value) return null
  return products.value.find(p => p.DESCRIPTION === productId.value) || null
})

// Inventory listings for this product (by PRODUCT_NAME, only items with stock)
const productListings = computed(() => {
  if (!isCard.value) return []
  return inventory.value.filter(i =>
    i.PRODUCT_NAME === productId.value &&
    i.QUANTITY_AVAILABLE && i.QUANTITY_AVAILABLE > 0
  )
})

// Detect booster / mystery products (sold by the company, no variant dropdowns)
const isBooster = computed(() => {
  const name = (productId.value || '').toLowerCase()
  return name.includes('mystery') || name.includes('booster')
})

// Hardcoded filter options
const LANGUAGE_OPTIONS = ['English', 'Japanese', 'Korean', 'Australian', 'Spanish']
const FOIL_OPTIONS = ['Non-Foil', 'Holofoil', 'Reverse Holofoil']
const CONDITION_OPTIONS = ['Mint', 'Near-Mint', 'Light Play', 'Moderate Play']

const selectedLanguage = ref('')
const selectedCondition = ref('')
const selectedFoil = ref('')

watch(productId, () => {
  selectedLanguage.value = ''
  selectedCondition.value = ''
  selectedFoil.value = ''
})

const filteredListings = computed(() => {
  return productListings.value.filter(i => {
    const name = (i.MODIFIER_NAME || '').toLowerCase()
    if (selectedLanguage.value && !name.includes(selectedLanguage.value.toLowerCase())) return false
    if (selectedCondition.value && !name.includes(selectedCondition.value.toLowerCase())) return false
    if (selectedFoil.value && !name.includes(selectedFoil.value.toLowerCase())) return false
    return true
  })
})

// Product display info
const currentProduct = computed(() => {
  if (!isCard.value || loading.value) return null
  // Try catalog first
  if (catalogProduct.value) {
    return {
      name: catalogProduct.value.DESCRIPTION,
      sku: catalogProduct.value['1'],
      price: (catalogProduct.value.BASE_PRICE_CENTS / 100).toFixed(2),
      image: getCardImage(catalogProduct.value.DESCRIPTION),
    }
  }
  // Fallback: product exists in inventory but not in catalog (mystery/booster)
  if (productListings.value.length) {
    const first = productListings.value[0]
    return {
      name: first.PRODUCT_NAME,
      sku: first.SKU,
      price: (first.BASE_PRICE_CENTS / 100).toFixed(2),
      image: getCardImage(first.PRODUCT_NAME),
    }
  }
  return null
})

// Add to cart handler
const cartQuantities = ref({})
const showCartPrompt = ref(false)

function getCartQty(listing) {
  return cartQuantities.value[listing.INVENTORY_ID] || 1
}

function setCartQty(listing, val) {
  cartQuantities.value[listing.INVENTORY_ID] = Math.max(1, Math.min(val, listing.QUANTITY_AVAILABLE))
}

async function handleAddToCart(listing) {
  const qty = getCartQty(listing)
  try {
    await addToCart(
      listing.INVENTORY_ID,
      qty,
      listing.UNIT_PRICE_CENTS,
      listing.CURRENCY_CODE || 'USD'
    )
    showCartPrompt.value = true
  } catch (e) {
    alert(e.message || 'Failed to add to cart')
  }
}
</script>

<template>
  <main class="page-shell product-page">
    <router-link to="/store" class="back-link">← Back to Store</router-link>

    <p v-if="loading" class="empty-state">Loading product…</p>

    <div v-else-if="currentProduct" class="product-container">
      <div class="product-image-section">
        <div class="product-image-large">
          <img :src="currentProduct.image" :alt="currentProduct.name" class="product-img" />
        </div>
      </div>

      <div class="product-details">
        <h1>{{ currentProduct.name }}</h1>
        <p class="description">Base Price: ${{ currentProduct.price }}</p>

        <!-- Booster / Mystery packs: company sells directly, no variants -->
        <template v-if="isBooster">
          <h2 class="section-heading">Buy</h2>
          <div v-if="productListings.length" class="booster-listings">
            <div v-for="listing in productListings" :key="listing.INVENTORY_ID" class="booster-row">
              <span>{{ listing.QUANTITY_AVAILABLE }} in stock</span>
              <span class="listing-price">${{ (listing.UNIT_PRICE_CENTS / 100).toFixed(2) }}</span>
              <input
                type="number"
                class="qty-input"
                :value="getCartQty(listing)"
                @input="setCartQty(listing, +$event.target.value)"
                min="1"
                :max="listing.QUANTITY_AVAILABLE"
              />
              <button class="action-btn listing-buy-btn" @click="handleAddToCart(listing)">Buy</button>
            </div>
          </div>
          <p v-else class="text-muted">Currently out of stock.</p>
        </template>

        <!-- Cards: Language / Condition / Foil filter dropdowns -->
        <template v-else>
          <div class="filters">
            <div class="filter-group">
              <label>Language</label>
              <select v-model="selectedLanguage">
                <option value="">All</option>
                <option v-for="l in LANGUAGE_OPTIONS" :key="l" :value="l">{{ l }}</option>
              </select>
            </div>
            <div class="filter-group">
              <label>Foil</label>
              <select v-model="selectedFoil">
                <option value="">All</option>
                <option v-for="f in FOIL_OPTIONS" :key="f" :value="f">{{ f }}</option>
              </select>
            </div>
            <div class="filter-group">
              <label>Condition</label>
              <select v-model="selectedCondition">
                <option value="">All</option>
                <option v-for="c in CONDITION_OPTIONS" :key="c" :value="c">{{ c }}</option>
              </select>
            </div>
          </div>

          <!-- Seller listings table -->
          <h2 class="section-heading">Listings ({{ filteredListings.length }})</h2>

          <div v-if="filteredListings.length" class="seller-listings">
            <div class="listing-header">
              <span>Seller</span>
              <span>Variant</span>
              <span>Stock</span>
              <span>Price</span>
              <span>Qty</span>
              <span></span>
            </div>
            <div v-for="listing in filteredListings" :key="listing.INVENTORY_ID" class="listing-row">
              <span class="listing-seller">Seller #{{ listing.SELLER_ID }}</span>
              <span>{{ listing.MODIFIER_NAME }}</span>
              <span>{{ listing.QUANTITY_AVAILABLE }}</span>
              <span class="listing-price">${{ (listing.UNIT_PRICE_CENTS / 100).toFixed(2) }}</span>
              <span>
                <input
                  type="number"
                  class="qty-input"
                  :value="getCartQty(listing)"
                  @input="setCartQty(listing, +$event.target.value)"
                  min="1"
                  :max="listing.QUANTITY_AVAILABLE"
                />
              </span>
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

    <!-- Cart prompt overlay -->
    <div v-if="showCartPrompt" class="modal-overlay" @click="showCartPrompt = false">
      <div class="cart-prompt" @click.stop>
        <h3>Added to cart!</h3>
        <div class="cart-prompt-actions">
          <router-link to="/cart" class="action-btn">Go to Cart</router-link>
          <button class="action-btn cart-prompt-continue" @click="showCartPrompt = false">Continue Shopping</button>
        </div>
      </div>
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

.qty-input {
  width: 60px;
  padding: 4px 6px;
  text-align: center;
  border-radius: 4px;
  border: 1px solid var(--color-border, #333);
  background: var(--color-background, #111);
  color: var(--color-text, #fff);
}

.filters {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  margin-bottom: 1.5rem;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.filter-group label {
  font-size: 0.85rem;
  color: var(--color-text-muted, #aaa);
}

.filter-group select {
  padding: 6px 10px;
  border-radius: 4px;
  border: 1px solid var(--color-border, #333);
  background: var(--color-background-soft, #1a1a2e);
  color: var(--color-text, #fff);
}

.booster-listings {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.booster-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem;
  background: var(--color-background-soft, #1a1a2e);
  border-radius: 8px;
  border: 1px solid var(--color-border, #333);
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.cart-prompt {
  background: var(--color-background, #111);
  border: 1px solid var(--color-border, #333);
  border-radius: 12px;
  padding: 2rem;
  text-align: center;
  min-width: 300px;
}

.cart-prompt h3 {
  margin: 0 0 1.25rem;
  color: #4caf50;
}

.cart-prompt-actions {
  display: flex;
  justify-content: center;
  gap: 1rem;
}

.cart-prompt-continue {
  background: var(--color-background-soft, #1a1a2e) !important;
  border: 1px solid var(--color-border, #333) !important;
}
</style>
