import { reactive } from 'vue'

// User-created sell listings (kept for backward compatibility)
// Inventory is now managed via the backend API.
export const userListings = reactive([])

let nextId = 200000

export function addListing(listing) {
  userListings.push({
    ...listing,
    id: nextId++,
    seller: localStorage.getItem('firstName') || 'You',
    stock: 1,
  })
}

// All available listings for a given product name (local only)
export function allListingsForName(name) {
  return userListings.filter(c => c.name === name && c.stock > 0)
}
