const cardImageFiles = import.meta.glob('@/assets/Images/Cards/*.png', { eager: true })
const boosterImageFiles = import.meta.glob('@/assets/Images/Boosters/*.png', { eager: true })

export function getCardImage(description) {
  if (!description) return null
  const lowerDesc = description.toLowerCase()
  if (lowerDesc.includes('mystery') || lowerDesc.includes('booster') || lowerDesc.includes('pack')) {
    const searchTerms = lowerDesc.replace('mystery', '').replace('pack', 'booster').trim().split(/\s+/)
    for (const [path, mod] of Object.entries(boosterImageFiles)) {
      const fileName = path.split('/').pop().replace('.png', '').toLowerCase()
      const fileParts = fileName.split('_')
      if (fileParts.length > 1 && fileParts.every(part => searchTerms.includes(part))) return mod.default
    }
    const defaultKey = Object.keys(boosterImageFiles).find(k => k.toLowerCase().endsWith('/booster.png'))
    if (defaultKey) return boosterImageFiles[defaultKey].default
  }
  for (const [path, mod] of Object.entries(cardImageFiles)) {
    const fileName = path.split('/').pop().replace('.png', '')
    if (fileName === description || fileName === description.replace(/\./g, '')) return mod.default
  }
  const blankKey = Object.keys(cardImageFiles).find(k => k.endsWith('Blank.png'))
  return blankKey ? cardImageFiles[blankKey].default : null
}
