import { createApp } from 'vue';
import App from './App.vue';
import axios from 'axios';
import router from './router';
import store from './store'; // Import Vuex store

// Function to get CSRF token from cookies
function getCSRFToken() {
  let csrfToken = null;
  const cookieMatch = document.cookie.match(/csrftoken=([\w-]+)/);
  if (cookieMatch) {
    csrfToken = cookieMatch[1];
  }
  return csrfToken;
}

// Set default axios headers for CSRF token
axios.defaults.headers.common['X-CSRFToken'] = getCSRFToken();

const app = createApp(App);
app.config.globalProperties.$axios = axios;

app.use(router);
app.use(store); // Use the Vuex store

app.mount('#app');
