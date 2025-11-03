<template>
  <header class="navbar">
    <div class="brand">Statistics Dashboard</div>
    <nav class="nav-links">
      <router-link to="/dashboard/datasets" class="nav-link">Datasets</router-link>
      <router-link to="/dashboard/modelevaluation" class="nav-link">Model Evaluation</router-link>
      <router-link to="/dashboard/comparemodels" class="nav-link">Compare Models</router-link>
    </nav>
  </header>
</template>

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

/* Mobile: stack links under brand */
@media (max-width: 768px){
  .navbar{ flex-direction:column; align-items:flex-start }
  .nav-links{ width:100%; flex-direction:column; gap:8px; margin-top:8px }
  .nav-link{ width:100%; padding:10px 12px }
}
</style>
