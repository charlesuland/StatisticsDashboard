<template>
  <div>
    <!-- Dataset selection -->
    <label for="dataset-select">Choose a dataset:</label>
    <select id="dataset-select" v-model="selectedDataset" @change="onDatasetChange">
      <option disabled value="">-- select a dataset --</option>
      <option v-for="dataset in datasets" :key="dataset" :value="dataset">
        {{ dataset }}
      </option>
    </select>

    <!-- Model selection (once dataset is selected) -->
    <div v-if="availableModels.length > 0">
      <label for="model-select">Select two models to compare:</label>
      <select id="model-select" v-model="selectedModels" multiple>
        <option v-for="model in availableModels" :key="model" :value="model">
          {{ model }}
        </option>
      </select>
    </div>

    <!-- Submit button -->
    <button @click="compareModels" :disabled="selectedModels.length !== 2">
      Compare Models
    </button>

    <!-- Show comparison results -->
    <div v-if="comparisonResult">
  <h3>Model Comparison for Dataset: {{ selectedDataset }}</h3>

  <div v-for="(model, index) in comparisonResult" :key="index" class="model-comparison">
    <h4>Model {{ index + 1 }}: {{ model.model_name }}</h4>
    <p><strong>Training Time:</strong> {{ model.training_time }} seconds</p>
    
    <div>
      <strong>Configuration:</strong>
      <ul>
        <li v-for="(value, key) in model.config" :key="key">
          {{ key }}: {{ value }}
        </li>
      </ul>
    </div>

    <div>
      <strong>Metrics:</strong>
      <ul>
        <li v-for="(value, key) in model.metrics" :key="key">
          {{ key }}: {{ value }}
        </li>
      </ul>
    </div>

    <hr />
  </div>
</div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import axios from 'axios'

const datasets = ref([])
const selectedDataset = ref("")
const token = localStorage.getItem("token") // JWT from login
const availableModels = ref([])
const selectedModels = ref([])
const comparisonResult = ref(null)


// Fetch all datasets on mount
async function fetchDatasets() {
  try {
    const response = await axios.get('http://localhost:8000/dashboard/datasets', {
      headers: { Authorization: `Bearer ${token}` }
    })
    datasets.value = response.data.files
  } catch (error) {
    console.error("Failed to fetch datasets:", error)
  }
}

// When user selects a dataset, fetch models run on it
async function onDatasetChange() {
  if (!selectedDataset.value) return
  try {
    const response = await axios.get('http://localhost:8000/dashboard/datasets/models', {
      params: { filename: selectedDataset.value },
      headers: { Authorization: `Bearer ${token}` }
    })
    availableModels.value = response.data.models
    selectedModels.value = [] // reset selection
  } catch (error) {
    console.error("Failed to fetch models for dataset:", error)
  }
}

async function compareModels() {
  if (selectedModels.value.length !== 2) {
    alert("Please select exactly two models to compare.");
    return;
  }

  try {
    const payload = {
      dataset: selectedDataset.value,
      models: selectedModels.value, // array of model names or IDs
    };

    const response = await axios.post(
      "http://localhost:8000/dashboard/compare_models",
      payload,
      {
        headers: { Authorization: `Bearer ${token}` },
      }
    );

    // response should contain an array of two objects with dataset, time, config, metrics
    comparisonResult.value = response.data; 
  } catch (error) {
    console.error("Failed to compare models:", error);
  }
}

onMounted(fetchDatasets)
</script>
