<template>
  <div class="login-container">
    <div class="login-card">
      <h2>Create an Account</h2>
      <form @submit.prevent="registerUser">
        <div class="form-group">
          <label>Username</label>
          <input v-model="username" type="text" placeholder="Choose a username" required />
        </div>
        <div class="form-group">
          <label>Password</label>
          <input v-model="password" type="password" placeholder="Choose a password" required />
        </div>
        <button type="submit" class="login-button">Register</button>
      </form>
      <p v-if="error" class="error">{{ error }}</p>
      <p v-if="success" class="status">{{ success }}</p>
      <router-link to="/login" class="register-link">Already have an account? Login</router-link>
    </div>
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

<style scoped>
/* reuse login styles for register */
.login-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #667eea, #764ba2);
  font-family: 'Arial', sans-serif;
}

.login-card {
  background: #fff;
  padding: 40px;
  border-radius: 20px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 15px 40px rgba(0,0,0,0.2);
  text-align: center;
}

.login-card h2 {
  margin-bottom: 30px;
  color: #333;
  font-size: 2em;
}

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

.error { color: red; margin-top: 15px }
.status { color: #2ecc71; margin-top: 10px }

.register-link {
  display: block;
  margin-top: 20px;
  color: #667eea;
  text-decoration: none;
  font-weight: bold;
  transition: color 0.3s;
}

.register-link:hover { color: #5a67d8 }
</style>
