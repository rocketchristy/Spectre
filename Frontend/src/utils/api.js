const API_BASE = '/api'

export async function loginUser(email, password) {
  const res = await fetch(`${API_BASE}/login`, {
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
  const res = await fetch(`${API_BASE}/register`, {
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
