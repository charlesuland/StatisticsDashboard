<template>
  <div>
    <!-- Dataset selection -->
    <label for="dataset-select">Choose a dataset:</label>
    <select id="dataset-select" v-model="selectedDataset" @change="onFileChange">
      <option disabled value="">-- select a dataset --</option>
      <option v-for="(dataset, index) in datasets" :key="index" :value="dataset">
        {{ dataset }}
      </option>
    </select>
    <p>Selected Dataset: {{ selectedDataset }}</p>

    <!-- Columns selection -->
    <div>
      <label for="columns-select">Select columns:</label>
      <select id="columns-select" v-model="selectedColumns" multiple>
        <option v-for="(col, index) in columns" :key="index" :value="col">
          {{ col }}
        </option>
      </select>

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

    <!-- Test split -->
    <div>
      <label for="testSplit">Test set percentage: {{ testSplit }}%</label>
      <input type="range" id="testSplit" min="10" max="40" v-model="testSplit" />
    </div>

    <!-- Model selection -->
    <div class="form-group">
      <label for="model">Select ML Model:</label>
      <select id="model" v-model="selectedModel">
        <option value="" disabled>Select a model</option>
        <option v-for="model in models" :key="model.value" :value="model.value">
          {{ model.label }}
        </option>
      </select>
    </div>

    <!-- Dynamic model parameters -->
    <div v-if="selectedModel">
      <h4>Parameters for {{ modelMap[selectedModel].label }}</h4>

      <div v-for="param in modelMap[selectedModel].params" :key="param.name" class="param">
        <label :for="param.name">{{ param.label }}:</label>

        <!-- Show appropriate input based on type -->
        <input
          v-if="param.type === 'number'"
          type="number"
          v-model="modelParams[param.name]"
          :step="param.step || 1"
          :min="param.min"
          :max="param.max"
        />

        <input
          v-else-if="param.type === 'float'"
          type="number"
          v-model="modelParams[param.name]"
          step="0.001"
          :min="param.min"
          :max="param.max"
        />

        <select v-else-if="param.type === 'select'" v-model="modelParams[param.name]">
          <option v-for="option in param.options" :key="option" :value="option">
            {{ option }}
          </option>
        </select>

        <input
          v-else-if="param.type === 'checkbox'"
          type="checkbox"
          v-model="modelParams[param.name]"
        />
      </div>
    </div>

    <!-- Submit button -->
    <button :disabled="!canSubmit" @click="submitOptions">Train Model</button>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, reactive, watch } from "vue";
import axios from "axios";

// Reactive state
const datasets = ref([]);
const columns = ref([]);
const selectedColumns = ref([]);
const targetColumn = ref("");
const testSplit = ref(20);
const selectedDataset = ref("");
const selectedModel = ref("");
const token = localStorage.getItem("token");
const modelParams = reactive({});

// Dataset & column fetching
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

async function fetchColumns() {
  if (!selectedDataset.value) return;
  try {
    const response = await axios.get("http://localhost:8000/dashboard/datasets/columns", {
      params: { filename: selectedDataset.value },
      headers: { Authorization: `Bearer ${token}` },
    });
    columns.value = response.data.columns;
  } catch (error) {
    console.error("Failed to fetch columns:", error);
  }
}

function onFileChange() {
  fetchColumns();
}

onMounted(() => {
  fetchDatasets();
});

// Model options
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

