import './assets/main.css'
import './assets/page.css'
import './assets/footer.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './index.js'

createApp(App).use(router).mount('#app')