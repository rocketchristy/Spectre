import { tempCardData } from './tempCard.js'
import { prices, cardPriceModifiers } from './prices.js'

function pick(arr) {
  return arr[Math.floor(Math.random() * arr.length)]
}

function calculatePrice(card) {
  const base = parseFloat(prices[0].card.replace('$', ''))
  let modifier = 1
  modifier *= cardPriceModifiers.condition[card.condition] || 1
  modifier *= cardPriceModifiers.foil[card.foil] || 1
  modifier *= cardPriceModifiers.language[card.language] || 1
  modifier *= cardPriceModifiers.rarity[card.rarity] || 1
  modifier *= cardPriceModifiers.type[card.type] || 1
  return (base * modifier).toFixed(2)
}

/** Generate individual card instances from tempCardData templates. */
export function generateCards(variantsPerName = 3) {
  const cards = []
  let id = 1

  for (const template of tempCardData) {
    for (const name of template.name) {
      for (let i = 0; i < variantsPerName; i++) {
        const card = {
          id: id++,
          name,
          condition: pick(template.condition),
          foil: pick(template.foil),
          language: pick(template.language),
          rarity: pick(template.rarity),
          type: template.type,
          stock: Math.floor(Math.random() * 101),
        }
        card.price = calculatePrice(card)
        cards.push(card)
      }
    }
  }

  return cards
}

/**
 * Find the template that contains a given card name.
 * Returns the raw template object from tempCardData so the Product page
 * can list ALL possible option values (even those not in generated stock).
 */
export function getTemplateForName(cardName) {
  return tempCardData.find(t => t.name.includes(cardName)) || null
}

// Single shared set of generated cards for this session
export const generatedCards = generateCards(3)
