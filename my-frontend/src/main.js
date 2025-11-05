import { createApp } from 'vue'
import App from './App.vue'
import router from "./router/index.js"
import './styles/global.css'
import axios from 'axios'

// Add a global axios response interceptor to catch 401 and force logout
axios.interceptors.response.use(
	res => res,
	err => {
		if (err.response && err.response.status === 401) {
			// clear auth and redirect to login
			try { localStorage.removeItem('token'); localStorage.removeItem('username'); } catch(e){}
			// if router is available, navigate to login
			try { router.push('/login'); } catch(e){}
		}
		return Promise.reject(err)
	}
)

// Validate stored token on startup (so a backend restart invalidating tokens logs out the user)
async function init() {
	const token = localStorage.getItem('token')
	if (token) {
		try {
			await axios.get('http://localhost:8000/auth/me', { headers: { Authorization: `Bearer ${token}` } })
			// token valid, continue
		} catch (e) {
			// invalid token -> clear and redirect to login
			try { localStorage.removeItem('token'); localStorage.removeItem('username'); } catch(e){}
			// don't mount the app into protected routes; push to login
			try { router.push('/login'); } catch(e){}
		}
	}

	createApp(App).use(router).mount('#app')
}

init()
