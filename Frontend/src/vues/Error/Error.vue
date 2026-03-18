<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const errorMessage = computed(() => route.query.message || 'An unexpected error occurred.')
</script>

<template>
  <main class="page-shell">
    <div class="error-container">
      <h1 class="error-title">Something went wrong</h1>
      <p class="error-message">{{ errorMessage }}</p>
      <div class="error-actions">
        <router-link to="/store" class="action-btn">Back to Store</router-link>
        <router-link to="/" class="action-btn">Return Home</router-link>
      </div>
    </div>
  </main>
</template>

<style scoped>
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 50vh;
  text-align: center;
  gap: 1.5rem;
}
.error-title {
  color: var(--color-heading, #fff);
  font-size: 2rem;
}
.error-message {
  color: var(--color-text, #ccc);
  font-size: 1.1rem;
  max-width: 500px;
}
.error-actions {
  display: flex;
  gap: 1rem;
}
</style>
