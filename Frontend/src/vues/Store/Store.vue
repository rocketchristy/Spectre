<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getProducts, getInventory, addInventoryItem, getModifiers } from '@/utils/api.js'
import { getCardImage } from '@/utils/cardImages.js'
import { getRandomAd, getRandomAdPair } from '@/utils/ads.js'
import { getRandomAdRow } from '@/utils/adRows.js'

const router = useRouter()
const [randomAd, randomAd2] = getRandomAdPair()
const adRow = getRandomAdRow()

const rowRefs = {}
function scrollRow(key, dir) {
  const el = rowRefs[key]
  if (el) el.scrollBy({ left: dir * 300, behavior: 'smooth' })
}

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

const suggestedPrice = ref(null)

function openSellModal() {
  sellForm.value = { productSku: '', language: '', condition: '', foil: '', quantity: 1, price: '' }
  sellError.value = ''
  suggestedPrice.value = null
  showSellModal.value = true
}
function closeSellModal() { showSellModal.value = false }

// Watch for card + all modifiers selected, then suggest a price
watch(
  () => [sellForm.value.productSku, sellForm.value.language, sellForm.value.foil, sellForm.value.condition],
  async ([sku, lang, foil, cond]) => {
    if (!sku || !lang || !foil || !cond) {
      suggestedPrice.value = null
      return
    }
    const product = products.value.find(p => p['1'] === sku)
    if (!product) return
    try {
      const modifiers = await getModifiers('C')
      const code = lang + foil + cond
      const match = modifiers.find(m => m.MODIFIER_CODE === code)
      if (match) {
        const cents = product.BASE_PRICE_CENTS * parseFloat(match.PRICE_MULTIPLIER)
        const suggested = (cents / 100).toFixed(2)
        suggestedPrice.value = suggested
        sellForm.value.price = suggested
      } else {
        suggestedPrice.value = null
      }
    } catch {
      suggestedPrice.value = null
    }
  }
)

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
  <div class="page-with-ad">
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

      <!-- Ad row banner -->
      <div v-if="adRow" class="ad-row-banner">
        <video v-if="adRow.isVideo" :src="adRow.src" autoplay loop muted playsinline class="ad-row-media" />
        <img v-else :src="adRow.src" alt="Advertisement" class="ad-row-media" />
      </div>

      <!-- Inventory grouped by Style (packs) -->
      <div v-for="[styleName, items] in styleGroups" :key="styleName">
        <section class="product-section">
          <h2 class="section-heading">{{ styleName }}</h2>
          <div class="scroll-row-wrapper">
            <button class="scroll-btn" @click="scrollRow(styleName, -1)">&#9664;</button>
            <div class="product-grid product-grid--scroll" :ref="el => { if (el) rowRefs[styleName] = el }">
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
                <span class="card-view-btn">View</span>
              </router-link>
            </div>
            <button class="scroll-btn" @click="scrollRow(styleName, 1)">&#9654;</button>
          </div>
        </section>
      </div>

      <!-- All Cards from Products Catalog -->
      <section class="product-section">
        <h2 class="section-heading">All Cards</h2>
        <div class="scroll-row-wrapper">
          <button class="scroll-btn" @click="scrollRow('all-cards', -1)">&#9664;</button>
          <div class="product-grid product-grid--scroll" :ref="el => { if (el) rowRefs['all-cards'] = el }">
            <router-link v-for="card in productCards" :key="card.sku"
              :to="{ name: 'product', params: { type: 'card', id: card.name } }"
              class="product-card product-card--sm"
            >
              <div class="product-image">
                <img :src="card.image" :alt="card.name" class="card-img" />
              </div>
              <h3>{{ card.name }}</h3>
              <p class="product-price">From ${{ card.price }}</p>
              <span class="card-view-btn">View</span>
            </router-link>
          </div>
          <button class="scroll-btn" @click="scrollRow('all-cards', 1)">&#9654;</button>
        </div>
      </section>

      <!-- Bargain Bin -->
      <section v-if="bargainCards.length" class="product-section">
        <h2 class="section-heading">Bargain Bin</h2>
        <p class="text-muted" style="margin-bottom:1rem">Cards under $1</p>
        <div class="scroll-row-wrapper">
          <button class="scroll-btn" @click="scrollRow('bargain', -1)">&#9664;</button>
          <div class="product-grid product-grid--scroll" :ref="el => { if (el) rowRefs['bargain'] = el }">
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
              <span class="card-view-btn">View</span>
            </router-link>
          </div>
          <button class="scroll-btn" @click="scrollRow('bargain', 1)">&#9654;</button>
        </div>
      </section>

      <!-- Rare Finds -->
      <section v-if="rareFinds.length" class="product-section">
        <h2 class="section-heading">Rare Finds</h2>
        <p class="text-muted" style="margin-bottom:1rem">Cards over $10</p>
        <div class="scroll-row-wrapper">
          <button class="scroll-btn" @click="scrollRow('rare', -1)">&#9664;</button>
          <div class="product-grid product-grid--scroll" :ref="el => { if (el) rowRefs['rare'] = el }">
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
              <span class="card-view-btn">View</span>
            </router-link>
          </div>
          <button class="scroll-btn" @click="scrollRow('rare', 1)">&#9654;</button>
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
              <p v-if="suggestedPrice" class="suggested-price">Suggested: ${{ suggestedPrice }}</p>
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
  <div class="store-ads-col">
    <aside class="store-ad-item">
      <img :src="randomAd" alt="Ad" />
    </aside>
    <aside class="store-ad-item">
      <img :src="randomAd2" alt="Ad" />
    </aside>
  </div>
  </div>
