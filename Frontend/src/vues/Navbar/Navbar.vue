<script setup>
const props = defineProps({
  msg: {
    type: String,
    default: 'Welcome to NXT TCG',
  },
})
</script>


<template>
  <header class="site-header">
    <img alt="NXT TCG Logo" class="logo" src="./assets/logo.png" width="125" height="125" />

    <div class="wrapper">
  <h1>{{ props.msg }}</h1>
      <p class="subtitle">A small starter homepage built with Vue 3 + Vite.</p>

      <nav class="cta">
        <a class="btn primary" href="#">Get Started</a>
        <a class="btn" href="#">Docs</a>
      </nav>
    </div>
  </header>

  <main class="hero">
    <section class="features">
      
    </section>
  </main>
  
  <footer class="main-footer">
    <div class="footer-content">
      <div class="footer-info">
        <div class="footer-logo">
          <img src="./assets/logo.png" alt="NXT TCG" class="footer-logo-image" />
          <div>
            <strong>NXT TCG</strong>
            <p class="muted">Collect, play, and enjoy.</p>
          </div>
        </div>
        <p class="muted">Small starter site built with Vue 3 and Vite.</p>
      </div>

      <div class="footer-col footer-links">
        <h4>Get started</h4>
        <ul>
          <li><a href="#">Play</a></li>
          <li><a href="#">Download</a></li>
          <li><a href="#">Pricing</a></li>
        </ul>
      </div>

      <div class="footer-col footer-links">
        <h4>Resources</h4>
        <ul>
          <li><a href="#">Docs</a></li>
          <li><a href="#">Tutorials</a></li>
          <li><a href="#">Community</a></li>
        </ul>
      </div>

      <div class="footer-col footer-links">
        <h4>Company</h4>
        <ul>
          <li><a href="#">About</a></li>
          <li><a href="#">Careers</a></li>
          <li><a href="#">Contact</a></li>
        </ul>
      </div>
    </div>

    <div class="footer-bottom">
      <div class="copyright">&copy; 2026 NXT TCG — Built with Vue + Vite</div>
      <div class="footer-nav">
        <a href="#">Privacy</a>
        <a href="#">Terms</a>
        <a href="#">Contact</a>
      </div>
    </div>
  </footer>
</template>

<style scoped>
header {
  line-height: 1.5;
}

.logo {
  display: block;
  margin: 0 auto 2rem;
}

@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }

  .logo {
    margin: 0 2rem 0 0;
  }

  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }
}
</style>
