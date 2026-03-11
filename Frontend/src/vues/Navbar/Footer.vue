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
      <div class="copyright">&copy; 2026 NXTCG —</div>
      <div class="footer-nav">
        <a href="#">Privacy</a>
        <a href="#">Terms</a>
        <a href="#">Contact</a>
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
</style>