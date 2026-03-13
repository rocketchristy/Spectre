<script setup>
import { ref, computed } from 'vue'
import { prices, cardPriceModifiers, elements, elementEmoji, mysteryProductTypes } from '@/utils/prices.js'
import { generatedCards, getTemplateForName, calculatePrice } from '@/utils/generateCards.js'
import { addListing } from '@/utils/listings.js'
import { tempCardData } from '@/utils/tempCard.js'

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

// ---------- Card names by type ----------
const uniqueNames = (type) => [...new Set(
  generatedCards.filter(c => !type || c.type === type).map(c => c.name)
)]
const allCardNames   = computed(() => uniqueNames(null))
const characterNames = computed(() => uniqueNames('character'))
const artifactNames  = computed(() => uniqueNames('artifact'))
const landNames      = computed(() => uniqueNames('lands'))

// ---------- Bargain Bin / Rare Finds ----------
const bargainCards = computed(() =>
  generatedCards.filter(c =>
    (c.condition === 'Lightplay' || c.condition === 'Moderate Play') &&
    c.rarity === 'Common' && c.foil === 'Non-foil' && c.stock > 0
  )
)
const rareFinds = computed(() =>
  generatedCards.filter(c =>
    c.condition === 'Mint' && c.foil !== 'Non-foil' && c.stock > 0 &&
    (c.rarity === 'Rare' || c.rarity === 'Super Rare')
  )
)

// ---------- Search ----------
const searchQuery = ref('')
const searchResults = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return []
  const seen = new Set()
  return generatedCards
    .filter(c => {
      if (seen.has(c.name)) return false
      if (c.name.toLowerCase().includes(q)) { seen.add(c.name); return true }
      return false
    })
    .slice(0, 12)
})
function clearSearch() { searchQuery.value = '' }

// ---------- Sell a Card modal ----------
const showSellModal = ref(false)

const allNames = computed(() => [...new Set(generatedCards.map(c => c.name))].sort())
const allConditions = ['Mint', 'Near Mint', 'Lightplay', 'Moderate Play']
const allFoils = ['Non-foil', 'Holofoil', 'Reverse Holofoil']
const allLanguages = ['english', 'japanese', 'australian']

const sellForm = ref({ name: '', condition: '', foil: '', language: '' })
const sellPrice = ref('')
const sellError = ref('')

const selectedTemplate = computed(() => {
  if (!sellForm.value.name) return null
  return getTemplateForName(sellForm.value.name)
})

const suggestedPrice = computed(() => {
  const f = sellForm.value
  if (!f.name || !f.condition || !f.foil || !f.language) return null
  const t = selectedTemplate.value
  if (!t) return null
  return calculatePrice({
    condition: f.condition,
    foil: f.foil,
    language: f.language,
    rarity: 'Common', // base suggestion
    type: t.type,
  })
})

function openSellModal() {
  sellForm.value = { name: '', condition: '', foil: '', language: '' }
  sellPrice.value = ''
  sellError.value = ''
  showSellModal.value = true
}

function closeSellModal() { showSellModal.value = false }

function submitSell() {
  const f = sellForm.value
  if (!f.name || !f.condition || !f.foil || !f.language) {
    sellError.value = 'Please fill in all fields.'
    return
  }
  const price = parseFloat(sellPrice.value || suggestedPrice.value)
  if (!price || price <= 0) {
    sellError.value = 'Please enter a valid price.'
    return
  }
  const t = selectedTemplate.value
  addListing({
    name: f.name,
    condition: f.condition,
    foil: f.foil,
    language: f.language,
    rarity: 'Common',
    type: t ? t.type : 'character',
    price: price.toFixed(2),
  })
  showSellModal.value = false
}
</script>

