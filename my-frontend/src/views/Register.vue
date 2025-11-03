<template>
  <div class="register">
    <h2>Create an Account</h2>
    <form @submit.prevent="registerUser">
      <div>
        <label>Username:</label>
        <input v-model="username" type="text" required />
      </div>
      <div>
        <label>Password:</label>
        <input v-model="password" type="password" required />
      </div>
      <button type="submit">Register</button>
    </form>

    <p v-if="error" style="color:red">{{ error }}</p>
    <p v-if="success" style="color:green">{{ success }}</p>

    <router-link to="/login">Already have an account? Login</router-link>
  </div>
</template>

<script setup>
import axios from "axios";
import { ref } from "vue";
import { useRouter } from "vue-router";

const username = ref("");
const password = ref("");
const error = ref("");
const success = ref("");
const router = useRouter();

const registerUser = async () => {
  error.value = "";
  success.value = "";
  try {
    await axios.post("http://localhost:8000/auth/register", {
      username: username.value,
      password: password.value,
    });
    success.value = "Registration successful! Redirecting to login...";
    setTimeout(() => router.push("/login"), 1500);
  } catch (err) {
    error.value =
      err.response?.data?.detail || "Registration failed. Try another username.";
  }
};
</script>
