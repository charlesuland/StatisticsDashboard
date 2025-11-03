<template>
  <div class="login">
    <h2>Login</h2>
    <form @submit.prevent="login">
      <div>
        <label>Username:</label>
        <input v-model="username" type="text" />
      </div>
      <div>
        <label>Password:</label>
        <input v-model="password" type="password" />
      </div>
      <button type="submit">Login</button>
    </form>
    <p v-if="error" style="color: red">{{ error }}</p>
  </div>
</template>

<script setup>
import axios from "axios";
import { useRouter } from "vue-router";
import { ref } from "vue";

const username = ref("");
const password = ref("");
const error = ref("");
const router = useRouter();

const login = async () => {
  try {
    const res = await axios.post("http://localhost:8000/auth/token", {
      username: username.value,
      password: password.value,
    });

    // Save JWT token
    localStorage.setItem("token", res.data.access_token);

    // Redirect to dashboard
    router.push("/dashboard");
  } catch (err) {
    error.value = "Invalid credentials.";
  }
};
</script>
