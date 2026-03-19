<script setup>
import { useRoute, useRouter } from 'vue-router'
import { computed, ref } from 'vue'

const route = useRoute()
const router = useRouter()

const isLoggedIn = computed(() => !!localStorage.getItem('token'))

const publicLinks = [
  { path: '/store', name: 'Store' },
  { path: '/gallery', name: 'Gallery' },
]
const authLinks = [
  { path: '/cart', name: 'Cart' },
  { path: '/orders', name: 'Orders' },
  { path: '/profile', name: 'Profile' },
]

function logout() {
  localStorage.removeItem('token')
  localStorage.removeItem('firstName')
  router.push({ name: 'landing' })
}
</script>

<template>
  <nav class="navbar">
    <div class="navbar-brand">
      <router-link to="/" class="brand-link">
        <img alt="NXTCG Logo" class="logo" src="../../assets/logo.png" width="50" height="50" />
        <span class="brand-text">NXTCG</span>
      </router-link>
    </div>

    <ul class="navbar-nav">
      <li v-for="link in publicLinks" :key="link.path" class="nav-item">
        <router-link
          v-if="route.path !== link.path"
          :to="link.path"
          class="nav-link"
        >{{ link.name }}</router-link>
        <span v-else class="nav-link active">{{ link.name }}</span>
      </li>
      <template v-if="isLoggedIn">
        <li v-for="link in authLinks" :key="link.path" class="nav-item">
          <router-link
            v-if="route.path !== link.path"
            :to="link.path"
            class="nav-link"
          >{{ link.name }}</router-link>
          <span v-else class="nav-link active">{{ link.name }}</span>
        </li>
        <li class="nav-item">
          <button class="nav-link logout-btn" @click="logout">Logout</button>
        </li>
      </template>
    </ul>
  </nav>
</template>

<style scoped>
.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.6rem 2rem;
  background: var(--bg-panel);
  border-bottom: 4px solid var(--water);
  box-shadow: 0 4px 0 var(--shadow);
  position: relative;
  z-index: 100;
}

/* left accent stripe */
.navbar::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 6px;
  background: linear-gradient(180deg, var(--shadow) 0%, var(--water) 50%, var(--grass) 100%);
}

.navbar-brand {
  display: flex;
  align-items: center;
  padding-left: 0.5rem;
}

.brand-link {
  display: flex;
  align-items: center;
  text-decoration: none;
  gap: 0.75rem;
  background: none !important;
}

.brand-text {
  font-family: var(--font-pixel);
  font-size: 0.75rem;
  color: var(--stone);
  text-shadow:
    2px 2px 0 var(--fire),
    4px 4px 0 rgba(128, 21, 2, 0.4);
  letter-spacing: 2px;
  line-height: 1.6;
}

.logo {
  display: block;
  border: 3px solid var(--shadow);
  box-shadow: 3px 3px 0 var(--shadow);
}

.navbar-nav {
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
  gap: 0.35rem;
}

.nav-item { margin: 0; }

.nav-link {
  display: block;
  text-decoration: none;
  font-family: var(--font-head);
  font-size: 1rem;
  font-weight: 900;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: var(--neutral);
  padding: 0.4rem 0.9rem;
  border: 3px solid transparent;
  transition: border-color 80ms, color 80ms, background 80ms;
  background: none;
}

.nav-link:hover:not(.active) {
  color: var(--stone);
  border-color: var(--water);
  background: rgba(12, 157, 215, 0.1);
  box-shadow: 3px 3px 0 var(--water);
}

.nav-link.active {
  color: #000;
  background: var(--grass);
  border-color: #000;
  box-shadow: 3px 3px 0 var(--stone);
}

.logout-btn {
  cursor: pointer;
  background: none;
  color: var(--fire);
  border-color: var(--fire);
  box-shadow: 3px 3px 0 var(--fire);
}
.logout-btn:hover {
  background: var(--fire);
  color: #fff;
  box-shadow: none;
}
</style>
