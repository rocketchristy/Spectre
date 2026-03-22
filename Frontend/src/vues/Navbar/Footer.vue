<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useEasterEgg } from '@/utils/easterEgg.js'
import docsPdf from '@/assets/docs/placeholder.pdf'
import apiDemoGif from '@/assets/demo/API-Demo.gif'

const showApiDiagram = ref(false)
const showCelebration = ref(false)
const celebrationLines = ref([])

const router = useRouter()
const { isUnlocked } = useEasterEgg()
const showAboutPrompt = ref(false)

function handleAboutClick() {
  if (isUnlocked.value) {
    router.push({ name: 'about' })
  } else {
    showAboutPrompt.value = true
    setTimeout(() => { showAboutPrompt.value = false }, 3500)
  }
}

async function onCommunityClick() {
  try {
    const [r1, r2] = await Promise.all([
      fetch('/hello_world').then(r => r.json()),
      fetch('/hola_mundo').then(r => r.json())
    ])
    celebrationLines.value = [r1, r2]
    showCelebration.value = true
  } catch {
    celebrationLines.value = ['Hello, World!', '¡Hola, Mundo!']
    showCelebration.value = true
  }
}

function closeCelebration() { showCelebration.value = false }
</script>

<template>
  <footer class="main-footer">
    <div class="footer-content">
      <div class="footer-info">
        <div class="footer-logo">
          <img src="../../assets/logo.png" alt="NXT TCG" class="footer-logo-image" />
          <div>
            <strong>NXT TCG</strong>
            <p class="muted">Collect, play, and enjoy.</p>
          </div>
        </div>
      </div>

      <div class="footer-col footer-links">
        <h4>Resources</h4>
        <ul>
          <li><a :href="docsPdf" target="_blank" rel="noopener noreferrer">Docs</a></li>
          <li><a href="#">Tutorials</a></li>
          <li><a href="#" @click.prevent="onCommunityClick">Community</a></li>
        </ul>
      </div>

      <div class="footer-col footer-links">
        <h4>Demo Links</h4>
        <ul>
          <li><a href="#" @click.prevent="showApiDiagram = true">API Diagram</a></li>
          <li><a href="http://127.0.0.1:8000/docs#/default/add_item_spectre_api_cart_item_post" target="_blank" rel="noopener noreferrer">Cart API</a></li>
        </ul>
      </div>

      <div class="footer-col footer-links">
        <h4>Company</h4>
        <ul>
          <li><a href="#" @click.prevent="handleAboutClick">About</a></li>
          <li><a href="#">Careers</a></li>
          <li><a href="#">Contact</a></li>
        </ul>
      </div>
    </div>

    <div class="footer-bottom">
      <div class="copyright">&copy; 2026 NXTCG —</div>
      <div class="footer-nav">
        <a href="#">Privacy</a>
        <a href="#">Terms</a>
        <a href="#">Contact</a>
      </div>
    </div>
    <!-- API Diagram modal -->
    <Teleport to="body">
      <div v-if="showApiDiagram" class="api-modal-overlay" @click.self="showApiDiagram = false">
        <div class="api-modal-card">
          <button class="api-modal-close" @click="showApiDiagram = false">&times;</button>
          <h3>API Diagram</h3>
          <img :src="apiDemoGif" alt="API Demo" class="api-modal-gif" />
        </div>
      </div>
    </Teleport>

    <!-- Celebration overlay -->
    <div v-if="showCelebration" class="celebration-overlay" @click="closeCelebration">
      <div class="celebration-card" @click.stop>
        <button class="celebration-close" @click="closeCelebration">&times;</button>
        <div class="celebration-emoji">🎉🌍🎊</div>
        <p v-for="(line, i) in celebrationLines" :key="i" class="celebration-text">{{ line }}</p>
        <div class="celebration-emoji">🥳✨🎶</div>
      </div>
    </div>
    <Teleport to="body">
      <Transition name="egg-toast">
        <div v-if="showAboutPrompt" class="egg-toast" style="border-color: var(--fire, #c0392b); box-shadow: 4px 4px 0 var(--fire, #c0392b); color: var(--fire, #c0392b);">
          🔒 Find all 5 hidden cards to unlock About Us!
        </div>
      </Transition>
    </Teleport>
  </footer>
</template>

<style scoped>
/* footer outer layout is handled by footer.css — only scoped overrides here */

.main-footer {
  background: var(--bg-panel);
  border-top: 4px solid var(--water);
  box-shadow: 0 -4px 0 var(--shadow);
  padding: 2rem 0 1.25rem;
  margin-top: 3rem;
  font-family: var(--font-body);
  width: 100vw;
  position: relative;
  left: 50%;
  margin-left: -50vw;
}

.api-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.api-modal-card {
  background: var(--bg-panel);
  border: 3px solid var(--water);
  box-shadow: 6px 6px 0 var(--shadow);
  border-radius: 4px;
  padding: 1.5rem;
  position: relative;
  max-width: 90vw;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.api-modal-card h3 {
  margin: 0;
  font-family: var(--font-title);
  color: var(--water);
}

.api-modal-gif {
  max-width: 100%;
  max-height: 75vh;
  object-fit: contain;
  border: 2px solid var(--shadow);
}

.api-modal-close {
  position: absolute;
  top: 0.5rem;
  right: 0.75rem;
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--text);
  line-height: 1;
}

