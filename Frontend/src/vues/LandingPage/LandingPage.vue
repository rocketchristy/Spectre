<script setup>
import bg from '@/assets/Images/LandingPageBG.png'
import '@/assets/landingPage.css'
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

defineOptions({ name: 'LandingPage' })

const router = useRouter()

// Initial state
const showAuthFields = ref(false)

const email = ref('')
const password = ref('')

const submitting = ref(false)
const touched = ref(false)

const isValid = computed(
  () => email.value.trim() !== '' && password.value.trim() !== ''
)

const onLogin = async () => {
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
  <div class="landing" :style="{ backgroundImage: `url(${bg})` }">
    <div class="landing__inner">
      <div class="landing__card" role="region">
        
        <h1 class="landing__title">Welcome to NextGen Trading Card Game™</h1>

        <!-- Login/Sign-up buttons -->
        <div v-if="!showAuthFields" class="initial-options">
          <button class="btn landing__cta" @click="showAuthFields = true">
            Login / Sign‑Up
          </button>

          <button class="btn landing__cta" @click="continueAsGuest">
            Continue your adventure as a guest
          </button>
        </div>

        <!-- Login/sign-up fields -->
        <div v-else class="auth-fields">

          <div class="login-strip__row">
            <input
              class="login-input"
              type="email"
              v-model.trim="email"
              placeholder="Email"
              autocomplete="email"
            />
          </div>

          <div class="login-strip__row">
            <input
              class="login-input"
              type="password"
              v-model.trim="password"
              placeholder="Password"
              autocomplete="current-password"
            />
          </div>

          <!-- Button actions -->
          <div class="auth-actions">
            <button
              class="btn landing__cta"
              :disabled="!isValid || submitting"
              @click="onLogin"
            >
              {{ submitting ? 'Checking…' : 'Login' }}
            </button>

            <button
              class="btn landing__cta"
              :disabled="!isValid || submitting"
              @click="onSignup"
            >
              {{ submitting ? 'Creating...' : 'Sign‑Up' }}
            </button>
          </div>

        </div>

        <div class="landing__carousel" aria-hidden="true">
          <!-- carousel here later -->
        </div>

      </div>
    </div>
  </div>
</template>