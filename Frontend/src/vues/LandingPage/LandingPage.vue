<script setup>
import bg from '@/assets/Images/LandingPageBG.png'
import '@/assets/landingPage.css'
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { loginUser, registerUser } from '@/utils/api.js'

defineOptions({ name: 'LandingPage' })

const router = useRouter()

// Initial state
const showAuthFields = ref(false)
const isSignup = ref(false)

const email = ref('')
const password = ref('')
const firstName = ref('')
const lastName = ref('')

const submitting = ref(false)
const touched = ref(false)
const errorMsg = ref('')

const isLoginValid = computed(
  () => email.value.trim() !== '' && password.value.trim() !== ''
)

const isSignupValid = computed(
  () =>
    isLoginValid.value &&
    firstName.value.trim() !== '' &&
    lastName.value.trim() !== ''
)

const isValid = computed(() =>
  isSignup.value ? isSignupValid.value : isLoginValid.value
)

const continueAsGuest = () => {
  router.push({ name: 'store' })
}

const onLogin = async () => {
  touched.value = true
  errorMsg.value = ''
  if (!isLoginValid.value) return
  try {
    submitting.value = true
    const data = await loginUser(email.value, password.value)
    localStorage.setItem('token', data.token)
    localStorage.setItem('firstName', data.first_name)
    router.push({ name: 'store' })
  } catch (err) {
    errorMsg.value = err.message
  } finally {
    submitting.value = false
  }
}

const onSignup = async () => {
  touched.value = true
  errorMsg.value = ''
  if (!isSignupValid.value) return
  try {
    submitting.value = true
    await registerUser(
      email.value,
      password.value,
      firstName.value,
      lastName.value
    )
    // Auto-login after successful registration
    const data = await loginUser(email.value, password.value)
    localStorage.setItem('token', data.token)
    localStorage.setItem('firstName', data.first_name)
    router.push({ name: 'store' })
  } catch (err) {
    errorMsg.value = err.message
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

          <p v-if="errorMsg" class="auth-error" role="alert">{{ errorMsg }}</p>

          <div v-if="isSignup" class="login-strip__row">
            <input
              class="login-input"
              type="text"
              v-model.trim="firstName"
              placeholder="First Name"
              autocomplete="given-name"
            />
          </div>

          <div v-if="isSignup" class="login-strip__row">
            <input
              class="login-input"
              type="text"
              v-model.trim="lastName"
              placeholder="Last Name"
              autocomplete="family-name"
            />
          </div>

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
            <template v-if="!isSignup">
              <button
                class="btn landing__cta"
                :disabled="!isValid || submitting"
                @click="onLogin"
              >
                {{ submitting ? 'Checking…' : 'Login' }}
              </button>

              <button
                class="btn landing__cta"
                @click="isSignup = true"
              >
                Sign‑Up
              </button>
            </template>

            <template v-else>
              <button
                class="btn landing__cta"
                :disabled="!isValid || submitting"
                @click="onSignup"
              >
                {{ submitting ? 'Creating…' : 'Create Account' }}
              </button>

              <button
                class="btn landing__cta"
                @click="isSignup = false; errorMsg = ''"
              >
                Back to Login
              </button>
            </template>
          </div>

        </div>

        <div class="landing__carousel" aria-hidden="true">
          <!-- carousel here later -->
        </div>

      </div>
    </div>
  </div>
</template>