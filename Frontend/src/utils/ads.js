const adFiles = import.meta.glob('@/assets/Images/adColumns/*.png', { eager: true })
const adImages = Object.values(adFiles).map(mod => mod.default)

export function getRandomAd() {
  if (!adImages.length) return null
  return adImages[Math.floor(Math.random() * adImages.length)]
}
