<script setup>
import '@/assets/profile.css'
import logo from '@/assets/logo.png'
import { ref } from 'vue'

defineOptions({ name: 'UserProfile' })

// User data
const userData = ref({
  firstName: 'John',
  lastName: 'Doe',
  email: 'john.doe@example.com',
  address: '123 Main St, Springfield, IL 62701'
})

// Modal states
const showUpdateModal = ref(false)
const showPasswordModal = ref(false)

// Form data for updating user info
const updateFormData = ref({
  firstName: userData.value.firstName,
  lastName: userData.value.lastName,
  email: userData.value.email,
  address: userData.value.address
})

// Form data for password
const passwordFormData = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const submitting = ref(false)

// Handle update user information
const openUpdateModal = () => {
  updateFormData.value = { ...userData.value }
  showUpdateModal.value = true
}

const closeUpdateModal = () => {
  showUpdateModal.value = false
}

const submitUpdateForm = async () => {
  try {
    submitting.value = true
    // TODO: Replace with real API call
    await new Promise((r) => setTimeout(r, 300))
    userData.value = { ...updateFormData.value }
    showUpdateModal.value = false
  } finally {
    submitting.value = false
  }
}

// Handle password update
const openPasswordModal = () => {
  passwordFormData.value = {
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  }
  showPasswordModal.value = true
}

const closePasswordModal = () => {
  showPasswordModal.value = false
}

const submitPasswordForm = async () => {
  if (passwordFormData.value.newPassword !== passwordFormData.value.confirmPassword) {
    alert('New passwords do not match!')
    return
  }

  try {
    submitting.value = true
    // TODO: Replace with real API call
    await new Promise((r) => setTimeout(r, 300))
    alert('Password updated successfully!')
    showPasswordModal.value = false
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="profile-container">
    <!-- Profile header with picture -->
    <div class="profile-header">
      <div class="profile-picture-wrapper">
        <img :src="logo" alt="Profile Picture" class="profile-picture" />
      </div>
      <h1 class="profile-title">User Profile</h1>
    </div>

    <!-- Profile information -->
    <div class="profile-content">
      <div class="profile-info">
        <div class="info-group">
          <label class="info-label">First Name:</label>
          <p class="info-value">{{ userData.firstName }}</p>
        </div>

        <div class="info-group">
          <label class="info-label">Last Name:</label>
          <p class="info-value">{{ userData.lastName }}</p>
        </div>

        <div class="info-group">
          <label class="info-label">Email:</label>
          <p class="info-value">{{ userData.email }}</p>
        </div>

        <div class="info-group">
          <label class="info-label">Address:</label>
          <p class="info-value">{{ userData.address }}</p>
        </div>
      </div>

      <!-- Action buttons -->
      <div class="profile-actions">
        <button class="btn btn-primary" @click="openUpdateModal">
          Update User Information
        </button>
        <button class="btn btn-secondary" @click="openPasswordModal">
          Update Password
        </button>
      </div>
    </div>

    <!-- Update User Information Modal -->
    <div v-if="showUpdateModal" class="modal-overlay" @click="closeUpdateModal">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h2>Update User Information</h2>
          <button class="modal-close" @click="closeUpdateModal">&times;</button>
        </div>

        <form @submit.prevent="submitUpdateForm" class="modal-form">
          <div class="form-group">
            <label for="firstName" class="form-label">First Name:</label>
            <input
              id="firstName"
              v-model.trim="updateFormData.firstName"
              type="text"
              class="form-input"
              placeholder="Enter first name"
            />
          </div>

          <div class="form-group">
            <label for="lastName" class="form-label">Last Name:</label>
            <input
              id="lastName"
              v-model.trim="updateFormData.lastName"
              type="text"
              class="form-input"
              placeholder="Enter last name"
            />
          </div>

          <div class="form-group">
            <label for="email" class="form-label">Email:</label>
            <input
              id="email"
              v-model.trim="updateFormData.email"
              type="email"
              class="form-input"
              placeholder="Enter email"
            />
          </div>

          <div class="form-group">
            <label for="address" class="form-label">Address:</label>
            <textarea
              id="address"
              v-model.trim="updateFormData.address"
              class="form-textarea"
              placeholder="Enter address"
            ></textarea>
          </div>

          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="closeUpdateModal">
              Cancel
            </button>
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
            <label for="currentPassword" class="form-label">Current Password:</label>
            <input
              id="currentPassword"
              v-model="passwordFormData.currentPassword"
              type="password"
              class="form-input"
              placeholder="Enter current password"
            />
          </div>

          <div class="form-group">
            <label for="newPassword" class="form-label">New Password:</label>
            <input
              id="newPassword"
              v-model="passwordFormData.newPassword"
              type="password"
              class="form-input"
              placeholder="Enter new password"
            />
          </div>

          <div class="form-group">
            <label for="confirmPassword" class="form-label">Confirm New Password:</label>
            <input
              id="confirmPassword"
              v-model="passwordFormData.confirmPassword"
              type="password"
              class="form-input"
              placeholder="Confirm new password"
            />
          </div>

          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="closePasswordModal">
              Cancel
            </button>
            <button type="submit" class="btn btn-primary" :disabled="submitting">
              {{ submitting ? 'Updating...' : 'Update Password' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
