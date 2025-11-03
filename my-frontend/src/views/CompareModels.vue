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
    <pre v-if="comparisonResult">{{ comparisonResult }}</pre>
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

// Send the selected models to the backend for comparison
async function compareModels() {
  if (selectedModels.value.length !== 2) return

  try {
    const payload = {
      dataset: selectedDataset.value,
      models: selectedModels.value
    }
    const response = await axios.post('http://localhost:8000/dashboard/modelevaluation', payload, {
      headers: { Authorization: `Bearer ${token}` }
    })
    comparisonResult.value = response.data
  } catch (error) {
    console.error("Failed to compare models:", error)
  }
}

onMounted(fetchDatasets)
</script>
