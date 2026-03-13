export const prices = [
    {"mystery_single": "$5",
     "mystery_mid" : "$12",
     "mystery_pack": "$35",
     "card": "$1"
    },
]

export const elements = ['Fire', 'Water', 'Grass', 'Earth', 'Ice', 'Shadow', 'Rainbow']

export const elementEmoji = {
  Fire: '🔥', Water: '💧', Grass: '🌿', Earth: '🪨',
  Ice: '❄️', Shadow: '🌑', Rainbow: '🌈'
}

export const mysteryProductTypes = {
  single: { name: 'Mystery Single', cards: 1, priceKey: 'mystery_single' },
  mid:    { name: 'Mystery Mid',    cards: 3, priceKey: 'mystery_mid' },
  pack:   { name: 'Mystery Pack',   cards: 10, priceKey: 'mystery_pack' },
}

export const cardPriceModifiers = {
    "condition": {
        "Mint": 2,
        "Near Mint": 1,
        "Lightplay": .8,
        "Moderate Play": .5
    },
    "foil": {
        "Non-foil": 1,
        "Holofoil": 3,
        "Reverse Holofoil": 4
    },
    "language": {
        "english": 1,
        "japanese": 1.2,
        "australian": 1.5
    },
    "rarity": {
        "Common": 1,
        "Uncommon": 1.5,
        "Rare": 3,
        "Super Rare": 4,
    },
    "type": {
        "character": 2,
        "artifact": 1,
        "lands": 1,
    }
}