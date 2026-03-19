const adRowFiles = import.meta.glob('@/assets/Images/adRows/*', { eager: true })
const adRowMedia = Object.entries(adRowFiles).map(([path, mod]) => ({
  src: mod.default,
  isVideo: path.endsWith('.mp4'),
}))

export function getRandomAdRow() {
  if (!adRowMedia.length) return null
  return adRowMedia[Math.floor(Math.random() * adRowMedia.length)]
}
