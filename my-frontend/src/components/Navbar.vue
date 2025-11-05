<template>
  <header class="navbar">
    <div class="left">
      <div class="brand"><router-link class="nav-link" to="/dashboard">Dashboard</router-link></div>
    </div>
    <div class="right">
      <nav class="nav-links">
        <router-link to="/dashboard/datasets" class="nav-link">Datasets</router-link>
        <router-link to="/dashboard/models" class="nav-link">Models</router-link>
      </nav>
      <div class="user">
        <div class="username-wrapper">
          <button class="username" @click="toggleMenu">{{ usernameDisplay }}</button>
          <div v-if="showMenu" class="user-menu">
            <button class="menu-item" @click="logout">Logout</button>
          </div>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

const router = useRouter();
const usernameDisplay = ref('Guest');
const showMenu = ref(false);

async function fetchUser() {
  const token = localStorage.getItem('token');
  if (!token) return;
  try {
    const r = await axios.get('http://localhost:8000/auth/me', { headers: { Authorization: `Bearer ${token}` } });
    usernameDisplay.value = r.data.username || r.data.user || 'Guest';
  } catch (e) {
    // ignore and keep Guest
  }
}

function toggleMenu() { showMenu.value = !showMenu.value }

function logout() {
  localStorage.removeItem('token');
  localStorage.removeItem('username');
  showMenu.value = false;
  router.push('/login');
}

onMounted(fetchUser);
</script>

<style scoped>
.navbar{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:16px;
  padding: 14px 20px;
  background: #2c3e50;
  color: #ecf0f1;
}
.brand{
  font-size:1.25rem;
  font-weight:700;
}
.left{ display:flex; align-items:center }
.right{ display:flex; align-items:center; gap:16px }
.nav-links{
  display:flex;
  gap:12px;
  align-items:center;
}
.nav-link{
  color: #ecf0f1;
  text-decoration: none;
  padding: 8px 12px;
  border-radius: 8px;
  transition: background 0.2s;
}
.nav-link:hover{
  background: #34495e;
}
.user{ color: #ecf0f1; background: rgba(255,255,255,0.03); padding: 8px 12px; border-radius:8px }
.username{ font-weight:600; background: transparent; border: none; color: inherit; cursor: pointer }
.username-wrapper{ position: relative }
.user-menu{ position: absolute; right: 0; top: calc(100% + 8px); background: #fff; color: #333; border-radius: 8px; box-shadow: 0 8px 20px rgba(0,0,0,0.15); padding: 8px; z-index:50 }
.user-menu .menu-item{ display:block; background:transparent; border:none; padding:8px 12px; width:100%; text-align:left; cursor:pointer }
.user-menu .menu-item:hover{ background:#f2f2f2 }

/* Mobile: stack links under brand */
@media (max-width: 768px){
  .navbar{ flex-direction:column; align-items:flex-start }
  .nav-links{ width:100%; flex-direction:column; gap:8px; margin-top:8px }
  .nav-link{ width:100%; padding:10px 12px }
}
</style>
