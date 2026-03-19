const adFiles = import.meta.glob('@/assets/Images/adColumns/*.png', { eager: true })
const adImages = Object.values(adFiles).map(mod => mod.default)

export function getRandomAd() {
  if (!adImages.length) return null
  return adImages[Math.floor(Math.random() * adImages.length)]
}

export function getRandomAdPair() {
  if (adImages.length < 2) return [adImages[0] ?? null, adImages[0] ?? null]
  const i = Math.floor(Math.random() * adImages.length)
  let j = Math.floor(Math.random() * (adImages.length - 1))
  if (j >= i) j++
  return [adImages[i], adImages[j]]
}
