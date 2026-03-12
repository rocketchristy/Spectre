export const prices = [
    {"pack": "$10",
     "bundle" : "$50",
     "box": "$100",
     "card": "$1"
    },

]
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