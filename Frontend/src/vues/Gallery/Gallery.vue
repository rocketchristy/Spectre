<script setup>
import '@/assets/gallery.css'
import { ref, computed, onMounted, onUnmounted } from 'vue'
import HiddenCard from '@/vues/EasterEgg/HiddenCard.vue'

defineOptions({ name: 'Gallery' })

// Dynamically import all card images from the Cards folder
const cardFiles = {
  ...import.meta.glob('@/assets/Images/Cards/*.png', { eager: true }),
  ...import.meta.glob('@/assets/Images/Cards/*.jpg', { eager: true }),
}

const allCards = computed(() =>
  Object.entries(cardFiles)
    .map(([path, module]) => {
      const fileName = path.split('/').pop().replace(/\.(png|jpg)$/i, '')
      return { id: fileName, name: fileName.replace(/_/g, ' '), image: module.default }
    })
    .sort((a, b) => a.name.localeCompare(b.name))
)

// Carousel state
const carouselIndex = ref(0)
const currentCard = computed(() => allCards.value[carouselIndex.value] || { name: '', image: '' })

function prevCard() {
  carouselIndex.value = (carouselIndex.value - 1 + allCards.value.length) % allCards.value.length
}
function nextCard() {
  carouselIndex.value = (carouselIndex.value + 1) % allCards.value.length
}

// Auto-scroll
let autoScrollTimer = null
function startAutoScroll() {
  stopAutoScroll()
  autoScrollTimer = setInterval(nextCard, 3000)
}
function stopAutoScroll() {
  if (autoScrollTimer) { clearInterval(autoScrollTimer); autoScrollTimer = null }
}

onMounted(startAutoScroll)
onUnmounted(stopAutoScroll)

// Modal
const showModal = ref(false)
const modalCard = ref(null)

function openCardModal(card) {
  modalCard.value = card
  showModal.value = true
}
function closeModal() {
  showModal.value = false
  modalCard.value = null
}
</script>

<template>
  <main class="gallery-shell">
    <!-- Welcome Section -->
    <section class="welcome-section" style="position: relative;">
      <div style="position: absolute; top: 0.5rem; right: 0.75rem;">
        <HiddenCard name="Christy" />
      </div>
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
      <div class="carousel-container" @mouseenter="stopAutoScroll" @mouseleave="startAutoScroll">
        <button class="carousel-btn carousel-btn--prev" @click="prevCard" aria-label="Previous card">‹</button>
        <div class="carousel-display">
          <div class="carousel-card">
            <img :src="currentCard.image" :alt="currentCard.name" class="carousel-image" />
            <h3 class="carousel-title">{{ currentCard.name }}</h3>
            <p class="carousel-index">{{ carouselIndex + 1 }} of {{ allCards.length }}</p>
          </div>
        </div>
        <button class="carousel-btn carousel-btn--next" @click="nextCard" aria-label="Next card">›</button>
      </div>
    </section>

    <!-- Static Card Grid -->
    <section class="card-grid-section">
      <h2 class="section-heading">All Cards</h2>
      <div class="card-grid">
        <div
          v-for="card in allCards" :key="card.id"
          class="grid-card"
          @click="openCardModal(card)"
        >
          <img :src="card.image" :alt="card.name" class="grid-card-img" />
          <p class="grid-card-name">{{ card.name }}</p>
        </div>
      </div>
    </section>

    <!-- Card Modal -->
    <div v-if="showModal && modalCard" class="modal-overlay" @click="closeModal">
      <div class="card-modal" @click.stop>
        <button class="modal-close" @click="closeModal">&times;</button>
        <img :src="modalCard.image" :alt="modalCard.name" class="modal-card-img" />
        <h2 class="modal-card-name">{{ modalCard.name }}</h2>
      </div>
    </div>
  </main>
</template>
