<script setup>
import { ref, computed } from 'vue'
import { useEasterEgg } from '@/utils/easterEgg.js'

const props = defineProps({ name: { type: String, required: true } })
const { foundCards, markFound, foundCount, isUnlocked, REQUIRED_CARDS } = useEasterEgg()

const alreadyFound = computed(() => foundCards.value.includes(props.name))
const showToast = ref(false)
const toastMsg = ref('')

// Eagerly load all card images (png + jpg) and pick the one matching the name
const cardFiles = {
  ...import.meta.glob('@/assets/Images/Cards/*.png', { eager: true }),
  ...import.meta.glob('@/assets/Images/Cards/*.jpg', { eager: true }),
}
const cardImage = computed(() => {
  const key = Object.keys(cardFiles).find(k => {
    const fileName = k.split('/').pop().replace(/\.(png|jpg)$/i, '')
    return fileName.toLowerCase() === props.name.toLowerCase()
  })
  return key ? cardFiles[key].default : null
})

function handleClick() {
  if (!alreadyFound.value) markFound(props.name)
  const count = foundCount.value
  const total = REQUIRED_CARDS.length
  if (isUnlocked.value) {
    toastMsg.value = `🎉 You found ${props.name}! All ${total} cards found — About Us is now unlocked!`
  } else {
    toastMsg.value = `✨ You found ${props.name}! (${count}/${total} found)`
  }
  showToast.value = true
  setTimeout(() => { showToast.value = false }, 3500)
}
</script>

<template>
  <span class="hidden-card" :class="{ found: alreadyFound }" @click="handleClick" :title="alreadyFound ? `✓ ${name} found` : '?'">
    <span class="hidden-card__inner">
      <img v-if="cardImage" :src="cardImage" :alt="name" class="card-img" />
      <span class="cname">{{ name }}</span>
    </span>
    <Teleport to="body">
      <Transition name="egg-toast">
        <div v-if="showToast" class="egg-toast">{{ toastMsg }}</div>
      </Transition>
    </Teleport>
  </span>
</template>

<style scoped>
.hidden-card {
  display: inline-block;
  cursor: pointer;
  opacity: 0.07;
  transition: opacity 0.25s;
  user-select: none;
  vertical-align: middle;
}
.hidden-card:hover { opacity: 1; }
.hidden-card.found { opacity: 0.55; }
.hidden-card__inner {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  border: 2px solid var(--shadow, #777);
  padding: 4px;
  background: var(--bg-panel, #111);
  box-shadow: 2px 2px 0 var(--shadow, #777);
}
.card-img {
  width: 64px;
  height: auto;
  display: block;
}
.cname {
  font-size: 0.5rem;
  letter-spacing: 1px;
  text-transform: uppercase;
  color: var(--stone, #ccc);
  white-space: nowrap;
}
</style>

<!-- Global (unscoped) so Teleport toast renders correctly -->
<style>
.egg-toast {
  position: fixed;
  bottom: 2rem;
  left: 50%;
  transform: translateX(-50%);
  background: var(--bg-panel, #111);
  border: 3px solid var(--grass, #b5d80d);
  box-shadow: 4px 4px 0 var(--grass, #b5d80d);
  color: var(--grass, #b5d80d);
  padding: 0.75rem 1.75rem;
  font-family: var(--font-head, monospace);
  font-size: 0.85rem;
  letter-spacing: 2px;
  z-index: 9999;
  pointer-events: none;
  white-space: nowrap;
}
.egg-toast-enter-active,
.egg-toast-leave-active { transition: opacity 0.3s, transform 0.3s; }
.egg-toast-enter-from { opacity: 0; transform: translateX(-50%) translateY(1rem); }
.egg-toast-leave-to  { opacity: 0; transform: translateX(-50%) translateY(-0.5rem); }
</style>
