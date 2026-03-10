<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { prices, cardPriceModifiers } from '@/utils/prices.js'
import { tempCardData } from '@/utils/tempCard.js'

const route = useRoute()

// Get product info from route params
const productType = computed(() => route.params.type)
const productId = computed(() => route.params.id)

// For sealed products
const sealedProducts = {
  pack: { name: 'Booster Pack', price: prices[0].pack, description: '10 random cards per pack', stock: 50, image: '📦' },
  bundle: { name: 'Bundle', price: prices[0].bundle, description: '5 packs + 1 promo card', stock: 25, image: '🎁' },
  box: { name: 'Booster Box', price: prices[0].box, description: '36 packs per box', stock: 10, image: '📦' },
}

// Filter selections for cards
const selectedCondition = ref('')
const selectedFoil = ref('')
const selectedLanguage = ref('')

// Quantity
const quantity = ref(1)

// Get available options from the card data for this character
const cardVariants = computed(() => {
  if (productType.value !== 'card') return []
  return tempCardData.filter(card => card.character === productId.value)
})

const availableConditions = computed(() => [...new Set(cardVariants.value.map(c => c.condition))])
const availableFoils = computed(() => [...new Set(cardVariants.value.map(c => c.foil))])
const availableLanguages = computed(() => [...new Set(cardVariants.value.map(c => c.language))])

// Reset filters and quantity when navigating to a different product
watch(productId, () => {
  selectedCondition.value = ''
  selectedFoil.value = ''
  selectedLanguage.value = ''
  quantity.value = 1
})


// Calculate current price based on selections
const calculatedPrice = computed(() => {
  if (productType.value !== 'card') return null
  
  const basePrice = parseFloat(prices[0].card.replace('$', ''))
  let modifier = 1

  if (selectedCondition.value) {
    modifier *= cardPriceModifiers.condition[selectedCondition.value] || 1
  }
  if (selectedFoil.value) {
    modifier *= cardPriceModifiers.foil[selectedFoil.value] || 1
  }
  if (selectedLanguage.value) {
    modifier *= cardPriceModifiers.language[selectedLanguage.value] || 1
  }

  return (basePrice * modifier).toFixed(2)
})

// Find matching stock based on current selections
const matchingCards = computed(() => {
  if (productType.value !== 'card') return []
  
  return cardVariants.value.filter(card => {
    if (selectedCondition.value && card.condition !== selectedCondition.value) return false
    if (selectedFoil.value && card.foil !== selectedFoil.value) return false
    if (selectedLanguage.value && card.language !== selectedLanguage.value) return false
    return true
  })
})

const currentStock = computed(() => matchingCards.value.length)

// Reset quantity when available stock changes
watch(currentStock, (newStock) => {
  if (quantity.value > newStock) quantity.value = Math.max(1, newStock)
})

const hasAllSelections = computed(() => {
  return selectedCondition.value && selectedFoil.value && selectedLanguage.value
})

// Check if current selection combination exists
const selectionExists = computed(() => {
  if (!hasAllSelections.value) return true
  return matchingCards.value.length > 0
})

// Total price
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

// Product display info
const currentProduct = computed(() => {
  if (productType.value === 'card') {
    return {
      name: `${productId.value} Card`,
      description: `${productId.value} character card`,
      image: '🃏',
      isCard: true
    }
  }
  return sealedProducts[productType.value] || null
})
</script>

