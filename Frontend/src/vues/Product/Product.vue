<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { prices, cardPriceModifiers } from '@/utils/prices.js'
import { generatedCards, getTemplateForName } from '@/utils/generateCards.js'

const route = useRoute()

const productType = computed(() => route.params.type)
const productId = computed(() => route.params.id)

// Sealed products
const sealedProducts = {
  pack: { name: 'Booster Pack', price: prices[0].pack, description: '10 random cards per pack', stock: 50, image: '📦' },
  bundle: { name: 'Bundle', price: prices[0].bundle, description: '5 packs + 1 promo card', stock: 25, image: '🎁' },
  box: { name: 'Booster Box', price: prices[0].box, description: '36 packs per box', stock: 10, image: '📦' },
}

// Filter selections
const selectedCondition = ref('')
const selectedFoil = ref('')
const selectedLanguage = ref('')

const quantity = ref(1)

// All generated cards matching this product name
const cardVariants = computed(() => {
  if (productType.value !== 'card') return []
  return generatedCards.filter(c => c.name === productId.value)
})

// The raw template for this card name — gives us ALL possible option values
const cardTemplate = computed(() => {
  if (productType.value !== 'card') return null
  return getTemplateForName(productId.value)
})

// All possible options from template
const allConditions = computed(() => cardTemplate.value?.condition || [])
const allFoils      = computed(() => cardTemplate.value?.foil || [])
const allLanguages  = computed(() => cardTemplate.value?.language || [])

// Options that actually exist in stock (stock > 0)
const inStockConditions = computed(() => new Set(
  cardVariants.value.filter(c => c.stock > 0).map(c => c.condition)
))
const inStockFoils = computed(() => new Set(
  cardVariants.value.filter(c => c.stock > 0).map(c => c.foil)
))
const inStockLanguages = computed(() => new Set(
  cardVariants.value.filter(c => c.stock > 0).map(c => c.language)
))

// Reset filters and quantity on product change
watch(productId, () => {
  selectedCondition.value = ''
  selectedFoil.value = ''
  selectedLanguage.value = ''
  quantity.value = 1
})

// Price based on current selections
const calculatedPrice = computed(() => {
  if (productType.value !== 'card') return null
  const base = parseFloat(prices[0].card.replace('$', ''))
  let modifier = 1
  if (selectedCondition.value) modifier *= cardPriceModifiers.condition[selectedCondition.value] || 1
  if (selectedFoil.value)      modifier *= cardPriceModifiers.foil[selectedFoil.value] || 1
  if (selectedLanguage.value)  modifier *= cardPriceModifiers.language[selectedLanguage.value] || 1
  return (base * modifier).toFixed(2)
})

// Cards matching current filter selections with stock > 0
const matchingCards = computed(() => {
  if (productType.value !== 'card') return []
  return cardVariants.value.filter(card => {
    if (card.stock <= 0) return false
    if (selectedCondition.value && card.condition !== selectedCondition.value) return false
    if (selectedFoil.value && card.foil !== selectedFoil.value) return false
    if (selectedLanguage.value && card.language !== selectedLanguage.value) return false
    return true
  })
})

const currentStock = computed(() =>
  matchingCards.value.reduce((sum, c) => sum + c.stock, 0)
)

watch(currentStock, (s) => {
  if (quantity.value > s) quantity.value = Math.max(1, s)
})

const hasAllSelections = computed(() =>
  selectedCondition.value && selectedFoil.value && selectedLanguage.value
)

const selectionExists = computed(() => {
  if (!hasAllSelections.value) return true
  return matchingCards.value.length > 0
})

const totalPrice = computed(() => {
  if (productType.value === 'card') {
    return (parseFloat(calculatedPrice.value) * quantity.value).toFixed(2)
  }
  if (currentProduct.value) {
    const base = parseFloat(currentProduct.value.price.replace('$', ''))
    return (base * quantity.value).toFixed(2)
  }
  return null
})

