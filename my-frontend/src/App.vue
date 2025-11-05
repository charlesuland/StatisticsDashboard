<script setup>
import router from './router';
import { computed } from "vue";
import { useRoute } from 'vue-router';
import Navbar from './components/Navbar.vue';

const route = useRoute();

const showNavbar = computed(() => route.path !== '/' && route.path !== '/login' && route.path !== '/register');
</script>

<template>
  <Navbar v-if="showNavbar" />

  <main>
    <router-view />
  </main>
</template>

<style scoped></style>
