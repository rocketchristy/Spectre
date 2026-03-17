const API_BASE = '/spectre/api'

export async function loginUser(email, password) {
  const res = await fetch(`${API_BASE}/user/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.reason || 'Login failed')
  }
  return res.json()
}

export async function registerUser(email, password, firstName, lastName) {
  const res = await fetch(`${API_BASE}/user/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email,
      password,
      first_name: firstName,
      last_name: lastName,
    }),
  })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.reason || 'Registration failed')
  }
  return res.json()
}

export async function getUser() {
  const token = localStorage.getItem('token')
  if (!token) throw new Error('Not logged in')
  const res = await fetch(`${API_BASE}/user`, {
    headers: { token },
  })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.reason || 'Failed to load profile')
  }
  return res.json()
}

export async function updateUser(email, password, fname, lname) {
  const token = localStorage.getItem('token')
  if (!token) throw new Error('Not logged in')
  const res = await fetch(`${API_BASE}/user`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', token },
    body: JSON.stringify({ email, password, fname, lname }),
  })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.reason || 'Update failed')
  }
  return res.json()
}

export async function addAddress(address) {
  const token = localStorage.getItem('token')
  if (!token) throw new Error('Not logged in')
  const res = await fetch(`${API_BASE}/user/address`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', token },
    body: JSON.stringify(address),
  })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.reason || 'Failed to add address')
  }
  return res.json()
}

export async function deleteAddress(index) {
  const token = localStorage.getItem('token')
  if (!token) throw new Error('Not logged in')
  const res = await fetch(`${API_BASE}/user/address/${index}`, {
    method: 'DELETE',
    headers: { token },
  })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.reason || 'Failed to delete address')
  }
}

// ---- Products ----

export async function getProducts() {
  const res = await fetch(`${API_BASE}/products/`)
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.reason || 'Failed to load products')
  }
  return res.json()
}

export async function getProduct(sku) {
  const res = await fetch(`${API_BASE}/products/${encodeURIComponent(sku)}`)
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.reason || 'Failed to load product')
  }
  return res.json()
}

// ---- Inventory ----

export async function getInventory() {
  const res = await fetch(`${API_BASE}/inventory/`)
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.reason || 'Failed to load inventory')
  }
  return res.json()
}

export async function getUserInventory() {
  const token = localStorage.getItem('token')
  if (!token) throw new Error('Not logged in')
  const res = await fetch(`${API_BASE}/inventory/me`, {
    headers: { token },
  })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.reason || 'Failed to load your inventory')
  }
  return res.json()
}

export async function addInventoryItem(sku, quantity, unitPriceCents, currencyCode) {
  const token = localStorage.getItem('token')
  if (!token) throw new Error('Not logged in')
  const res = await fetch(`${API_BASE}/inventory/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', token },
    body: JSON.stringify({ sku, quantity, unitPriceCents, currencyCode }),
  })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.reason || 'Failed to add inventory item')
  }
  return res.json()
}

// ---- Cart ----

export async function getCart() {
  const token = localStorage.getItem('token')
  if (!token) throw new Error('Not logged in')
  const res = await fetch(`${API_BASE}/cart/`, {
    headers: { token },
  })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.reason || 'Failed to load cart')
  }
  return res.json()
}

export async function addToCart(inventoryId, quantity, unitPriceCents, currencyCode) {
  const token = localStorage.getItem('token')
  if (!token) throw new Error('Not logged in')
  const res = await fetch(`${API_BASE}/cart/item`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', token },
    body: JSON.stringify({
      inventory_id: inventoryId,
      quantity,
      unit_price_cents: unitPriceCents,
      currency_code: currencyCode,
    }),
  })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.reason || 'Failed to add to cart')
  }
  return res.json()
}

export async function removeFromCart(inventoryId) {
  const token = localStorage.getItem('token')
  if (!token) throw new Error('Not logged in')
  const res = await fetch(`${API_BASE}/cart/item/${inventoryId}`, {
    method: 'DELETE',
    headers: { token },
  })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.reason || 'Failed to remove from cart')
  }
}
