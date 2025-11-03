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

    <!-- Model selection -->
    <div v-if="availableModels.length > 0">
      <label for="model-select">Select two models to compare:</label>
      <select id="model-select" v-model="selectedModels" multiple>
        <option v-for="model in availableModels" :key="model" :value="model">
          {{ model }}
        </option>
      </select>
    </div>

    <button @click="compareModels" :disabled="selectedModels.length !== 2">
      Compare Models
    </button>

    <!-- Results -->
    <div v-if="comparisonResult && comparisonResult.length">
      <h3>Model Comparison for Dataset: {{ selectedDataset }}</h3>

      <div
        v-for="(model, index) in comparisonResult"
        :key="index"
        class="model-comparison"
      >
        <h4>
          Model {{ index + 1 }} ({{ model.model_type }} - ID: {{ model.model_id }})
        </h4>
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

// Fetch available models for selected dataset
async function onDatasetChange() {
  if (!selectedDataset.value) return;
  try {
    const response = await axios.get("http://localhost:8000/dashboard/datasets/models", {
      params: { filename: selectedDataset.value },
      headers: { Authorization: `Bearer ${token}` },
    });
    availableModels.value = response.data.models;
    selectedModels.value = []; // reset selection
  } catch (error) {
    console.error("Failed to fetch models:", error);
  }
}

// Compare two selected models
async function compareModels() {
  if (selectedModels.value.length !== 2) {
    alert("Please select exactly two models to compare.");
    return;
  }

  try {
    // Extract only the IDs (e.g., from "LinearRegression_3" → 3)
    const modelIds = selectedModels.value.map((m) => parseInt(m.split("_").pop()));

    const response = await axios.get("http://localhost:8000/dashboard/compare_models", {
      params: { model_ids: modelIds },
      headers: { Authorization: `Bearer ${token}` },
    });

    comparisonResult.value = [response.data.dataset1, response.data.dataset2];
  } catch (error) {
    console.error("Failed to compare models:", error);
  }
}

onMounted(fetchDatasets);
</script>