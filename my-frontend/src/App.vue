<script setup>
import router from './router';
import { computed } from "vue";
import { useRoute } from 'vue-router';
import Navbar from './components/Navbar.vue';

const route = useRoute();

const showNavbar = true;//computed(() => route.path !== '/');
</script>

<template>
  <Navbar v-if="showNavbar"/>
  
  <router-link to="/dashboard">Dashboard</router-link>

  <main>
    <router-view />
  </main>
</template>

<style scoped>

</style>
