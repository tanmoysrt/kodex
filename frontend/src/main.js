import './index.css'

import { createApp } from 'vue'
import router from './router'
import App from './App.vue'

import { frappeRequest, FrappeUI, resourcesPlugin, setConfig, Toast } from 'frappe-ui'
import { createPinia } from 'pinia'

let app = createApp(App)
const pinia = createPinia()
app.use(pinia)
app.use(router)
app.use(FrappeUI)
setConfig('resourceFetcher', frappeRequest)
app.use(resourcesPlugin)

app.mount('#app')
