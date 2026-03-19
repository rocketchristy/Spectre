<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getCart, removeFromCart, checkout as apiCheckout, getUser, getInventory, addToCart, addAddress } from '@/utils/api.js'

const router = useRouter()

const cartItems = ref([])
const loading = ref(true)
const removing = ref(null)
const errorMsg = ref('')

// Checkout flow
const addresses = ref([])
const billingAddressId = ref('')
const shippingAddressId = ref('')
const checkingOut = ref(false)
const checkoutSuccess = ref(false)

// Add address inline
const showAddAddress = ref(false)
const addingAddress = ref(false)
const addressForm = ref({
  full_name: '', line1: '', line2: '', city: '',
  region: '', postal_code: '', country_code: '', phone: ''
})

// Random booster promo
const promoBooster = ref(null)
const addingPromo = ref(false)

import { getCardImage } from '@/utils/cardImages.js'
import { getRandomAd } from '@/utils/ads.js'
import { getRandomAdRow } from '@/utils/adRows.js'
import HiddenCard from '@/vues/EasterEgg/HiddenCard.vue'

const randomAd = getRandomAd()
const adRow = getRandomAdRow()

async function fetchCart() {
  loading.value = true
  errorMsg.value = ''
  try {
    const data = await getCart()
    cartItems.value = data || []
  } catch (e) {
    errorMsg.value = e.message
  } finally {
    loading.value = false
  }
}

async function fetchAddresses() {
  try {
    const data = await getUser()
    addresses.value = data.addresses || []
    if (addresses.value.length && !billingAddressId.value) {
      billingAddressId.value = addresses.value[0].ID
      shippingAddressId.value = addresses.value[0].ID
    }
  } catch { /* ignore */ }
}

async function fetchPromoBooster() {
  try {
    const allInventory = await getInventory()
    const boosters = allInventory.filter(i =>
      i.QUANTITY_AVAILABLE > 0 &&
      ((i.PRODUCT_NAME || '').toLowerCase().includes('mystery') ||
       (i.PRODUCT_NAME || '').toLowerCase().includes('booster'))
    )
    if (boosters.length) {
      promoBooster.value = boosters[Math.floor(Math.random() * boosters.length)]
    }
  } catch { /* ignore */ }
}

onMounted(() => {
  fetchCart()
  fetchAddresses()
  fetchPromoBooster()
})

const cartTotal = computed(() =>
  cartItems.value.reduce((sum, item) => sum + (item.UNIT_PRICE_CENTS * item.QUANTITY), 0)
)

async function handleRemove(cartItemId) {
  removing.value = cartItemId
  try {
    await removeFromCart(cartItemId)
    cartItems.value = cartItems.value.filter(item => item.CART_ITEM_ID !== cartItemId)
  } catch (e) {
    errorMsg.value = e.message
  } finally {
    removing.value = null
  }
}

async function submitNewAddress() {
  addingAddress.value = true
  errorMsg.value = ''
  try {
    await addAddress(addressForm.value)
    await fetchAddresses()
    showAddAddress.value = false
    addressForm.value = { full_name: '', line1: '', line2: '', city: '', region: '', postal_code: '', country_code: '', phone: '' }
    billingAddressId.value = addresses.value[0].ID
    shippingAddressId.value = addresses.value[0].ID
  } catch (e) {
    errorMsg.value = e.message
  } finally {
    addingAddress.value = false
  }
}

async function handleCheckout() {
  checkingOut.value = true
  errorMsg.value = ''
  try {
    await apiCheckout(billingAddressId.value, shippingAddressId.value)
    checkoutSuccess.value = true
    cartItems.value = []
  } catch (e) {
    errorMsg.value = e.message
  } finally {
    checkingOut.value = false
  }
}

async function addPromoToCart() {
  if (!promoBooster.value) return
  addingPromo.value = true
  try {
    await addToCart(
      promoBooster.value.INVENTORY_ID,
      1,
      promoBooster.value.UNIT_PRICE_CENTS,
      promoBooster.value.CURRENCY_CODE || 'USD'
    )
    promoBooster.value = null
    await fetchCart()
  } catch (e) {
    errorMsg.value = e.message
  } finally {
    addingPromo.value = false
  }
}
</script>

