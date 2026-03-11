<script setup>
import { ref, computed } from 'vue'
import { prices, cardPriceModifiers } from '@/utils/prices.js'
import { generatedCards } from '@/utils/generateCards.js'

const sealedProducts = [
  { id: 'pack', name: 'Booster Pack', type: 'pack', price: prices[0].pack, description: '10 random cards per pack', image: '📦' },
  { id: 'bundle', name: 'Bundle', type: 'bundle', price: prices[0].bundle, description: '6 packs per bundle', image: '🎁' },
  { id: 'box', name: 'Booster Box', type: 'box', price: prices[0].box, description: '15 packs per box', image: '📦' },
]

// Unique card names by type
const uniqueNames = (type) => [...new Set(
  generatedCards.filter(c => !type || c.type === type).map(c => c.name)
)]

const allCardNames      = computed(() => uniqueNames(null))
const characterNames    = computed(() => uniqueNames('character'))
const artifactNames     = computed(() => uniqueNames('artifact'))
const landNames         = computed(() => uniqueNames('lands'))

// Bargain Bin: Lightplay or Moderate Play cards with stock > 0
const bargainCards = computed(() =>
  generatedCards.filter(c =>
    (c.condition === 'Lightplay' || c.condition === 'Moderate Play') && c.rarity === 'Common' && c.foil === "Non-foil" && c.stock > 0
  )
)

// Rare Finds: Mint + any foil type (not Non-foil) with stock > 0
const rareFinds = computed(() =>
  generatedCards.filter(c =>
    c.condition === 'Mint' && c.foil !== 'Non-foil' && c.stock > 0 && (c.rarity === 'Rare' || c.rarity === 'Super Rare')
  )
)

// Search
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
</script>

<template>
  <main class="page-shell">
    <h1 class="page-title">Store</h1>

    <!-- Search bar -->
    <div class="search-wrapper">
      <input
        v-model="searchQuery"
        class="search-input"
        type="text"
        placeholder="Search for a card…"
      />
      <div v-if="searchResults.length" class="search-results">
        <router-link
          v-for="card in searchResults" :key="card.name"
          :to="{ name: 'product', params: { type: 'card', id: card.name } }"
          @click="clearSearch"
        >
          {{ card.name }}
        </router-link>
      </div>
    </div>

    <!-- Sealed / Booster products -->
    <section class="product-section">
      <h2 class="section-heading">Booster Products</h2>
      <div class="product-grid">
        <router-link
          v-for="p in sealedProducts" :key="p.id"
          :to="{ name: 'product', params: { type: p.type, id: p.id } }"
          class="product-card"
        >
          <div class="product-image">{{ p.image }}</div>
          <h3>{{ p.name }}</h3>
          <p class="product-description">{{ p.description }}</p>
          <p class="product-price">{{ p.price }}</p>
        </router-link>
      </div>
    </section>

    <!-- All Cards -->
    <section class="product-section">
      <h2 class="section-heading">All Cards</h2>
      <div class="product-grid product-grid--scroll">
        <router-link
          v-for="name in allCardNames" :key="name"
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
        <router-link
          v-for="name in characterNames" :key="name"
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
        <router-link
          v-for="name in artifactNames" :key="name"
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
        <router-link
          v-for="name in landNames" :key="name"
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
        <router-link
          v-for="card in bargainCards" :key="card.id"
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
        <router-link
          v-for="card in rareFinds" :key="card.id"
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
  </main>
</template>

<style scoped>
.product-section {
  margin-bottom: 3rem;
}
</style>
