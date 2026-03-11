<script setup>
import { prices } from '@/utils/prices.js'
import { tempCardData } from '@/utils/tempCard.js'

// Get unique characters from card data
const uniqueCharacters = [...new Set(tempCardData.map(card => card.character))]

const products = [
  { id: 'pack', name: 'Booster Pack', type: 'pack', price: prices[0].pack, description: '10 random cards per pack', image: '📦' },
  { id: 'bundle', name: 'Bundle', type: 'bundle', price: prices[0].bundle, description: '6 packs per bundle', image: '🎁' },
  { id: 'box', name: 'Booster Box', type: 'box', price: prices[0].box, description: '15 packs per box', image: '📦' },
]

// Generate card products from unique characters
const cardProducts = uniqueCharacters.map(char => ({
  id: `card-${char.toLowerCase()}`,
  name: `${char} Card`,
  type: 'card',
  character: char,
  basePrice: prices[0].card,
  image: '🃏'
}))
</script>

<template>
  <main class="store-page">
    <h1 class="store-title">Store</h1>
    
    <section class="product-section">
      <h2>Sealed Products</h2>
      <div class="product-grid">
        <router-link 
          v-for="product in products" 
          :key="product.id"
          :to="{ name: 'product', params: { type: product.type, id: product.id } }"
          class="product-card"
        >
          <div class="product-image">{{ product.image }}</div>
          <h3>{{ product.name }}</h3>
          <p class="product-description">{{ product.description }}</p>
          <p class="product-price">{{ product.price }}</p>
        </router-link>
      </div>
    </section>

    <section class="product-section">
      <h2>Singles</h2>
      <div class="product-grid">
        <router-link 
          v-for="card in cardProducts" 
          :key="card.id"
          :to="{ name: 'product', params: { type: 'card', id: card.character } }"
          class="product-card"
        >
          <div class="product-image">{{ card.image }}</div>
          <h3>{{ card.name }}</h3>
          <p class="product-description">{{ card.description }}</p>
          <p class="product-price">From {{ card.basePrice }}</p>
        </router-link>
      </div>
    </section>
  </main>
</template>

<style scoped>
.store-page {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.store-title {
  text-align: center;
  margin-bottom: 2rem;
  color: var(--color-heading, #fff);
}

.product-section {
  margin-bottom: 3rem;
}

.product-section h2 {
  margin-bottom: 1.5rem;
  color: var(--color-heading, #fff);
  border-bottom: 2px solid var(--color-border, #333);
  padding-bottom: 0.5rem;
}

.product-grid {
  display: flex;
  flex-direction: row;
  flex-wrap: nowrap;
  gap: 1.5rem;
}

.product-card {
  flex: 1;
  min-width: 0; /* prevents flex blowout */
  background: var(--color-background-soft, #1a1a2e);
  border: 1px solid var(--color-border, #333);
  border-radius: 8px;
  padding: 1.5rem;
  text-decoration: none;
  color: var(--color-text, #ccc);
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.product-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
  border-color: var(--color-accent, #646cff);
}

.product-image {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.product-card h3 {
  margin: 0 0 0.5rem;
  color: var(--color-heading, #fff);
}

.product-description {
  font-size: 0.875rem;
  margin: 0 0 1rem;
  color: var(--color-text-mute, #888);
}

.product-price {
  font-size: 1.25rem;
  font-weight: bold;
  color: var(--color-accent, #42b883);
  margin: 0;
}
</style>
