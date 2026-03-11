<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()

const navLinks = [
  { path: '/', name: 'Home' },
  { path: '/store', name: 'Store' },
]
</script>

<template>
  <nav class="navbar">
    <div class="navbar-brand">
      <router-link to="/" class="brand-link">
        <img alt="NXT TCG Logo" class="logo" src="../../assets/logo.png" width="50" height="50" />
        <span class="brand-text">NXT TCG</span>
      </router-link>
    </div>

    <ul class="navbar-nav">
      <li v-for="link in navLinks" :key="link.path" class="nav-item">
        <router-link 
          v-if="route.path !== link.path"
          :to="link.path" 
          class="nav-link"
        >
          {{ link.name }}
        </router-link>
        <span v-else class="nav-link active">{{ link.name }}</span>
      </li>
    </ul>
  </nav>
</template>

<style scoped>
.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 2rem;
  background-color: var(--color-background-soft, #1a1a2e);
  border-bottom: 1px solid var(--color-border, #333);
}

.navbar-brand {
  display: flex;
  align-items: center;
}

.brand-link {
  display: flex;
  align-items: center;
  text-decoration: none;
  color: var(--color-heading, #fff);
  gap: 0.75rem;
}

.brand-text {
  font-size: 1.25rem;
  font-weight: bold;
}

.logo {
  display: block;
}

.navbar-nav {
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
  gap: 1.5rem;
}

.nav-item {
  margin: 0;
}

.nav-link {
  text-decoration: none;
  color: var(--color-text, #ccc);
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: background-color 0.2s, color 0.2s;
}

.nav-link:hover:not(.active) {
  background-color: var(--color-background-mute, #2a2a4e);
  color: var(--color-heading, #fff);
}

.nav-link.active {
  color: var(--color-heading, #fff);
  font-weight: bold;
  cursor: default;
}
</style>