<template>
  <main class="product-page">
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
          <button class="buy-btn" :disabled="currentProduct.stock === 0">
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
                <option v-for="cond in availableConditions" :key="cond" :value="cond">
                  {{ cond }}
                </option>
              </select>
            </div>

            <div class="filter-group">
              <label>Foil</label>
              <select v-model="selectedFoil">
                <option value="">Select foil type...</option>
                <option v-for="foil in availableFoils" :key="foil" :value="foil">
                  {{ foil }}
                </option>
              </select>
            </div>

            <div class="filter-group">
              <label>Language</label>
              <select v-model="selectedLanguage">
                <option value="">Select language...</option>
                <option v-for="lang in availableLanguages" :key="lang" :value="lang">
                  {{ lang }}
                </option>
              </select>
            </div>
          </div>

          <div class="price-section">
            <span class="price">${{ hasAllSelections ? totalPrice : calculatedPrice }}</span>
            <span class="stock" :class="{ 'out-of-stock': currentStock === 0 }">
              <template v-if="hasAllSelections">{{ currentStock }} in stock</template>
              <template v-else>{{ currentStock }} variants available</template>
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
            class="buy-btn" 
            :disabled="!hasAllSelections || currentStock === 0"
          >
            <template v-if="!hasAllSelections">Select options</template>
            <template v-else-if="currentStock === 0">Out of Stock</template>
            <template v-else>Add {{ quantity }} to Cart</template>
          </button>
        </template>
      </div>
    </div>

    <div v-else class="not-found">
      <h2>Product not found</h2>
      <router-link to="/store">Return to store</router-link>
    </div>
  </main>
</template>

<style scoped>
.product-page {
  padding: 2rem;
  max-width: 1000px;
  margin: 0 auto;
}

.back-link {
  display: inline-block;
  margin-bottom: 2rem;
  color: var(--color-text, #ccc);
  text-decoration: none;
}

.back-link:hover {
  color: var(--color-heading, #fff);
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

.description {
  color: var(--color-text-mute, #888);
  margin-bottom: 2rem;
}

.filters {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 2rem;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-group label {
  font-weight: bold;
  color: var(--color-heading, #fff);
  font-size: 0.875rem;
  text-transform: uppercase;
}

.filter-group select {
  padding: 0.75rem 1rem;
  border-radius: 6px;
  border: 1px solid var(--color-border, #333);
  background: var(--color-background-soft, #1a1a2e);
  color: var(--color-text, #ccc);
  font-size: 1rem;
  cursor: pointer;
}

.filter-group select:focus {
  outline: none;
  border-color: var(--color-accent, #646cff);
}

.price-section {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.price {
  font-size: 2rem;
  font-weight: bold;
  color: var(--color-accent, #42b883);
}

.stock {
  font-size: 1rem;
  color: var(--color-text-mute, #888);
  padding: 0.25rem 0.75rem;
  background: var(--color-background-soft, #1a1a2e);
  border-radius: 4px;
}

.stock.out-of-stock {
  color: #ff6b6b;
  background: rgba(255, 107, 107, 0.1);
}

.no-match-warning {
  color: #ff6b6b;
  margin-bottom: 1rem;
  padding: 0.75rem;
  background: rgba(255, 107, 107, 0.1);
  border-radius: 6px;
}

.buy-btn {
  width: 100%;
  padding: 1rem 2rem;
  font-size: 1.1rem;
  font-weight: bold;
  border: none;
  border-radius: 8px;
  background: var(--color-accent, #42b883);
  color: white;
  cursor: pointer;
  transition: background 0.2s, opacity 0.2s;
}

.buy-btn:hover:not(:disabled) {
  background: var(--color-accent-hover, #33a06f);
}

.buy-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.quantity-control {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.quantity-control button {
  width: 2.25rem;
  height: 2.25rem;
  font-size: 1.25rem;
  line-height: 1;
  border: 1px solid var(--color-border, #333);
  background: var(--color-background-soft, #1a1a2e);
  color: var(--color-heading, #fff);
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;
}

.quantity-control button:hover:not(:disabled) {
  background: var(--color-background-mute, #2a2a4e);
}

.quantity-control button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.quantity-control input {
  width: 4rem;
  text-align: center;
  padding: 0.4rem;
  border: 1px solid var(--color-border, #333);
  background: var(--color-background-soft, #1a1a2e);
  color: var(--color-heading, #fff);
  border-radius: 4px;
  font-size: 1rem;
}

.quantity-control input::-webkit-inner-spin-button,
.quantity-control input::-webkit-outer-spin-button {
  opacity: 1;
}

.not-found {
  text-align: center;
  padding: 4rem;
}

.not-found h2 {
  color: var(--color-heading, #fff);
  margin-bottom: 1rem;
}

.not-found a {
  color: var(--color-accent, #42b883);
}
</style>
