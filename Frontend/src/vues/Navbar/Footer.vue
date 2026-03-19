<script setup>
import { ref } from 'vue'

const showCelebration = ref(false)
const celebrationLines = ref([])

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
          <li><a href="#">Docs</a></li>
          <li><a href="#">Tutorials</a></li>
          <li><a href="#" @click.prevent="onCommunityClick">Community</a></li>
        </ul>
      </div>

      <div class="footer-col footer-links">
        <h4>Company</h4>
        <ul>
          <li><router-link :to="{ name: 'about' }">About</router-link></li>
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
    <!-- Celebration overlay -->
    <div v-if="showCelebration" class="celebration-overlay" @click="closeCelebration">
      <div class="celebration-card" @click.stop>
        <button class="celebration-close" @click="closeCelebration">&times;</button>
        <div class="celebration-emoji">🎉🌍🎊</div>
        <p v-for="(line, i) in celebrationLines" :key="i" class="celebration-text">{{ line }}</p>
        <div class="celebration-emoji">🥳✨🎶</div>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.main-footer {
  background: var(--color-background-soft, #1a1a2e);
  border-top: 1px solid var(--color-border, #333);
  padding: 2rem;
  margin-top: auto;
}

.footer-content {
  display: flex;
  flex-wrap: wrap;
  gap: 2rem;
  max-width: 1200px;
  margin: 0 auto 1.5rem;
}

.footer-info {
  flex: 2;
  min-width: 200px;
}

.footer-logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.footer-logo-image {
  width: 40px;
  height: 40px;
}

.footer-col {
  flex: 1;
  min-width: 120px;
}

.footer-col h4 {
  color: var(--color-heading, #fff);
  margin: 0 0 0.75rem;
}

.footer-links ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.footer-links li {
  margin-bottom: 0.4rem;
}

.footer-links a {
  color: var(--color-text, #ccc);
  text-decoration: none;
}

.footer-links a:hover {
  color: var(--color-heading, #fff);
}

.footer-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  padding-top: 1rem;
  border-top: 1px solid var(--color-border, #333);
  font-size: 0.875rem;
  color: var(--color-text-mute, #888);
}

.footer-nav {
  display: flex;
  gap: 1rem;
}

.footer-nav a {
  color: var(--color-text-mute, #888);
  text-decoration: none;
}

.footer-nav a:hover {
  color: var(--color-heading, #fff);
}

.muted {
  color: var(--color-text-mute, #888);
  margin: 0;
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