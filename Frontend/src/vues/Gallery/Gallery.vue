<script setup>
import '@/assets/gallery.css'
import { ref, computed } from 'vue'

defineOptions({ name: 'Gallery' })

// Dynamically import all card border images from the Cards folder
const cardFiles = import.meta.glob('@/assets/Images/Cards/*.png', { eager: true })

// Create carousel with 51 slots, repeating the available cards
const carouselCards = computed(() => {
  const cards = Object.entries(cardFiles).map(([path, module]) => {
    const fileName = path.split('/').pop().replace('.png', '')
    return {
      id: fileName,
      name: fileName.replace(/_/g, ' '),
      image: module.default
    }
  }).sort((a, b) => a.name.localeCompare(b.name))
  
  // Create 51 slots by cycling through available cards
  const carousel = []
  for (let i = 0; i < 51; i++) {
    carousel.push(cards[i % cards.length])
  }
  return carousel
})

// Current carousel index
const carouselIndex = ref(0)

// Current carousel card
const currentCarouselCard = computed(() => carouselCards.value[carouselIndex.value] || { name: 'Card', image: '' })

// Navigate carousel
const prevCard = () => {
  carouselIndex.value = (carouselIndex.value - 1 + carouselCards.value.length) % carouselCards.value.length
}

const nextCard = () => {
  carouselIndex.value = (carouselIndex.value + 1) % carouselCards.value.length
}

// Sample user cards (current user's cards for sale) - MOVED
/*
const currentUserCards = computed(() =>
  generatedCards.filter(c => c.stock > 0 && c.rarity === 'Rare').slice(0, 6)
)
*/

// Sample other users' cards for sale - MOVED
/*
const otherUsersCards = computed(() =>
  generatedCards.filter(c => c.stock > 0 && c.rarity !== 'Rare').slice(0, 12)
)
*/
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
            <img :src="currentCarouselCard.image" :alt="currentCarouselCard.name" class="carousel-image" />
            <h3 class="carousel-title">{{ currentCarouselCard.name }}</h3>
            <p class="carousel-index">
              {{ carouselIndex + 1 }} of {{ carouselCards.length }}
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
          v-for="(_, index) in carouselCards"
          :key="index"
          class="indicator"
          :class="{ active: index === carouselIndex }"
          @click="carouselIndex = index"
          :aria-label="`Go to card ${index + 1}`"
        />
      </div>
    </section>

    <!-- Other Users' Cards Section - MOVED -->
    <!--
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
            <p class="card-rarity" :class="`rarity-${card.rarity.toLowerCase().replace(' ', '-')}`">
              {{ card.rarity }}
            </p>
            <p class="card-condition">{{ card.condition }}</p>
            <p class="card-foil" v-if="card.foil !== 'Non-foil'">{{ card.foil }}</p>
            <p class="card-price">${{ card.price }}</p>
          </div>
        </router-link>
      </div>
    </section>
    -->
  </main>
</template>
