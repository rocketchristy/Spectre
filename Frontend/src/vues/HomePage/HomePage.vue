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
.site-header {
  line-height: 1.5;
  text-align: center;
  padding: 2rem 1rem;
}

.logo {
  display: block;
  margin: 0 auto 1rem;
}

.wrapper h1 {
  margin: 0 0 0.5rem;
  font-size: 1.6rem;
  color: var(--color-heading);
}

.subtitle {
  color: var(--color-text);
  margin-bottom: 1rem;
}

.cta .btn {
  display: inline-block;
  margin: 0 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  text-decoration: none;
  border: 1px solid var(--color-border);
  color: inherit;
}

.btn.primary {
  background: var(--vt-light-orange);
  color: white;
  border-color: transparent;
}

.hero {
  padding: 2rem 1rem;
}

.features {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.features article {
  width: 220px;
  border: 1px solid var(--color-border);
  padding: 1rem;
  border-radius: 8px;
  background: var(--color-background-soft);
}

/* Blue header and footer to match request */
.site-header {
  /* make header full-bleed while keeping content centered */
  width: 100vw;
  position: relative;
  left: 50%;
  right: 50%;
  margin-left: -50vw;
  margin-right: -50vw;
  background: var(--vt-c-blue);
  color: var(--vt-c-white);
  padding: 1rem 0.75rem;
}

.site-header .wrapper {
  max-width: 980px;
  margin: 0 auto;
}

.site-header .subtitle,
.site-header .cta .btn {
  color: rgba(255,255,255,0.95);
}

.logo {
  width: 88px;
  height: auto;
}
</style>
