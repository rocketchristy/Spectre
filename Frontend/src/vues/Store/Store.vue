<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getProducts, getInventory, addInventoryItem } from '@/utils/api.js'

const router = useRouter()
const products = ref([])
const inventory = ref([])
const loading = ref(true)

// Dynamically import all card images
const cardImageFiles = import.meta.glob('@/assets/Images/Cards/*.png', { eager: true })

function getCardImage(description) {
  // Check if this is a booster/mystery product
  const lowerDesc = description.toLowerCase()
  if (lowerDesc.includes('mystery') || lowerDesc.includes('booster')) {
    const boosterKey = Object.keys(cardImageFiles).find(k => k.toLowerCase().endsWith('booster.png'))
    if (boosterKey) return cardImageFiles[boosterKey].default
  }
  // Try to find exact match by description
  for (const [path, mod] of Object.entries(cardImageFiles)) {
    const fileName = path.split('/').pop().replace('.png', '')
    if (fileName === description) return mod.default
  }
  // Fallback to Blank
  const blankKey = Object.keys(cardImageFiles).find(k => k.endsWith('Blank.png'))
  return blankKey ? cardImageFiles[blankKey].default : null
}

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

// Products from API: { "1": sku, "BASE_PRICE_CENTS": number, "DESCRIPTION": name }
const productCards = computed(() =>
  products.value.map(p => ({
    sku: p['1'],
    name: p.DESCRIPTION,
    price: (p.BASE_PRICE_CENTS / 100).toFixed(2),
    image: getCardImage(p.DESCRIPTION),
  }))
)

// Inventory items with stock, enriched with images
const inventoryCards = computed(() =>
  inventory.value
    .filter(i => i.QUANTITY_AVAILABLE && i.QUANTITY_AVAILABLE > 0)
    .map(i => ({
      ...i,
      image: getCardImage(i.PRODUCT_NAME),
    }))
)

// Group inventory by STYLE_NAME, with aggregate stock per product
const styleGroups = computed(() => {
  const groups = new Map()
  for (const i of inventoryCards.value) {
    const style = i.STYLE_NAME || 'Other'
    if (style === 'Card Single') continue
    if (!groups.has(style)) groups.set(style, new Map())
    const prodMap = groups.get(style)
    if (!prodMap.has(i.PRODUCT_NAME)) {
      prodMap.set(i.PRODUCT_NAME, { ...i, totalStock: 0 })
    }
    prodMap.get(i.PRODUCT_NAME).totalStock += i.QUANTITY_AVAILABLE || 0
  }
  // Convert inner maps to arrays and sort: Mystery Single > Mystery Midi > Mystery Pack > rest
  const STYLE_ORDER = ['Mystery Single', 'Mystery Midi', 'Mystery Pack']
  const result = new Map()
  const sortedKeys = [...groups.keys()].sort((a, b) => {
    const ai = STYLE_ORDER.indexOf(a)
    const bi = STYLE_ORDER.indexOf(b)
    if (ai !== -1 && bi !== -1) return ai - bi
    if (ai !== -1) return -1
    if (bi !== -1) return 1
    return a.localeCompare(b)
  })
  for (const style of sortedKeys) {
    result.set(style, [...groups.get(style).values()])
  }
  return result
})

// Helper to check if an item is a specific card (not a booster/mystery)
function isSpecificCard(item) {
  const style = (item.STYLE_NAME || '').toLowerCase()
  const name = (item.PRODUCT_NAME || '').toLowerCase()
  return !style.includes('mystery') && !style.includes('booster') &&
         !name.includes('mystery') && !name.includes('booster')
}

// Bargain Bin: specific cards under $1
const bargainCards = computed(() => {
  const sorted = [...inventoryCards.value]
    .filter(i => isSpecificCard(i) && i.UNIT_PRICE_CENTS < 100)
    .sort((a, b) => a.UNIT_PRICE_CENTS - b.UNIT_PRICE_CENTS)
  const seen = new Set()
  return sorted.filter(i => {
    if (seen.has(i.PRODUCT_NAME)) return false
    seen.add(i.PRODUCT_NAME)
    return true
  }).slice(0, 12)
})

// Rare Finds: specific cards over $10
const rareFinds = computed(() => {
  const sorted = [...inventoryCards.value]
    .filter(i => isSpecificCard(i) && i.UNIT_PRICE_CENTS > 1000)
    .sort((a, b) => b.UNIT_PRICE_CENTS - a.UNIT_PRICE_CENTS)
  const seen = new Set()
  return sorted.filter(i => {
    if (seen.has(i.PRODUCT_NAME)) return false
    seen.add(i.PRODUCT_NAME)
    return true
  }).slice(0, 12)
})

// Search across products
const searchQuery = ref('')
const searchResults = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return []
  return productCards.value
    .filter(p => p.name.toLowerCase().includes(q))
    .slice(0, 12)
})
function clearSearch() { searchQuery.value = '' }

// Sell a Card modal
const showSellModal = ref(false)
const sellForm = ref({ productSku: '', language: '', condition: '', foil: '', quantity: 1, price: '' })
const sellError = ref('')

// Hardcoded variant options with 1-char codes for modifier building
// SKU modifier order: Language + Foil + Condition
const LANGUAGE_OPTIONS = [
  { label: 'English', code: 'E' },
  { label: 'Japanese', code: 'J' },
  { label: 'Korean', code: 'K' },
  { label: 'Australian', code: 'A' },
  { label: 'Spanish', code: 'S' },
]
const FOIL_OPTIONS = [
  { label: 'Non-Foil', code: 'N' },
  { label: 'Holofoil', code: 'H' },
  { label: 'Reverse Holofoil', code: 'R' },
]
const CONDITION_OPTIONS = [
  { label: 'Mint', code: 'M' },
  { label: 'Near-Mint', code: 'N' },
  { label: 'Light Play', code: 'L' },
  { label: 'Moderate Play', code: 'P' },
]

