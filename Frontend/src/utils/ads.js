/**
 * Ad configuration exports.
 * Each ad type exposes an array of items that components can consume.
 * Replace placeholder paths with real asset URLs when available.
 */

/** Static image carousel — rotates through a set of still images */
export const staticImageCarousel = [
  { id: 1, src: '/ads/carousel-1.png', alt: 'Featured set – Wave 1', link: '/store' },
  { id: 2, src: '/ads/carousel-2.png', alt: 'New singles drop',      link: '/store' },
  { id: 3, src: '/ads/carousel-3.png', alt: 'Limited edition bundle', link: '/store' },
]

/** Vertical GIF banner — tall sidebar-style ad */
export const gifBannerVertical = {
  src: '/ads/banner-vertical.gif',
  alt: 'Side banner ad',
  link: '/store',
  width: 160,
  height: 600,
}

/** Horizontal GIF banner — wide leaderboard-style ad */
export const gifBannerHorizontal = {
  src: '/ads/banner-horizontal.gif',
  alt: 'Top banner ad',
  link: '/store',
  width: 728,
  height: 90,
}