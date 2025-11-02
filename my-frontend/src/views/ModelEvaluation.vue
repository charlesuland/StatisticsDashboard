<template>
  <div>
    <label for="dataset-select">Choose a dataset:</label>
    <select id="dataset-select" v-model="selectedDataset" @change="onFileChange">
      <option disabled value="">-- select a dataset --</option>
      <option v-for="(dataset, index) in datasets" :key="index" :value="dataset">
        {{ dataset }}
      </option>
    </select>

    <p>Selected Dataset: {{ selectedDataset }}</p>
  </div>
    <div>
    <label for="columns-select">Select columns:</label>
    <select id="columns-select" v-model="selectedColumns" multiple>
      <option v-for="(col, index) in columns" :key="index" :value="col">
        {{ col }}
      </option>
    </select>

    <p>Selected Columns: {{ selectedColumns.join(', ') }}</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";

// Reactive array for dropdown
const datasets = ref([])
const columns = ref([])
const selectedColumns = ref([])

// Selected value
const selectedDataset = ref("")

// Fetch the list of datasets from the backend on component mount
async function fetchDatasets() {
  try {
        const response = await axios.get(
            'http://localhost:8000/dashboard/datasets',
        );
        datasets.value = response.data.files;
  } catch (error) {
    console.error("Failed to fetch datasets:", error)
  }
  
}

async function fetchColumns() {
      try {
        const response = await axios.get(
            'http://localhost:8000/dashboard/datasets/columns',
            {
            params: {
                filename: selectedDataset.value,  // key-value pair sent as query string 
            }
  }
);
        
        columns.value = response.data.columns;
  } catch (error) {
    console.error("Failed to fetch columns:", error)
  }
}
async function onFileChange() {
    fetchColumns();
}

onMounted(() => {
  fetchDatasets()
})
</script>