const currentProduct = computed(() => {
  if (productType.value === 'card') {
    const t = cardTemplate.value
    return {
      name: `${productId.value}`,
      description: t ? `${t.type} card` : 'Card',
      image: '🃏',
      isCard: true,
    }
  }
  return sealedProducts[productType.value] || null
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

        <!-- Sealed product (no filters) -->
        <template v-if="!currentProduct.isCard">
          <div class="price-section">
            <span class="price">${{ totalPrice }}</span>
            <span class="stock" :class="{ 'out-of-stock': currentProduct.stock === 0 }">
              {{ currentProduct.stock }} in stock
            </span>
          </div>
          <div class="quantity-control">
            <button @click="quantity = Math.max(1, quantity - 1)" :disabled="quantity <= 1">−</button>
            <input
              type="number"
              v-model.number="quantity"
              :min="1"
              :max="currentProduct.stock"
              @change="quantity = Math.min(Math.max(1, quantity), currentProduct.stock)"
            />
            <button @click="quantity = Math.min(quantity + 1, currentProduct.stock)" :disabled="quantity >= currentProduct.stock">+</button>
          </div>
          <button class="action-btn buy-btn" :disabled="currentProduct.stock === 0">
            Add {{ quantity }} to Cart
          </button>
        </template>

        <!-- Card product (with filters) -->
        <template v-else>
          <div class="filters">
            <div class="filter-group">
              <label>Condition</label>
              <select v-model="selectedCondition">
                <option value="">Select condition...</option>
                <option
                  v-for="cond in allConditions" :key="cond" :value="cond"
                  :disabled="!inStockConditions.has(cond)"
                  :class="{ 'option-unavailable': !inStockConditions.has(cond) }"
                >
                  {{ cond }}{{ !inStockConditions.has(cond) ? ' (unavailable)' : '' }}
                </option>
              </select>
            </div>

            <div class="filter-group">
              <label>Foil</label>
              <select v-model="selectedFoil">
                <option value="">Select foil type...</option>
                <option
                  v-for="foil in allFoils" :key="foil" :value="foil"
                  :disabled="!inStockFoils.has(foil)"
                  :class="{ 'option-unavailable': !inStockFoils.has(foil) }"
                >
                  {{ foil }}{{ !inStockFoils.has(foil) ? ' (unavailable)' : '' }}
                </option>
              </select>
            </div>

            <div class="filter-group">
              <label>Language</label>
              <select v-model="selectedLanguage">
                <option value="">Select language...</option>
                <option
                  v-for="lang in allLanguages" :key="lang" :value="lang"
                  :disabled="!inStockLanguages.has(lang)"
                  :class="{ 'option-unavailable': !inStockLanguages.has(lang) }"
                >
                  {{ lang }}{{ !inStockLanguages.has(lang) ? ' (unavailable)' : '' }}
                </option>
              </select>
            </div>
          </div>

          <div class="price-section">
            <span class="price">${{ hasAllSelections ? totalPrice : calculatedPrice }}</span>
            <span class="stock" :class="{ 'out-of-stock': currentStock === 0 }">
              <template v-if="hasAllSelections">{{ currentStock }} in stock</template>
              <template v-else>{{ currentStock }} available</template>
            </span>
          </div>

          <div v-if="hasAllSelections && !selectionExists" class="no-match-warning">
            This combination is not available.
          </div>

          <div v-if="hasAllSelections && currentStock > 0" class="quantity-control">
            <button @click="quantity = Math.max(1, quantity - 1)" :disabled="quantity <= 1">−</button>
            <input
              type="number"
              v-model.number="quantity"
              :min="1"
              :max="currentStock"
              @change="quantity = Math.min(Math.max(1, quantity), currentStock)"
            />
            <button @click="quantity = Math.min(quantity + 1, currentStock)" :disabled="quantity >= currentStock">+</button>
          </div>

          <button 
            class="action-btn buy-btn" 
            :disabled="!hasAllSelections || currentStock === 0"
          >
            <template v-if="!hasAllSelections">Select options</template>
            <template v-else-if="currentStock === 0">Out of Stock</template>
            <template v-else>Add {{ quantity }} to Cart</template>
          </button>
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
/* Only product-page-specific overrides; shared rules in page.css */
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
