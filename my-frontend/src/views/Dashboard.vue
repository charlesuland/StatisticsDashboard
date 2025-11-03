<template>
  <div class="dashboard-container">
    <!-- Sidebar -->
    <aside class="sidebar">
      <h2>Statistics Dashboard</h2>
      <nav>
        <router-link to="/dashboard/datasets" class="nav-link">Datasets</router-link>
        <router-link to="/dashboard/modelevaluation" class="nav-link">Model Evaluation</router-link>
        <router-link to="/dashboard/comparemodels" class="nav-link">Compare Models</router-link>
      </nav>
    </aside>

    <!-- Main Content -->
    <main class="main-content">
      <header class="header">
        <h1>Welcome to your Dashboard</h1>
        <p>Explore datasets, evaluate models, and compare results.</p>
      </header>

      <!--<section class="content">
        <router-view />
      </section> -->
    </main>
  </div>
</template>

<style scoped>
/* Full page layout */
.dashboard-container {
  display: flex;
  height: 100vh;
  font-family: 'Arial', sans-serif;
}

/* Sidebar styling */
.sidebar {
  width: 250px;
  background-color: #2c3e50;
  color: #ecf0f1;
  display: flex;
  flex-direction: column;
  padding: 30px 20px;
}

.sidebar h2 {
  font-size: 1.8em;
  margin-bottom: 40px;
  text-align: center;
}

.nav-link {
  display: block;
  color: #ecf0f1;
  text-decoration: none;
  padding: 12px 15px;
  margin-bottom: 10px;
  border-radius: 8px;
  transition: background 0.3s;
}

.nav-link:hover {
  background-color: #34495e;
}

/* Main content styling */
.main-content {
  flex: 1;
  background-color: #f4f6f8;
  padding: 40px;
  overflow-y: auto;
}

.header h1 {
  font-size: 2em;
  margin-bottom: 10px;
  color: #2c3e50;
}

.header p {
  font-size: 1em;
  color: #555;
  margin-bottom: 30px;
}

/* Section styling */
.content {
  background: white;
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
  min-height: 400px;
}

/* Responsive for smaller screens */
@media (max-width: 768px) {
  .dashboard-container {
    flex-direction: column;
  }
  .sidebar {
    width: 100%;
    flex-direction: row;
    justify-content: space-around;
    padding: 20px;
  }
  .nav-link {
    margin-bottom: 0;
  }
  .main-content {
    padding: 20px;
  }
}
</style>