.api-modal-close:hover {
  color: var(--fire, #c0392b);
}

.footer-content {
  display: grid;
  grid-template-columns: 2fr repeat(3, 1fr);
  gap: 2rem 3rem;
  max-width: 920px;
  margin: 0 auto 1.5rem;
  padding: 0 2rem;
  align-items: start;
}

.footer-info { display: flex; flex-direction: column; gap: 0.75rem; }

.footer-logo { display: flex; align-items: center; gap: 1rem; }

.footer-logo-image {
  width: 44px;
  height: 44px;
  object-fit: contain;
  border: 3px solid var(--water);
  box-shadow: 3px 3px 0 var(--shadow);
  padding: 3px;
  background: var(--bg-card);
}

.footer-logo strong {
  font-family: var(--font-pixel);
  font-size: 0.65rem;
  color: var(--stone);
  display: block;
  letter-spacing: 2px;
}

.muted { color: var(--text-muted); font-size: 0.8rem; }

.footer-col { display: flex; flex-direction: column; gap: 0.5rem; }

.footer-col h4 {
  font-family: var(--font-head);
  font-size: 0.95rem;
  color: var(--water);
  letter-spacing: 3px;
  text-transform: uppercase;
  border-bottom: 2px solid var(--water);
  padding-bottom: 0.3rem;
  margin-bottom: 0.25rem;
}

.footer-links ul { list-style: none; padding: 0; margin: 0; }
.footer-links li { margin-bottom: 0.35rem; }

.footer-links a {
  color: var(--neutral);
  text-decoration: none;
  font-size: 0.88rem;
  transition: color 0.1s;
}

.footer-links a:hover { color: var(--grass); background: none; }

.footer-bottom {
  border-top: 3px solid rgba(12, 157, 215, 0.2);
  padding: 1rem 2rem 0;
  max-width: 920px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  font-size: 0.8rem;
  color: var(--text-muted);
}

.footer-nav { display: flex; gap: 1rem; }

.footer-nav a {
  color: var(--text-muted);
  text-decoration: none;
  transition: color 0.1s;
}

.footer-nav a:hover { color: var(--water); background: none; }

@media (max-width: 900px) {
  .footer-content { grid-template-columns: 1fr; gap: 1.5rem; }
  .footer-bottom { flex-direction: column; align-items: center; text-align: center; }
}

/* ── Celebration overlay (Community link) ─── */
.celebration-overlay {
  position: fixed;
  inset: 0;
  background: rgba(7, 0, 8, 0.88);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  animation: fadeIn 0.2s ease;
}

.celebration-card {
  background: linear-gradient(145deg, #1c0028, #110016);
  border: 4px solid var(--stone);
  box-shadow: 8px 8px 0 var(--stone), 0 0 40px rgba(255, 224, 151, 0.2);
  padding: 2.5rem 3rem;
  text-align: center;
  animation: popIn 0.3s ease;
  position: relative;
  max-width: 420px;
  width: 90%;
}

.celebration-close {
  position: absolute;
  top: 6px;
  right: 8px;
  background: var(--neutral);
  border: 2px solid #000;
  color: #000;
  font-size: 1rem;
  font-weight: bold;
  width: 26px;
  height: 22px;
  cursor: pointer;
  font-family: var(--font-head);
  box-shadow: inset -2px -2px 0 rgba(0,0,0,0.4), inset 2px 2px 0 rgba(255,255,255,0.5);
}

.celebration-close:hover { background: var(--fire); color: #fff; border-color: #fff; }

.celebration-emoji { font-size: 2.2rem; margin: 0.4rem 0; }

.celebration-text {
  font-family: var(--font-head);
  font-size: 1.6rem;
  color: var(--stone);
  margin: 0.6rem 0;
  letter-spacing: 3px;
  text-transform: uppercase;
  text-shadow: 3px 3px 0 var(--fire);
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes popIn {
  from { transform: scale(0.6); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

.celebration-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  animation: fadeIn 0.3s ease;
}

.celebration-card {
  background: linear-gradient(135deg, #1a1a2e, #16213e);
  border: 2px solid gold;
  border-radius: 16px;
  padding: 2.5rem 3rem;
  text-align: center;
  box-shadow: 0 0 40px rgba(255, 215, 0, 0.4);
  animation: popIn 0.4s ease;
  position: relative;
}

.celebration-close {
  position: absolute;
  top: 0.5rem;
  right: 0.75rem;
  background: none;
  border: none;
  color: #aaa;
  font-size: 1.5rem;
  cursor: pointer;
}

.celebration-close:hover {
  color: #fff;
}

.celebration-emoji {
  font-size: 2.5rem;
  margin: 0.5rem 0;
}

.celebration-text {
  font-size: 1.75rem;
  font-weight: 700;
  color: gold;
  margin: 0.75rem 0;
  text-shadow: 0 0 12px rgba(255, 215, 0, 0.6);
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes popIn {
  from { transform: scale(0.5); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}
</style>