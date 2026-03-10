<script setup>
import HomePage from './HomePage.vue'
import Navbar from './vues/Navbar/Navbar.vue'
import { RouterView } from 'vue-router';
</script>

<template>
  <Navbar />
  <router-view />
</template>

<style scoped>
</style>
