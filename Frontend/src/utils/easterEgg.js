import { ref, computed } from 'vue'

const STORAGE_KEY = 'nxtcg_found_cards'
export const REQUIRED_CARDS = ['Claire', 'Ben', 'Bryce', 'Jessalyn', 'Christy']

// Module-level ref so all components share the same reactive state
const foundCards = ref(JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]'))

export function useEasterEgg() {
  function markFound(name) {
    if (!foundCards.value.includes(name)) {
      foundCards.value = [...foundCards.value, name]
      localStorage.setItem(STORAGE_KEY, JSON.stringify(foundCards.value))
    }
  }

  const isUnlocked = computed(() =>
    REQUIRED_CARDS.every(n => foundCards.value.includes(n))
  )

  const foundCount = computed(() =>
    REQUIRED_CARDS.filter(n => foundCards.value.includes(n)).length
  )

  return { foundCards, markFound, isUnlocked, foundCount, REQUIRED_CARDS }
}