<template>
  <div class="page-with-ad">
  <main class="page-shell">
    <h1 class="page-title">Your Cart</h1>

    <p v-if="loading" class="empty-state">Loading…</p>

    <template v-else>
      <!-- Ad row banner -->
      <div v-if="adRow" class="ad-row-banner">
        <video v-if="adRow.isVideo" :src="adRow.src" autoplay loop muted playsinline class="ad-row-media" />
        <img v-else :src="adRow.src" alt="Advertisement" class="ad-row-media" />
      </div>

      <!-- Checkout success message -->
      <div v-if="checkoutSuccess" class="checkout-success">
        <h2>Order placed successfully!</h2>
        <div class="checkout-success-actions">
          <router-link to="/orders" class="action-btn">View Orders</router-link>
          <router-link to="/store" class="action-btn" style="background: var(--color-background-soft, #1a1a2e);">Continue Shopping</router-link>
        </div>
      </div>

      <div class="cart-layout">
       <div class="cart-items-col">
        <template v-if="cartItems.length">
        <div class="card-list">
          <div v-for="item in cartItems" :key="item.CART_ITEM_ID" class="list-row">
            <span class="list-row__icon">
              <img
                :src="getCardImage(item.PRODUCT_NAME)"
                :alt="item.PRODUCT_NAME"
                class="cart-item-img"
              />
            </span>

            <div class="list-row__info">
              <strong>{{ item.PRODUCT_NAME }}</strong>
              <span class="text-muted">{{ item.MODIFIER_NAME }}</span>
              <span class="text-muted">${{ (item.UNIT_PRICE_CENTS / 100).toFixed(2) }} each × {{ item.QUANTITY }}</span>
            </div>

            <span class="list-row__price">${{ (item.UNIT_PRICE_CENTS * item.QUANTITY / 100).toFixed(2) }}</span>

            <button
              class="btn-icon btn-danger"
              @click="handleRemove(item.CART_ITEM_ID)"
              :disabled="removing === item.CART_ITEM_ID"
              title="Remove"
            >✕</button>
          </div>
        </div>

        <div class="summary-bar">
          <span class="summary-bar__total">Total: <strong>${{ (cartTotal / 100).toFixed(2) }}</strong></span>
        </div>
        </template>

        <template v-else>
          <div class="empty-cart-notice">
            <h2>Your cart is empty</h2>
            <router-link to="/store" class="action-btn">Browse the Store</router-link>
          </div>
        </template>

        <!-- Promo booster -->
        <div v-if="promoBooster" class="promo-section">
          <h3>Why not add a booster?</h3>
          <div class="promo-card">
            <img :src="getCardImage(promoBooster.PRODUCT_NAME)" :alt="promoBooster.PRODUCT_NAME" class="promo-img" />
            <div class="promo-info">
              <strong>{{ promoBooster.PRODUCT_NAME }}</strong>
              <span class="text-muted">${{ (promoBooster.UNIT_PRICE_CENTS / 100).toFixed(2) }}</span>
            </div>
            <button class="action-btn" @click="addPromoToCart" :disabled="addingPromo">
              {{ addingPromo ? 'Adding…' : 'Add to Cart' }}
            </button>
          </div>
        </div>
       </div>

        <!-- Checkout panel (always visible) -->
        <div class="checkout-panel">
          <h2>Checkout</h2>

          <template v-if="addresses.length">
            <form @submit.prevent="handleCheckout" class="checkout-form">
              <div class="form-group">
                <label class="form-label">Billing Address</label>
                <select v-model="billingAddressId" class="form-input">
                  <option v-for="addr in addresses" :key="addr.ID" :value="addr.ID">
                    {{ addr.FULL_NAME }} — {{ addr.LINE1 }}, {{ addr.CITY }}
                  </option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">Shipping Address</label>
                <select v-model="shippingAddressId" class="form-input">
                  <option v-for="addr in addresses" :key="addr.ID" :value="addr.ID">
                    {{ addr.FULL_NAME }} — {{ addr.LINE1 }}, {{ addr.CITY }}
                  </option>
                </select>
              </div>
              <p class="checkout-total">Order Total: <strong>${{ (cartTotal / 100).toFixed(2) }}</strong></p>
              <p v-if="errorMsg" class="modal-error">{{ errorMsg }}</p>
              <div class="checkout-actions">
                <button type="submit" class="action-btn" :disabled="checkingOut">
                  {{ checkingOut ? 'Processing…' : 'Place Order' }}
                </button>
              </div>
            </form>
            <button class="btn-link" @click="showAddAddress = true">
              + Add another address
            </button>
          </template>

          <div v-else class="no-address-notice">
            <p>You need an address to check out.</p>
            <button class="action-btn" @click="showAddAddress = true">Add Address</button>
          </div>
        </div>
      </div>

      <!-- Add Address Modal -->
      <div v-if="showAddAddress" class="modal-overlay" @click="showAddAddress = false">
        <div class="modal" @click.stop>
          <div class="modal-header">
            <h2>Add Address</h2>
            <button class="modal-close" @click="showAddAddress = false">&times;</button>
          </div>
          <form @submit.prevent="submitNewAddress" class="modal-form">
            <div class="form-group">
              <label class="form-label">Full Name</label>
              <input v-model.trim="addressForm.full_name" class="form-input" required />
            </div>
            <div class="form-group">
              <label class="form-label">Address Line 1</label>
              <input v-model.trim="addressForm.line1" class="form-input" required />
            </div>
            <div class="form-group">
              <label class="form-label">Address Line 2</label>
              <input v-model.trim="addressForm.line2" class="form-input" />
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">City</label>
                <input v-model.trim="addressForm.city" class="form-input" required />
              </div>
              <div class="form-group">
                <label class="form-label">State / Region</label>
                <input v-model.trim="addressForm.region" class="form-input" required />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">Postal Code</label>
                <input v-model.trim="addressForm.postal_code" class="form-input" required />
              </div>
              <div class="form-group">
                <label class="form-label">Country Code</label>
                <input v-model.trim="addressForm.country_code" class="form-input" maxlength="3" required />
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">Phone</label>
              <input v-model.trim="addressForm.phone" class="form-input" required />
            </div>
            <p v-if="errorMsg" class="modal-error">{{ errorMsg }}</p>
            <div class="checkout-actions">
              <button type="button" class="btn btn-secondary" @click="showAddAddress = false">Cancel</button>
              <button type="submit" class="action-btn" :disabled="addingAddress">
                {{ addingAddress ? 'Saving…' : 'Save Address' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </template>

    <p v-if="errorMsg && !showAddAddress" class="modal-error" style="text-align:center;margin-top:1rem;">{{ errorMsg }}</p>
  </main>
  <aside v-if="randomAd" class="ad-column">
    <img :src="randomAd" alt="Advertisement" class="ad-img" />
    <div style="margin-top: 0.75rem; text-align: center;">
      <HiddenCard name="Bryce" />
    </div>
  </aside>
  </div>
</template>

<style scoped>
.page-with-ad {
  display: flex;
  gap: 1.5rem;
  max-width: 1200px;
  margin: 0 auto;
  height:100%;
}
.ad-column {
  width: 180px;
  flex-shrink: 0;
  position: sticky;
  top: 50%;
  transform: translateY(-50%);
  align-self: center;
  height: fit-content;
}
.page-shell { flex: 1; min-width: 0; }
.ad-img { width: 100%; border: 3px solid var(--shadow); box-shadow: 4px 4px 0 var(--shadow); }
@media (max-width: 900px) { .ad-column { display: none; } }

.cart-layout {
  display: grid;
  grid-template-columns: 1fr 340px;
  gap: 2rem;
  align-items: start;
}
@media (max-width: 768px) { .cart-layout { grid-template-columns: 1fr; } }

.cart-items-col { min-width: 0; }

.promo-section {
  margin: 1.5rem 0;
  padding: 1rem;
  border: 2px dashed var(--shadow);
  background: rgba(235, 155, 249, 0.05);
}
.promo-section h3 { margin: 0 0 0.75rem; color: var(--shadow); }
.promo-card { display: flex; align-items: center; gap: 1rem; }
.promo-img { width: 60px; height: auto; }
.promo-info { flex: 1; display: flex; flex-direction: column; gap: 0.2rem; }

.checkout-panel {
  position: sticky;
  top: 2rem;
  background: linear-gradient(160deg, var(--bg-card), var(--bg-panel));
  border: 3px solid var(--stone);
  box-shadow: var(--drop-stone);
  padding: 1.5rem;
}
.checkout-panel h2 { margin: 0 0 1rem; color: var(--stone); border-bottom: 2px solid var(--stone); padding-bottom: 0.6rem; }
.checkout-form { display: flex; flex-direction: column; gap: 1rem; }
.checkout-total { text-align: center; font-family: var(--font-head); font-size: 1.3rem; letter-spacing: 2px; margin: 0.75rem 0; color: var(--grass); }
.checkout-actions { display: flex; justify-content: flex-end; gap: 0.75rem; }

.checkout-success { text-align: center; padding: 2rem; margin-bottom: 1.5rem; border: 3px solid var(--grass); box-shadow: var(--drop-grass); }
.checkout-success h2 { color: var(--grass); margin-bottom: 1rem; }
.checkout-success-actions { display: flex; justify-content: center; gap: 1rem; }

.no-address-notice { text-align: center; padding: 1rem 0; color: var(--text-muted); }
.no-address-notice p { margin-bottom: 1rem; }

.cart-item-img { width: 50px; height: auto; }

.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }

.ad-row-banner { margin: 1.5rem 0; border: 3px solid var(--water); box-shadow: 4px 4px 0 var(--water); overflow: hidden; }
.ad-row-media { display: block; width: 100%; height: auto; }
</style>
