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
    <br></br>
    <!-- Single-select for target column -->
      <label for="target-column">Select target column:</label>
      <select id="target-column" v-model="targetColumn">
        <option disabled value="">-- select target --</option>
        <option v-for="col in columns" :key="col" :value="col">
          {{ col }}
        </option>
      </select>

    <p>Selected Columns: {{ selectedColumns.join(', ') }}</p>
    <p>Target Column: {{ targetColumn }}</p>
  </div>
  <div>
    <label for="testSplit">Test set percentage: {{ testSplit }}%</label>
    <input
      type="range"
      id="testSplit"
      min="10"
      max="40"
      v-model="testSplit"
    />
  </div>
      <!-- ML Model Dropdown -->
    <div class="form-group">
      <label for="model">Select ML Model:</label>
      <select id="model" v-model="selectedModel">
        <option value="" disabled>Select a model</option>
        <option v-for="model in models" :key="model.value" :value="model.value">
          {{ model.label }}
        </option>
      </select>
    </div>
        <!-- Submit Button -->
      <button
        :disabled="!canSubmit"
        @click="submitOptions"
      >
        Train Model
      </button>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import axios from "axios";

const targetColumn = ref("");
// Reactive array for dropdown
const datasets = ref([])
const columns = ref([])
const selectedColumns = ref([])
const testSplit = ref(20)
const selectedDataset = ref("")
const selectedModel = ref("")
const token = localStorage.getItem("token"); 

const canSubmit = computed(() => {
  return selectedModel.value && selectedDataset.value && selectedColumns.value.length > 0 && targetColumn.value;
});


// Fetch the list of datasets from the backend on component mount
async function fetchDatasets() {
  try {
    
        const response = await axios.get(
            'http://localhost:8000/dashboard/datasets',
            {
                headers: {
                    Authorization: `Bearer ${token}`, // must be exactly like this
                },
            }
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
            },
            headers: {
                    Authorization: `Bearer ${token}`, // must be exactly like this
                },
            
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

async function submitOptions() {
  try {
    const payload = {
      filename: selectedDataset.value,
      features: selectedColumns.value,
      target: targetColumn.value,
      test_split: testSplit.value,
      model: selectedModel.value
    };

    const response = await axios.post(
      "http://localhost:8000/dashboard/modelevaluation",
      payload,{
      headers: {
                    Authorization: `Bearer ${token}`, // must be exactly like this
                },
            },
      
    );

    console.log("Backend response:", response.data);
    alert("Training started successfully!");
  } catch (error) {
    console.error("Failed to submit options:", error);
  }
}
    const models = [
      { label: "Linear Regression", value: "linear_regression" },
      { label: "Logistic Regression", value: "logistic_regression" },
      { label: "Decision Tree", value: "decision_tree" },
      { label: "Random Forest", value: "random_forest" },
      { label: "Support Vector Machine", value: "svm" },
      { label: "Bagging", value: "bagging" },
      { label: "Boosting", value: "boosting" },
      { label: "Custom Neural Network", value: "custom_dnn" },
    ];
</script>