<template>
  <main class="page-shell">
    <h1 class="page-title">Store</h1>

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
        <router-link v-for="name in allCardNames" :key="name"
          :to="{ name: 'product', params: { type: 'card', id: name } }"
          class="product-card product-card--sm"
        >
          <div class="product-image">🃏</div>
          <h3>{{ name }}</h3>
        </router-link>
      </div>
    </section>

    <!-- Character Cards -->
    <section class="product-section">
      <h2 class="section-heading">Character Cards</h2>
      <div class="product-grid product-grid--scroll">
        <router-link v-for="name in characterNames" :key="name"
          :to="{ name: 'product', params: { type: 'card', id: name } }"
          class="product-card product-card--sm"
        >
          <div class="product-image">🃏</div>
          <h3>{{ name }}</h3>
        </router-link>
      </div>
    </section>

    <!-- Artifact Cards -->
    <section class="product-section">
      <h2 class="section-heading">Artifact Cards</h2>
      <div class="product-grid product-grid--scroll">
        <router-link v-for="name in artifactNames" :key="name"
          :to="{ name: 'product', params: { type: 'card', id: name } }"
          class="product-card product-card--sm"
        >
          <div class="product-image">🃏</div>
          <h3>{{ name }}</h3>
        </router-link>
      </div>
    </section>

    <!-- Land Cards -->
    <section class="product-section">
      <h2 class="section-heading">Land Cards</h2>
      <div class="product-grid product-grid--scroll">
        <router-link v-for="name in landNames" :key="name"
          :to="{ name: 'product', params: { type: 'card', id: name } }"
          class="product-card product-card--sm"
        >
          <div class="product-image">🃏</div>
          <h3>{{ name }}</h3>
        </router-link>
      </div>
    </section>

    <!-- Bargain Bin -->
    <section class="product-section">
      <h2 class="section-heading">Bargain Bin</h2>
      <p class="text-muted" style="margin-bottom:1rem">Lightplay &amp; Moderate Play cards at a discount</p>
      <div class="product-grid product-grid--scroll">
        <router-link v-for="card in bargainCards" :key="card.id"
          :to="{ name: 'product', params: { type: 'card', id: card.name } }"
          class="product-card product-card--sm"
        >
          <div class="product-image">🃏</div>
          <h3>{{ card.name }}</h3>
          <p class="product-description">{{ card.condition }} · {{ card.foil }}</p>
          <p class="product-price">${{ card.price }}</p>
        </router-link>
      </div>
    </section>

    <!-- Rare Finds -->
    <section class="product-section">
      <h2 class="section-heading">Rare Finds</h2>
      <p class="text-muted" style="margin-bottom:1rem">Mint condition foil cards</p>
      <div class="product-grid product-grid--scroll">
        <router-link v-for="card in rareFinds" :key="card.id"
          :to="{ name: 'product', params: { type: 'card', id: card.name } }"
          class="product-card product-card--sm"
        >
          <div class="product-image">🃏</div>
          <h3>{{ card.name }}</h3>
          <p class="product-description">{{ card.rarity }} · {{ card.foil }}</p>
          <p class="product-price">${{ card.price }}</p>
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
            <select v-model="sellForm.name" class="form-input">
              <option value="">Select a card…</option>
              <option v-for="n in allNames" :key="n" :value="n">{{ n }}</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Condition</label>
            <select v-model="sellForm.condition" class="form-input">
              <option value="">Select condition…</option>
              <option v-for="c in allConditions" :key="c" :value="c">{{ c }}</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Foil</label>
            <select v-model="sellForm.foil" class="form-input">
              <option value="">Select foil type…</option>
              <option v-for="f in allFoils" :key="f" :value="f">{{ f }}</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Language</label>
            <select v-model="sellForm.language" class="form-input">
              <option value="">Select language…</option>
              <option v-for="l in allLanguages" :key="l" :value="l">{{ l }}</option>
            </select>
          </div>
          <div v-if="suggestedPrice" class="form-group">
            <label class="form-label">Suggested Price</label>
            <p class="suggested-price">${{ suggestedPrice }}</p>
          </div>
          <div class="form-group">
            <label class="form-label">Your Price ($)</label>
            <input v-model="sellPrice" type="number" step="0.01" min="0.01" class="form-input"
              :placeholder="suggestedPrice ? suggestedPrice : 'Enter price'" />
          </div>
          <p v-if="sellError" class="modal-error">{{ sellError }}</p>
          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="closeSellModal">Cancel</button>
            <button type="submit" class="btn btn-primary">List for Sale</button>
          </div>
        </form>
      </div>
    </div>
  </main>
</template>

<style scoped>
.product-section {
  margin-bottom: 3rem;
}
</style>
