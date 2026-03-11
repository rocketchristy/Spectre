
<script setup>
import bg from '@/assets/Images/LandingPageBG.png'
import '@/assets/landingPage.css'
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

defineOptions({ name: 'LandingPage' })

const router = useRouter()

// form state (simple client-side gate)
const username = ref('')
const password = ref('')
const touched = ref(false)
const submitting = ref(false)

const isValid = computed(
  () => username.value.trim() !== '' && password.value.trim() !== ''
)

const onSubmit = async (e) => {
  e?.preventDefault?.()
  touched.value = true
  if (!isValid.value) return
  try {
    submitting.value = true
    // TODO: replace with real auth if needed
    await new Promise((r) => setTimeout(r, 150))
    router.push({ name: 'store' })
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <!-- Use the imported image as the full-viewport background on the .landing container -->
  <div class="landing" :style="{ backgroundImage: `url(${bg})` }">
    <div class="landing__inner">
      <div class="landing__card" role="region" aria-label="Landing background">
        <h1 class="landing__title">Welcome to NextGen Trading Card Game™</h1>

        <!-- Login form-->
         <form class="login-strip" @submit="onSubmit" novalidate>
          <div class="login-strip__row">
            <label class="sr-only" for="username">Username</label>
            <input
              id="username"
              class="login-input"
              type="text"
              v-model.trim="username"
              placeholder="Username"
              autocomplete="username"
            />
          </div>
          <div class="login-strip__row">
            <label class="sr-only" for="password">Password</label>
            <input
              id="password"
              class="login-input"
              type="password"
              v-model.trim="password"
              placeholder="Password"
              autocomplete="current-password"
            />
          </div>

          <!-- CTA moved below inputs; only navigates when both fields are filled -->
          <button
            class="landing__cta btn"
            type="submit"
            :disabled="!isValid || submitting"
          >
            {{ submitting ? 'Checking…' : 'Click here to start your adventure' }}
          </button>
        </form>
        <!-- Placeholder for future image carousel -->
        <div class="landing__carousel" aria-hidden="true">
            
          <!-- insert carousel component here later -->
        </div>
      </div>
    </div>
  </div>
</template>
