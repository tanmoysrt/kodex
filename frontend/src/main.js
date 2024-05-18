import './index.css'

import { createApp } from 'vue'
import router from './router'
import App from './App.vue'

import { frappeRequest, FrappeUI, resourcesPlugin, setConfig, Toast } from 'frappe-ui'

let app = createApp(App)

setConfig('resourceFetcher', frappeRequest)

app.use(FrappeUI)
app.use(router)
app.use(resourcesPlugin)


app.mount('#app')
