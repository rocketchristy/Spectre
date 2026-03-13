import { reactive } from 'vue'
import { generatedCards } from './generateCards.js'

// User-created sell listings (frontend-only until backend is wired)
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

// All available cards: generated inventory + user listings
export function allListingsForName(name) {
  const generated = generatedCards.filter(c => c.name === name && c.stock > 0)
  const user = userListings.filter(c => c.name === name && c.stock > 0)
  return [...generated, ...user]
}
