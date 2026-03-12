<script setup>
import '@/assets/profile.css'
import logo from '@/assets/logo.png'
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getUser, updateUser, addAddress, deleteAddress } from '@/utils/api.js'

defineOptions({ name: 'UserProfile' })

const router = useRouter()

const userInfo = ref(null)
const addresses = ref([])
const loading = ref(true)
const errorMsg = ref('')
const submitting = ref(false)

const showUpdateModal = ref(false)
const showPasswordModal = ref(false)
const showAddressModal = ref(false)

const updateFormData = ref({ firstName: '', lastName: '', email: '', password: '' })
const passwordFormData = ref({ newPassword: '', confirmPassword: '' })
const addressFormData = ref({
  full_name: '', line1: '', line2: '', city: '',
  region: '', postal_code: '', country_code: '', phone: ''
})

async function fetchProfile() {
  try {
    loading.value = true
    errorMsg.value = ''
    const data = await getUser()
    userInfo.value = data.info?.[0] ?? null
    addresses.value = data.addresses ?? []
  } catch (e) {
    errorMsg.value = e.message
  } finally {
    loading.value = false
  }
}

onMounted(fetchProfile)

// Update info modal
const openUpdateModal = () => {
  if (!userInfo.value) return
  updateFormData.value = {
    firstName: userInfo.value.FIRST_NAME,
    lastName: userInfo.value.LAST_NAME,
    email: userInfo.value.EMAIL,
    password: ''
  }
  errorMsg.value = ''
  showUpdateModal.value = true
}

const closeUpdateModal = () => { showUpdateModal.value = false }

const submitUpdateForm = async () => {
  try {
    submitting.value = true
    errorMsg.value = ''
    const f = updateFormData.value
    await updateUser(f.email, f.password, f.firstName, f.lastName)
    showUpdateModal.value = false
    await fetchProfile()
  } catch (e) {
    errorMsg.value = e.message
  } finally {
    submitting.value = false
  }
}

// Password modal
const openPasswordModal = () => {
  passwordFormData.value = { newPassword: '', confirmPassword: '' }
  errorMsg.value = ''
  showPasswordModal.value = true
}

const closePasswordModal = () => { showPasswordModal.value = false }

const submitPasswordForm = async () => {
  const p = passwordFormData.value
  if (p.newPassword !== p.confirmPassword) {
    errorMsg.value = 'Passwords do not match'
    return
  }
  try {
    submitting.value = true
    errorMsg.value = ''
    await updateUser(userInfo.value.EMAIL, p.newPassword, userInfo.value.FIRST_NAME, userInfo.value.LAST_NAME)
    showPasswordModal.value = false
  } catch (e) {
    errorMsg.value = e.message
  } finally {
    submitting.value = false
  }
}

// Address modal
const openAddressModal = () => {
  addressFormData.value = {
    full_name: '', line1: '', line2: '', city: '',
    region: '', postal_code: '', country_code: '', phone: ''
  }
  errorMsg.value = ''
  showAddressModal.value = true
}

const closeAddressModal = () => { showAddressModal.value = false }

const submitAddressForm = async () => {
  try {
    submitting.value = true
    errorMsg.value = ''
    await addAddress(addressFormData.value)
    showAddressModal.value = false
    await fetchProfile()
  } catch (e) {
    errorMsg.value = e.message
  } finally {
    submitting.value = false
  }
}

const removeAddress = async (id) => {
  try {
    submitting.value = true
    errorMsg.value = ''
    await deleteAddress(id)
    await fetchProfile()
  } catch (e) {
    errorMsg.value = e.message
  } finally {
    submitting.value = false
  }
}

const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('firstName')
  router.push('/')
}
</script>

