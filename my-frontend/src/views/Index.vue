<template>
  <div class="landing-container">
    <div class="card">
      <h1>Statistics Dashboard</h1>
      <h3>Charles Uland and Sylva Ford</h3>
      <p>Access all your statistics and machine learning insights in one place.</p>
      <router-link to="/login" class="login-button">Log In</router-link>
    </div>
  </div>
</template>

<style scoped>
/* Full-screen centered container with a gradient background */
.landing-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #4e9af1, #667eea);
  font-family: Arial, sans-serif;
}

/* Card styling */
.card {
  background-color: white;
  padding: 40px;
  border-radius: 20px;
  text-align: center;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  max-width: 400px;
  width: 90%;
}

.card h1 {
  font-size: 2.5em;
  margin-bottom: 10px;
  color: #333;
}

.card h3 {
  font-weight: normal;
  margin-bottom: 20px;
  color: #555;
}

.card p {
  color: #666;
  margin-bottom: 30px;
  line-height: 1.5;
}

/* Button styling */
.login-button {
  display: inline-block;
  padding: 12px 30px;
  background-color: #4e9af1;
  color: white;
  font-weight: bold;
  border-radius: 50px;
  text-decoration: none;
  transition: background 0.3s;
}

.login-button:hover {
  background-color: #3b7dd8;
}
</style>