// Map model to parameters
const modelMap = {
  linear_regression: {
    label: "Linear Regression",
    params: [
      {     name: "fit_intercept",      // key sent to backend
    label: "Fit Intercept?",    // label shown in UI
    type: "checkbox",             // boolean input 
    value: true
    },
    ],
  },
  logistic_regression: {
    label: "Logistic Regression",
    params: [
      { name: "penalty", label: "Penalty", type: "select", options: ["l1", "l2", "elasticnet", "none"] },
      { name: "C", label: "Inverse Regularization (C)", type: "float", min: 0.01, max: 1000, step: 0.01 },
      { name: "solver", label: "Solver", type: "select", options: ["lbfgs", "liblinear", "saga", "newton-cg"] },
      { name: "max_iter", label: "Max Iterations", type: "number", min: 1, max: 10000, step: 1 },
    ],
  },
  decision_tree: {
    label: "Decision Tree",
    params: [
      { name: "max_depth", label: "Max Depth", type: "number", min: 1, max: 100 },
      { name: "min_samples_split", label: "Min Samples Split", type: "number", min: 2, max: 100 },
      { name: "classifier", label: "Classifier", type: "checkbox" },
    ],
  },
  random_forest: {
    label: "Random Forest",
    params: [
      { name: "n_estimators", label: "Number of Trees", type: "number", min: 1, max: 1000 },
      { name: "max_depth", label: "Max Depth", type: "number", min: 1, max: 100 },
      { name: "classifier", label: "Classifier", type: "checkbox" },
    ],
  },
  bagging: {
    label: "Bagging",
    params: [
      { name: "n_estimators", label: "Number of Estimators", type: "number", min: 1, max: 100 },
      { name: "max_samples", label: "Max Samples", type: "float", min: 0.1, max: 1.0, step: 0.01 },
      { name: "classifier", label: "Classifier", type: "checkbox" },
    ],
  },
  boosting: {
    label: "Boosting",
    params: [
      { name: "n_estimators", label: "Number of Estimators", type: "number", min: 1, max: 100 },
      { name: "learning_rate", label: "Learning Rate", type: "float", min: 0.01, max: 2.0, step: 0.01 },
      { name: "classifier", label: "Classifier", type: "checkbox" },
    ],
  },
  svm: {
    label: "Support Vector Machine",
    params: [
      { name: "kernel", label: "Kernel", type: "select", options: ["linear", "poly", "rbf", "sigmoid"] },
      { name: "C", label: "C (Regularization)", type: "float", min: 0.01, max: 1000, step: 0.01 },
      { name: "gamma", label: "Gamma", type: "select", options: ["scale", "auto"] },
      { name: "classifier", label: "Classifier", type: "checkbox" },
    ],
  },
  custom_dnn: {
    label: "Custom Neural Network",
    params: [
      { name: "activation", label: "Activation", type: "select", options: ["relu", "identity", "logistic", "tanh"] },
      { name: "solver", label: "Solver", type: "select", options: ["lbfgs", "sgd", "adam"] },
      { name: "learning_rate_init", label: "Learning Rate Init", type: "float", min: 0.0001, max: 1, step: 0.0001 },
      { name: "max_iter", label: "Max Iterations", type: "number", min: 1, max: 10000 },
      { name: "classifier", label: "Classifier", type: "checkbox" },
    ],
  },
};

// Compute if submit is allowed
const canSubmit = computed(() => {
  return selectedModel.value && selectedDataset.value && selectedColumns.value.length > 0 && targetColumn.value;
});

// Submit function
async function submitOptions() {
  try {
    const payload = {
      filename: selectedDataset.value,
      features: selectedColumns.value,
      target: targetColumn.value,
      test_split: testSplit.value,
      model: selectedModel.value,
      params: modelParams,
    };

    const response = await axios.post(
      "http://localhost:8000/dashboard/modelevaluation",
      payload,
      { headers: { Authorization: `Bearer ${token}` } }
    );

    console.log("Backend response:", response.data);
    alert("Training started successfully!");
  } catch (error) {
    console.error("Failed to submit options:", error);
  }
};

// Watch for model change and reset params
watch(selectedModel, (newModel) => {
  if (newModel) {
    Object.keys(modelParams).forEach(key => delete modelParams[key]); // clear previous
    modelMap[newModel].params.forEach(p => {
      if (p.type === "checkbox") modelParams[p.name] = false;
      else if (p.type === "number" || p.type === "float") modelParams[p.name] = p.min || 0;
      else modelParams[p.name] = "";
    });
  }
});
</script>
