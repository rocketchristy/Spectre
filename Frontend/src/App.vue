<script setup>
import Navbar from './vues/Navbar/Navbar.vue'
import SiteFooter from './vues/Navbar/Footer.vue'
import { RouterView, useRoute } from 'vue-router';

const route = useRoute()
</script>

<template>
  <div class="app-layout">
    <Navbar v-if="route.path !== '/'" />
    <router-view />
      <SiteFooter v-if="route.path !== '/'" />
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  width: 100%;
}
</style>