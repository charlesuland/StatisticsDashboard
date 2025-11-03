<template>
  <div class="login-container">
    <div class="login-card">
      <h2>Login</h2>
      <form @submit.prevent="login">
        <div class="form-group">
          <label>Username</label>
          <input v-model="username" type="text" placeholder="Enter your username" />
        </div>
        <div class="form-group">
          <label>Password</label>
          <input v-model="password" type="password" placeholder="Enter your password" />
        </div>
        <button type="submit" class="login-button">Login</button>
      </form>
      <p v-if="error" class="error">{{ error }}</p>
      <router-link to="/register" class="register-link">Don't have an account? Register</router-link>
    </div>
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

    localStorage.setItem("token", res.data.access_token);
    router.push("/dashboard");
  } catch (err) {
    error.value = "Invalid credentials.";
  }
};
</script>

<style scoped>
/* Full-page centered container */
.login-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #667eea, #764ba2);
  font-family: 'Arial', sans-serif;
}

/* Card for login form */
.login-card {
  background: #fff;
  padding: 40px;
  border-radius: 20px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 15px 40px rgba(0,0,0,0.2);
  text-align: center;
}

/* Header */
.login-card h2 {
  margin-bottom: 30px;
  color: #333;
  font-size: 2em;
}

/* Form groups */
.form-group {
  margin-bottom: 20px;
  text-align: left;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  color: #555;
  font-weight: bold;
}

.form-group input {
  width: 100%;
  padding: 12px 15px;
  border-radius: 10px;
  border: 1px solid #ccc;
  font-size: 1em;
  transition: border 0.3s, box-shadow 0.3s;
}

.form-group input:focus {
  border-color: #667eea;
  box-shadow: 0 0 5px rgba(102, 126, 234, 0.5);
  outline: none;
}

/* Button */
.login-button {
  width: 100%;
  padding: 12px;
  background-color: #667eea;
  color: white;
  font-size: 1em;
  font-weight: bold;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: background 0.3s;
}

.login-button:hover {
  background-color: #5a67d8;
}

/* Error message */
.error {
  color: red;
  margin-top: 15px;
}

/* Register link */
.register-link {
  display: block;
  margin-top: 20px;
  color: #667eea;
  text-decoration: none;
  font-weight: bold;
  transition: color 0.3s;
}

.register-link:hover {
  color: #5a67d8;
}
</style>