</template>

<style scoped>
/* Two-ad sidebar layout */
.page-with-ad {
  display: flex;
  gap: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
  align-items: stretch;
}
.page-shell {
  flex: 1;
  min-width: 0;
  padding: 2rem;
}
.store-ads-col {
  width: 180px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  position: sticky;
  top: 0;
  height: 100vh;
  align-self: flex-start;
  padding: 2rem 0;
}
.store-ad-item img {
  width: 100%;
  height: 45vh;
  object-fit: fill;
  border: 3px solid var(--shadow);
  box-shadow: 4px 4px 0 var(--shadow);
  display: block;
}
@media (max-width: 900px) { .store-ads-col { display: none; } }

/* Scroll row with ◀ ▶ buttons */
.scroll-row-wrapper {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.scroll-btn {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  background: var(--water);
  color: #fff;
  border: 3px solid var(--shadow);
  box-shadow: 3px 3px 0 var(--shadow);
  font-size: 1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
}
.scroll-btn:hover { background: var(--shadow); color: #000; }
.scroll-row-wrapper .product-grid--scroll { flex: 1; min-width: 0; }

.card-img {
  width: 100%;
  max-width: 120px;
  height: auto;
}
.product-stock {
  font-size: 0.85rem;
  color: var(--ice);
  font-family: var(--font-head);
  letter-spacing: 1px;
}
.product-description {
  font-size: 0.82rem;
  color: var(--shadow);
  font-weight: bold;
}

/* view button on each card */
.card-view-btn {
  display: block;
  width: 100%;
  margin-top: 0.5rem;
  padding: 0.35rem 0;
  background: var(--water);
  color: #fff;
  border: 2px solid rgba(255,255,255,0.4);
  font-family: var(--font-head);
  font-size: 0.75rem;
  letter-spacing: 2px;
  text-transform: uppercase;
  cursor: pointer;
  pointer-events: none; /* card link handles click */
  text-align: center;
  box-shadow: 2px 2px 0 var(--shadow);
}

.ad-row-banner {
  margin: 1.5rem 0;
  border: 3px solid var(--water);
  box-shadow: 4px 4px 0 var(--water);
  overflow: hidden;
}
.ad-row-media {
  display: block;
  width: 100%;
  height: auto;
}

.suggested-price {
  margin-top: 0.25rem;
  font-size: 0.85rem;
  color: var(--grass);
  font-style: italic;
}
</style>
