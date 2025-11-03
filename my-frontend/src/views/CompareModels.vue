<template>
  <div class="compare-page">
    <!-- Dataset Selection -->
    <div class="card">
      <h2>Select Dataset</h2>
      <select v-model="selectedDataset" @change="onDatasetChange">
        <option disabled value="">-- choose dataset --</option>
        <option v-for="dataset in datasets" :key="dataset" :value="dataset">
          {{ dataset }}
        </option>
      </select>
    </div>

    <!-- Model Selection -->
    <div class="card" v-if="availableModels.length">
      <h2>Select Two Models to Compare</h2>
          <select v-model="selectedModels" multiple>
      <option v-for="model in availableModels" :key="model" :value="model">
        {{ model }}
      </option>
    </select>
      <button @click="compareModels" :disabled="selectedModels.length !== 2">
        Compare Models
      </button>
    </div>

    <!-- Comparison Results -->
    <div class="comparison-results" v-if="comparisonResult.length === 2">
      <h2>Model Comparison for Dataset: {{ selectedDataset }}</h2>
      <div class="columns">
        <!-- Column for Model 1 -->
        <div class="model-column">
          <h3>Model 1: {{ comparisonResult[0].model_type }} (ID: {{ comparisonResult[0].model_id }})</h3>
          <div>
            <strong>Configuration:</strong>
            <ul>
              <li v-for="(value, key) in comparisonResult[0].config" :key="key">
                {{ formatKey(key) }}: {{ value }}
              </li>
            </ul>
          </div>
          <div>
            <strong>Metrics:</strong>
            <ul>
              <li v-for="(value, key) in comparisonResult[0].metrics" :key="key">
                {{ formatKey(key) }}: {{ value }}
              </li>
            </ul>
          </div>
        </div>

        <!-- Column for Model 2 -->
        <div class="model-column">
          <h3>Model 2: {{ comparisonResult[1].model_type }} (ID: {{ comparisonResult[1].model_id }})</h3>
          
          <div>
            <strong>Configuration:</strong>
            <ul>
              <li v-for="(value, key) in comparisonResult[1].config" :key="key">
                {{ formatKey(key) }}: {{ value }}
              </li>
            </ul>
          </div>
          <div>
            <strong>Metrics:</strong>
            <ul>
              <li v-for="(value, key) in comparisonResult[1].metrics" :key="key">
                {{ formatKey(key) }}: {{ value }}
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";

const datasets = ref([]);
const selectedDataset = ref("");
const token = localStorage.getItem("token");
const availableModels = ref([]);
const selectedModels = ref([]);
const comparisonResult = ref([]);

// Fetch datasets
async function fetchDatasets() {
  try {
    const response = await axios.get("http://localhost:8000/dashboard/datasets", {
      headers: { Authorization: `Bearer ${token}` },
    });
    datasets.value = response.data.files;
  } catch (error) {
    console.error("Failed to fetch datasets:", error);
  }
}

// Fetch available models when dataset changes
async function onDatasetChange() {
  if (!selectedDataset.value) return;
  try {
    const response = await axios.get("http://localhost:8000/dashboard/datasets/models", {
      params: { filename: selectedDataset.value },
      headers: { Authorization: `Bearer ${token}` },
    });
    availableModels.value = response.data.models;
    console.log(availableModels.value);
    selectedModels.value = [];
  } catch (error) {
    console.error("Failed to fetch models:", error);
  }
}

// Compare selected models
async function compareModels() {
  if (selectedModels.value.length !== 2) return;

  try {
    const modelIds = selectedModels.value.map(m => parseInt(m.split("_").pop()));

const baseUrl = "http://localhost:8000/dashboard/compare_models";

// Use URLSearchParams to correctly handle encoding and the multiple keys
const params = new URLSearchParams();
modelIds.forEach(id => {
    params.append('model_ids', id);
});

// Construct the final URL
const url = `${baseUrl}?${params.toString()}`;
// url will be: "http://localhost:8000/dashboard/compare_models?model_ids=3&model_ids=5"

axios.get(url, {
  headers: {
    Authorization: `Bearer ${localStorage.getItem("token")}`
  }
})
.then(res => {
  comparisonResult.value = res.data
})
.catch(err => console.error(err))

  } catch (error) {
    console.error("Failed to compare models:", error);
  }
}

// Utility to prettify keys
const formatKey = (key) => key.replace(/_/g, " ").toUpperCase();

onMounted(fetchDatasets);
</script>

<style scoped>
.compare-page {
  padding: 20px;
  font-family: Arial, sans-serif;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.card {
  background: #fff;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 6px 20px rgba(0,0,0,0.1);
}

select {
  padding: 8px;
  border-radius: 8px;
  font-size: 1em;
}

button {
  margin-top: 10px;
  padding: 10px 20px;
  background: #667eea;
  color: #fff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}

button:disabled {
  background: #aaa;
  cursor: not-allowed;
}

.comparison-results {
  margin-top: 20px;
}

.columns {
  display: flex;
  gap: 20px;
}

.model-column {
  flex: 1;
  background: #f4f6f8;
  padding: 15px;
  border-radius: 10px;
}

.model-column h3 {
  margin-bottom: 10px;
}

.model-column ul {
  list-style: none;
  padding-left: 0;
}

.model-column ul li {
  margin-bottom: 5px;
}
</style>