function openSellModal() {
  sellForm.value = { productSku: '', language: '', condition: '', foil: '', quantity: 1, price: '' }
  sellError.value = ''
  showSellModal.value = true
}
function closeSellModal() { showSellModal.value = false }

// Build modifier code (3 chars) from the 3 dropdown selections
// Order: Language + Foil + Condition
const sellModifierCode = computed(() => {
  return sellForm.value.language + sellForm.value.foil + sellForm.value.condition
})

// Computed full SKU: base(10) + modifier(3) = 13 chars
const sellFullSku = computed(() => {
  const base = sellForm.value.productSku
  if (!base) return ''
  return base + sellModifierCode.value
})

async function submitSell() {
  if (!sellForm.value.productSku) {
    sellError.value = 'Please select a card.'
    return
  }
  if (!sellForm.value.language || !sellForm.value.condition || !sellForm.value.foil) {
    sellError.value = 'Please select language, condition, and foil.'
    return
  }
  const price = parseFloat(sellForm.value.price)
  if (!price || price <= 0) {
    sellError.value = 'Please enter a valid price.'
    return
  }
  const quantity = parseInt(sellForm.value.quantity) || 1
  try {
    await addInventoryItem(sellFullSku.value, quantity, Math.round(price * 100), 'USD')
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
            v-for="card in searchResults" :key="card.sku"
            :to="{ name: 'product', params: { type: 'card', id: card.name } }"
            @click="clearSearch"
          >{{ card.name }}</router-link>
        </div>
      </div>

      <!-- Inventory grouped by Style (packs) -->
      <section v-for="[styleName, items] in styleGroups" :key="styleName" class="product-section">
        <h2 class="section-heading">{{ styleName }}</h2>
        <div class="product-grid product-grid--scroll">
          <router-link v-for="item in items" :key="item.SKU + '-' + item.INVENTORY_ID"
            :to="{ name: 'product', params: { type: 'card', id: item.PRODUCT_NAME } }"
            class="product-card product-card--sm"
          >
            <div class="product-image">
              <img :src="item.image" :alt="item.PRODUCT_NAME" class="card-img" />
            </div>
            <h3>{{ item.PRODUCT_NAME }}</h3>
            <p class="product-description">{{ item.MODIFIER_NAME }}</p>
            <p class="product-price">${{ (item.UNIT_PRICE_CENTS / 100).toFixed(2) }}</p>
            <p class="product-stock">{{ item.totalStock }} in stock</p>
          </router-link>
        </div>
      </section>

      <!-- All Cards from Products Catalog -->
      <section class="product-section">
        <h2 class="section-heading">All Cards</h2>
        <div class="product-grid product-grid--scroll">
          <router-link v-for="card in productCards" :key="card.sku"
            :to="{ name: 'product', params: { type: 'card', id: card.name } }"
            class="product-card product-card--sm"
          >
            <div class="product-image">
              <img :src="card.image" :alt="card.name" class="card-img" />
            </div>
            <h3>{{ card.name }}</h3>
            <p class="product-price">From ${{ card.price }}</p>
          </router-link>
        </div>
      </section>

      <!-- Bargain Bin -->
      <section v-if="bargainCards.length" class="product-section">
        <h2 class="section-heading">Bargain Bin</h2>
        <p class="text-muted" style="margin-bottom:1rem">Cards under $1</p>
        <div class="product-grid product-grid--scroll">
          <router-link v-for="card in bargainCards" :key="card.SKU + '-' + card.INVENTORY_ID"
            :to="{ name: 'product', params: { type: 'card', id: card.PRODUCT_NAME } }"
            class="product-card product-card--sm"
          >
            <div class="product-image">
              <img :src="card.image" :alt="card.PRODUCT_NAME" class="card-img" />
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
        <p class="text-muted" style="margin-bottom:1rem">Cards over $10</p>
        <div class="product-grid product-grid--scroll">
          <router-link v-for="card in rareFinds" :key="card.SKU + '-' + card.INVENTORY_ID"
            :to="{ name: 'product', params: { type: 'card', id: card.PRODUCT_NAME } }"
            class="product-card product-card--sm"
          >
            <div class="product-image">
              <img :src="card.image" :alt="card.PRODUCT_NAME" class="card-img" />
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
              <label class="form-label">Card</label>
              <select v-model="sellForm.productSku" class="form-input">
                <option value="">Select a card…</option>
                <option v-for="p in productCards" :key="p.sku" :value="p.sku">{{ p.name }}</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Language</label>
              <select v-model="sellForm.language" class="form-input">
                <option value="">Select language…</option>
                <option v-for="l in LANGUAGE_OPTIONS" :key="l.code" :value="l.code">{{ l.label }}</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Foil</label>
              <select v-model="sellForm.foil" class="form-input">
                <option value="">Select foil type…</option>
                <option v-for="f in FOIL_OPTIONS" :key="f.code" :value="f.code">{{ f.label }}</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Condition</label>
              <select v-model="sellForm.condition" class="form-input">
                <option value="">Select condition…</option>
                <option v-for="c in CONDITION_OPTIONS" :key="c.code" :value="c.code">{{ c.label }}</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Quantity</label>
              <input v-model.number="sellForm.quantity" type="number" min="1" class="form-input" placeholder="1" />
            </div>
            <div class="form-group">
              <label class="form-label">Your Price ($)</label>
              <input v-model="sellForm.price" type="number" step="0.01" min="0.01" class="form-input" placeholder="Enter price" />
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
.product-stock {
  font-size: 0.8rem;
  color: var(--color-text-muted, #888);
}
</style>
