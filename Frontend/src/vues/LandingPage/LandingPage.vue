<script setup>
// Import the background image from src/assets/Images
// Use the exact path and casing that exists in the repo
import bg from '@/assets/Images/LandingPageBG.png'
// set the component name for devtools and stack traces
defineOptions({ name: 'LandingPage' })
</script>

<template>
  <!-- Use the imported image as the full-viewport background on the .landing container -->
  <div class="landing" :style="{ backgroundImage: `url(${bg})` }">
    <div class="landing__inner">
      <div class="landing__card" role="region" aria-label="Landing background">
        <h1 class="landing__title">Welcome to NextGen Trading Card Game™</h1>
        <router-link class="landing__cta btn" :to="{ name: 'homepage' }">Click here to start your adventure</router-link>

        <!-- Placeholder for future image carousel -->
        <div class="landing__carousel" aria-hidden="true">
            
          <!-- insert carousel component here later -->
        </div>
      </div>
    </div>
  </div>
</template>
