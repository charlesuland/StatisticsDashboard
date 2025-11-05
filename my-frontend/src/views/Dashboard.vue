<template>
  <div class="dashboard-container">
    <!-- Main Content -->
    <main class="main-content">
      <header class="header">
        <h1>Welcome to your Dashboard</h1>
        <p>Explore datasets, evaluate models, and compare results.</p>
      </header>

      <section class="content">
        <div class="widgets-grid">
          <div class="card widget">
            <h3>Your Datasets</h3>
            <p class="muted">Click a dataset to see its models</p>
            <div class="widget-actions">
              <button class="add-dataset-btn" @click="goToAddDataset">Add Dataset</button>
            </div>
            <ul class="dataset-list">
              <li v-for="(d, i) in datasets" :key="d" @click="selectDataset(d)"
                :class="{ selected: d === selectedDataset }">
                <strong>{{ d }}</strong>
                <span class="count">({{ counts[d] ?? '-' }})</span>
              </li>
            </ul>
          </div>

          <div class="card widget">
            <h3>Models for: <span class="dataset-name">{{ selectedDataset || '—' }}</span></h3>
            <p class="muted">Select a dataset to load models</p>
            <div class="widget-actions">
              <button class="train-dataset-btn" @click="goToTrain">Train Model</button>
              <button class="compare-dataset-btn" @click="goToModels">Compare Models</button>
            </div>
            <ul class="model-list">
              <li v-for="m in models" :key="m" class="model-item">
                <router-link :to="`dashboard/model/${selectedDataset}/${m}`">{{ m }}</router-link>
              </li>
              <li v-if="!models.length" class="muted">No models available</li>
            </ul>
          </div>
        </div>
      </section>
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
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  min-height: 400px;
}

.widgets-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px
}

.widget {
  padding: 18px
}

.widget-actions {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.add-dataset-btn, .train-dataset-btn, .compare-dataset-btn {
  padding: 6px 10px;
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}

.add-dataset-btn:hover, .train-dataset-btn:hover, .compare-dataset-btn:hover {
  opacity: 0.95;
}

.dataset-list,
.model-list {
  list-style: none;
  padding: 0;
  margin: 8px 0
}

.dataset-list li,
.model-list li {
  padding: 8px 6px;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  justify-content: space-between
}

.dataset-list li:hover,
.model-list li:hover {
  background: #f0f4ff
}

.dataset-list li.selected {
  background: #e6eefc;
  font-weight: bold
}

.muted {
  color: #666;
  font-size: 0.9em
}

.count {
  color: #999;
  font-weight: normal
}

.model-item a {
  color: #2563eb;
  text-decoration: none
}

.model-item a:hover {
  text-decoration: underline
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

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const datasets = ref([])
const counts = ref({})
const selectedDataset = ref("")
const models = ref([])
const token = localStorage.getItem('token')
const router = useRouter()

async function fetchDatasets() {
  try {
    const res = await axios.get('http://localhost:8000/dashboard/datasets', { headers: { Authorization: `Bearer ${token}` } })
    datasets.value = res.data.files || []
    // simple initial counts placeholder
    datasets.value.forEach(d => counts.value[d] = '-')
  } catch (e) {
    console.error('Failed to fetch datasets', e)
  }
}

async function selectDataset(name) {
  selectedDataset.value = name
  // fetch models for the dataset
  try {
    const res = await axios.get('http://localhost:8000/dashboard/datasets/models', { params: { filename: name }, headers: { Authorization: `Bearer ${token}` } })
    models.value = res.data.models || []
    // update counts if backend provides processed files count
    if (res.data.counts) counts.value[name] = res.data.counts
  } catch (e) {
    console.error('Failed to fetch models for', name, e)
    models.value = []
  }
}

onMounted(fetchDatasets)

function goToAddDataset() {
  // navigate to the dataset upload/list page
  router.push({ path: '/dashboard/datasets' });
}

function goToTrain() {
  // if a dataset is selected, prefill the filename query param
  if (selectedDataset.value) router.push({ path: '/dashboard/modelevaluation', query: { filename: selectedDataset.value } });
  else router.push({ path: '/dashboard/modelevaluation' });
}

function goToModels() {
  // navigate to models page; if dataset selected, include it so page can pre-filter
  if (selectedDataset.value) router.push({ path: '/dashboard/models', query: { dataset: selectedDataset.value } });
  else router.push({ path: '/dashboard/models' });
}
</script>
