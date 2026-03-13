<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { prices, cardPriceModifiers, mysteryProductTypes, elementEmoji } from '@/utils/prices.js'
import { generatedCards, getTemplateForName } from '@/utils/generateCards.js'
import { allListingsForName, userListings } from '@/utils/listings.js'

const route = useRoute()

const productType = computed(() => route.params.type)
const productId   = computed(() => route.params.id)

// ---------- Mystery products ----------
const isMystery = computed(() => productType.value?.startsWith('mystery-'))

const mysteryProduct = computed(() => {
  if (!isMystery.value) return null
  const tier = productType.value.replace('mystery-', '')   // single | mid | pack
  const element = productId.value                           // Fire, Water, etc.
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

// ---------- Filter selections ----------
const selectedCondition = ref('')
const selectedFoil      = ref('')
const selectedLanguage  = ref('')

const quantity = ref(1)

// ---------- Card data ----------
const isCard = computed(() => productType.value === 'card')

// All listings (generated + user) for this card name
const cardListings = computed(() => {
  if (!isCard.value) return []
  return allListingsForName(productId.value)
})

const cardTemplate = computed(() => {
  if (!isCard.value) return null
  return getTemplateForName(productId.value)
})

const allConditions = computed(() => cardTemplate.value?.condition || [])
const allFoils      = computed(() => cardTemplate.value?.foil || [])
const allLanguages  = computed(() => cardTemplate.value?.language || [])

// Reset on product change
watch(productId, () => {
  selectedCondition.value = ''
  selectedFoil.value = ''
  selectedLanguage.value = ''
  quantity.value = 1
})

// Filtered seller listings
const filteredListings = computed(() => {
  return cardListings.value.filter(card => {
    if (selectedCondition.value && card.condition !== selectedCondition.value) return false
    if (selectedFoil.value && card.foil !== selectedFoil.value) return false
    if (selectedLanguage.value && card.language !== selectedLanguage.value) return false
    return true
  })
})

// ---------- Current product (for the header area) ----------
const currentProduct = computed(() => {
  if (isMystery.value) return mysteryProduct.value
  if (isCard.value) {
    const t = cardTemplate.value
    return {
      name: productId.value,
      description: t ? `${t.type} card` : 'Card',
      image: '🃏',
    }
  }
  return null
})

// Mystery product price helpers
const mysteryTotalPrice = computed(() => {
  if (!mysteryProduct.value) return null
  const base = parseFloat(mysteryProduct.value.price.replace('$', ''))
  return (base * quantity.value).toFixed(2)
})
</script>

<template>
  <main class="page-shell product-page">
    <router-link to="/store" class="back-link">← Back to Store</router-link>

    <div v-if="currentProduct" class="product-container">
      <div class="product-image-section">
        <div class="product-image-large">{{ currentProduct.image }}</div>
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

        <!-- Card product: filters + seller listings -->
        <template v-else-if="isCard">
          <div class="filters">
            <div class="filter-group">
              <label>Condition</label>
              <select v-model="selectedCondition">
                <option value="">All conditions</option>
                <option v-for="c in allConditions" :key="c" :value="c">{{ c }}</option>
              </select>
            </div>
            <div class="filter-group">
              <label>Foil</label>
              <select v-model="selectedFoil">
                <option value="">All foil types</option>
                <option v-for="f in allFoils" :key="f" :value="f">{{ f }}</option>
              </select>
            </div>
            <div class="filter-group">
              <label>Language</label>
              <select v-model="selectedLanguage">
                <option value="">All languages</option>
                <option v-for="l in allLanguages" :key="l" :value="l">{{ l }}</option>
              </select>
            </div>
          </div>

          <!-- Seller listings table -->
          <h2 class="section-heading">Listings ({{ filteredListings.length }})</h2>

          <div v-if="filteredListings.length" class="seller-listings">
            <div class="listing-header">
              <span>Seller</span>
              <span>Condition</span>
              <span>Foil</span>
              <span>Language</span>
              <span>Price</span>
              <span></span>
            </div>
            <div v-for="card in filteredListings" :key="card.id" class="listing-row">
              <span class="listing-seller">{{ card.seller }}</span>
              <span>{{ card.condition }}</span>
              <span>{{ card.foil }}</span>
              <span>{{ card.language }}</span>
              <span class="listing-price">${{ card.price }}</span>
              <button class="action-btn listing-buy-btn">Add to Cart</button>
            </div>
          </div>
          <p v-else class="text-muted">No listings match the selected filters.</p>
        </template>
      </div>
    </div>

    <div v-else class="empty-state">
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

.buy-btn {
  width: 100%;
}
</style>