<template>
  <div class="profile-container">
    <div v-if="loading" class="profile-loading">Loading profile...</div>

    <template v-else-if="userInfo">
      <!-- Profile header -->
      <div class="profile-header">
        <div class="profile-picture-wrapper">
          <img :src="logo" alt="Profile Picture" class="profile-picture" />
        </div>
        <h1 class="profile-title">{{ userInfo.FIRST_NAME }} {{ userInfo.LAST_NAME }}</h1>
      </div>

      <div class="profile-content">
        <!-- User info -->
        <div class="profile-info">
          <div class="info-group">
            <label class="info-label">First Name:</label>
            <p class="info-value">{{ userInfo.FIRST_NAME }}</p>
          </div>
          <div class="info-group">
            <label class="info-label">Last Name:</label>
            <p class="info-value">{{ userInfo.LAST_NAME }}</p>
          </div>
          <div class="info-group">
            <label class="info-label">Email:</label>
            <p class="info-value">{{ userInfo.EMAIL }}</p>
          </div>
        </div>

        <!-- Addresses -->
        <div class="addresses-section">
          <div class="addresses-header">
            <h2>Addresses</h2>
            <button class="btn btn-primary" @click="openAddressModal">Add Address</button>
          </div>

          <div v-if="addresses.length" class="address-grid">
            <div v-for="addr in addresses" :key="addr.ID" class="address-card">
              <p class="address-name">{{ addr.FULL_NAME }}</p>
              <p>{{ addr.LINE1 }}</p>
              <p v-if="addr.LINE2">{{ addr.LINE2 }}</p>
              <p>{{ addr.CITY }}, {{ addr.REGION }} {{ addr.POSTAL_CODE }}</p>
              <p>{{ addr.COUNTRY_CODE }}</p>
              <p v-if="addr.PHONE">{{ addr.PHONE }}</p>
              <button class="btn btn-danger" @click="removeAddress(addr.ID)" :disabled="submitting">
                Remove
              </button>
            </div>
          </div>
          <p v-else class="info-value">No addresses on file.</p>
        </div>

        <p v-if="errorMsg" class="modal-error">{{ errorMsg }}</p>

        <!-- Action buttons -->
        <div class="profile-actions">
          <button class="btn btn-primary" @click="openUpdateModal">Update Information</button>
          <button class="btn btn-secondary" @click="openPasswordModal">Update Password</button>
          <button class="btn btn-logout" @click="logout">Log Out</button>
        </div>
      </div>

      <!-- Update Information Modal -->
      <div v-if="showUpdateModal" class="modal-overlay" @click="closeUpdateModal">
        <div class="modal" @click.stop>
          <div class="modal-header">
            <h2>Update Information</h2>
            <button class="modal-close" @click="closeUpdateModal">&times;</button>
          </div>
          <form @submit.prevent="submitUpdateForm" class="modal-form">
            <div class="form-group">
              <label for="firstName" class="form-label">First Name:</label>
              <input id="firstName" v-model.trim="updateFormData.firstName" type="text" class="form-input" />
            </div>
            <div class="form-group">
              <label for="lastName" class="form-label">Last Name:</label>
              <input id="lastName" v-model.trim="updateFormData.lastName" type="text" class="form-input" />
            </div>
            <div class="form-group">
              <label for="email" class="form-label">Email:</label>
              <input id="email" v-model.trim="updateFormData.email" type="email" class="form-input" />
            </div>
            <div class="form-group">
              <label for="password" class="form-label">Password:</label>
              <input id="password" v-model="updateFormData.password" type="password" class="form-input" placeholder="Enter current or new password" />
            </div>
            <p v-if="errorMsg" class="modal-error">{{ errorMsg }}</p>
            <div class="modal-actions">
              <button type="button" class="btn btn-secondary" @click="closeUpdateModal">Cancel</button>
              <button type="submit" class="btn btn-primary" :disabled="submitting">
                {{ submitting ? 'Saving...' : 'Save Changes' }}
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- Update Password Modal -->
      <div v-if="showPasswordModal" class="modal-overlay" @click="closePasswordModal">
        <div class="modal" @click.stop>
          <div class="modal-header">
            <h2>Update Password</h2>
            <button class="modal-close" @click="closePasswordModal">&times;</button>
          </div>
          <form @submit.prevent="submitPasswordForm" class="modal-form">
            <div class="form-group">
              <label for="newPassword" class="form-label">New Password:</label>
              <input id="newPassword" v-model="passwordFormData.newPassword" type="password" class="form-input" />
            </div>
            <div class="form-group">
              <label for="confirmPassword" class="form-label">Confirm Password:</label>
              <input id="confirmPassword" v-model="passwordFormData.confirmPassword" type="password" class="form-input" />
            </div>
            <p v-if="errorMsg" class="modal-error">{{ errorMsg }}</p>
            <div class="modal-actions">
              <button type="button" class="btn btn-secondary" @click="closePasswordModal">Cancel</button>
              <button type="submit" class="btn btn-primary" :disabled="submitting">
                {{ submitting ? 'Updating...' : 'Update Password' }}
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- Add Address Modal -->
      <div v-if="showAddressModal" class="modal-overlay" @click="closeAddressModal">
        <div class="modal" @click.stop>
          <div class="modal-header">
            <h2>Add Address</h2>
            <button class="modal-close" @click="closeAddressModal">&times;</button>
          </div>
          <form @submit.prevent="submitAddressForm" class="modal-form">
            <div class="form-group">
              <label for="fullName" class="form-label">Full Name:</label>
              <input id="fullName" v-model.trim="addressFormData.full_name" type="text" class="form-input" />
            </div>
            <div class="form-group">
              <label for="line1" class="form-label">Address Line 1:</label>
              <input id="line1" v-model.trim="addressFormData.line1" type="text" class="form-input" />
            </div>
            <div class="form-group">
              <label for="line2" class="form-label">Address Line 2:</label>
              <input id="line2" v-model.trim="addressFormData.line2" type="text" class="form-input" />
            </div>
            <div class="form-group">
              <label for="city" class="form-label">City:</label>
              <input id="city" v-model.trim="addressFormData.city" type="text" class="form-input" />
            </div>
            <div class="form-group">
              <label for="region" class="form-label">State / Region:</label>
              <input id="region" v-model.trim="addressFormData.region" type="text" class="form-input" />
            </div>
            <div class="form-group">
              <label for="postalCode" class="form-label">Postal Code:</label>
              <input id="postalCode" v-model.trim="addressFormData.postal_code" type="text" class="form-input" />
            </div>
            <div class="form-group">
              <label for="countryCode" class="form-label">Country Code:</label>
              <input id="countryCode" v-model.trim="addressFormData.country_code" type="text" class="form-input" />
            </div>
            <div class="form-group">
              <label for="phone" class="form-label">Phone:</label>
              <input id="phone" v-model.trim="addressFormData.phone" type="text" class="form-input" />
            </div>
            <p v-if="errorMsg" class="modal-error">{{ errorMsg }}</p>
            <div class="modal-actions">
              <button type="button" class="btn btn-secondary" @click="closeAddressModal">Cancel</button>
              <button type="submit" class="btn btn-primary" :disabled="submitting">
                {{ submitting ? 'Adding...' : 'Add Address' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </template>

    <div v-else class="profile-loading">
      <p class="modal-error">{{ errorMsg || 'Unable to load profile.' }}</p>
      <button class="btn btn-primary" @click="fetchProfile">Retry</button>
    </div>
  </div>
</template>
