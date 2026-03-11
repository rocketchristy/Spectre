<script setup>
import '@/assets/gallery.css'
import { ref, computed } from 'vue'
import { generatedCards } from '@/utils/generateCards.js'

defineOptions({ name: 'Gallery' })

// Get unique card names for carousel
const uniqueCardNames = computed(() => [
  ...new Set(generatedCards.map(c => c.name))
])

// Current carousel index
const carouselIndex = ref(0)

// Current carousel card
const currentCarouselCard = computed(() => ({
  name: uniqueCardNames.value[carouselIndex.value] || 'Card',
  image: '🎴'
}))

// Navigate carousel
const prevCard = () => {
  carouselIndex.value = (carouselIndex.value - 1 + uniqueCardNames.value.length) % uniqueCardNames.value.length
}

const nextCard = () => {
  carouselIndex.value = (carouselIndex.value + 1) % uniqueCardNames.value.length
}

// Sample user cards (current user's cards for sale)
const currentUserCards = computed(() =>
  generatedCards.filter(c => c.stock > 0 && c.rarity === 'Rare').slice(0, 6)
)

// Sample other users' cards for sale
const otherUsersCards = computed(() =>
  generatedCards.filter(c => c.stock > 0 && c.rarity !== 'Rare').slice(0, 12)
)
</script>

<template>
  <main class="gallery-shell">
    <!-- Welcome Section -->
    <section class="welcome-section">
      <div class="welcome-content">
        <h1 class="welcome-title">Welcome to the Card Gallery</h1>
        <p class="welcome-message">
          Explore our extensive collection of trading cards. Browse cards from collectors worldwide,
          or showcase your own collection for sale. Find rare gems, complete your sets, or build your deck!
        </p>
      </div>
    </section>

    <!-- Carousel Section -->
    <section class="carousel-section">
      <h2 class="section-heading">Featured Cards</h2>
      <div class="carousel-container">
        <button class="carousel-btn carousel-btn--prev" @click="prevCard" aria-label="Previous card">
          ‹
        </button>

        <div class="carousel-display">
          <div class="carousel-card">
            <div class="carousel-image">{{ currentCarouselCard.image }}</div>
            <h3 class="carousel-title">{{ currentCarouselCard.name }}</h3>
            <p class="carousel-index">
              {{ carouselIndex + 1 }} of {{ uniqueCardNames.length }}
            </p>
          </div>
        </div>

        <button class="carousel-btn carousel-btn--next" @click="nextCard" aria-label="Next card">
          ›
        </button>
      </div>

      <!-- Carousel indicators -->
      <div class="carousel-indicators">
        <button
          v-for="(_, index) in uniqueCardNames"
          :key="index"
          class="indicator"
          :class="{ active: index === carouselIndex }"
          @click="carouselIndex = index"
          :aria-label="`Go to card ${index + 1}`"
        />
      </div>
    </section>

    <!-- Other Users' Cards Section -->
    <section class="marketplace-section">
      <h2 class="section-heading">Cards from Collectors</h2>
      <div class="cards-grid">
        <router-link
          v-for="card in otherUsersCards"
          :key="card.id"
          :to="{ name: 'product', params: { type: 'card', id: card.name } }"
          class="marketplace-card"
        >
          <div class="card-image">🎴</div>
          <div class="card-info">
            <h3 class="card-name">{{ card.name }}</h3>
            <p class="card-rarity" :class="`rarity-${card.rarity.toLowerCase()}`">
              {{ card.rarity }}
            </p>
            <p class="card-condition">{{ card.condition }}</p>
            <p class="card-foil" v-if="card.foil !== 'Non-foil'">{{ card.foil }}</p>
            <p class="card-price">${{ card.price }}</p>
          </div>
        </router-link>
      </div>
    </section>

    <!-- Current User's Cards Section -->
    <section class="user-cards-section">
      <h2 class="section-heading">Your Cards for Sale</h2>
      <div v-if="currentUserCards.length > 0" class="cards-grid">
        <router-link
          v-for="card in currentUserCards"
          :key="card.id"
          :to="{ name: 'product', params: { type: 'card', id: card.name } }"
          class="user-card"
        >
          <div class="card-image">🎴</div>
          <div class="card-info">
            <h3 class="card-name">{{ card.name }}</h3>
            <p class="card-rarity" :class="`rarity-${card.rarity.toLowerCase()}`">
              {{ card.rarity }}
            </p>
            <p class="card-condition">{{ card.condition }}</p>
            <p class="card-foil" v-if="card.foil !== 'Non-foil'">{{ card.foil }}</p>
            <p class="card-price">${{ card.price }}</p>
          </div>
          <button class="edit-btn">Edit</button>
        </router-link>
      </div>
      <div v-else class="no-cards">
        <p>You don't have any cards listed for sale yet.</p>
        <router-link to="/store" class="btn-link">Add Cards to Sell</router-link>
      </div>
    </section>
  </main>
</template>
