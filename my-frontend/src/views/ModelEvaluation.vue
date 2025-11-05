<template>
  <div class="ml-dashboard">
    <div v-if="isTraining" class="training-overlay">
      <div class="training-box">
        <div class="spinner" aria-hidden="true"></div>
        <div class="training-text">Training model — this may take a minute...</div>
      </div>
    </div>
    <div class="left-column">
      <!-- Dataset Selection -->
      <div class="card">
        <h2>Dataset Selection</h2>
        <div class="form-group">
          <label for="dataset-select">Choose a dataset:</label>
          <select id="dataset-select" v-model="selectedDataset" @change="onFileChange" :disabled="isTraining">
            <option disabled value="">-- select a dataset --</option>
            <option v-for="(dataset, index) in datasets" :key="index" :value="dataset">
              {{ dataset }}
            </option>
          </select>
          <p class="selected">Selected Dataset: {{ selectedDataset }}</p>
        </div>

        <div class="form-group">
          <label for="columns-select">Select columns:</label>
          <select id="columns-select" v-model="selectedColumns" multiple :disabled="isTraining">
            <option v-for="(col, index) in columns" :key="index" :value="col">{{ col }}</option>
          </select>
        </div>

        <div class="form-group">
          <label for="target-column">Target column:</label>
          <select id="target-column" v-model="targetColumn" :disabled="isTraining">
            <option disabled value="">-- select target --</option>
            <option v-for="col in columns" :key="col" :value="col">{{ col }}</option>
          </select>
          <small class="type-hint" v-if="targetColumn">Type: {{ targetType }}</small>
        </div>

        <div class="form-group range-group">
          <label for="testSplit">Test set percentage: {{ testSplit }}%</label>
          <input type="range" id="testSplit" min="10" max="40" v-model="testSplit" :disabled="isTraining" />
        </div>
      </div>

      <!-- Model Selection -->
      <div class="card">
        <h2>Model Selection</h2>
        <div class="form-group">
          <label for="model">Choose ML Model:</label>
          <select id="model" v-model="selectedModel" :disabled="isTraining">
            <option value="" disabled>Select a model</option>
            <option v-for="model in models" :key="model.value" :value="model.value">{{ model.label }}</option>
          </select>
        </div>

        <!-- Dynamic model parameters -->
        <div v-if="selectedModel" class="params">
          <h3>Parameters for {{ modelMap[selectedModel].label }}</h3>
          <div v-for="param in modelMap[selectedModel].params" :key="param.name" class="param">
            <label :for="param.name">{{ param.label }}:</label>

            <input v-if="param.type === 'number'" type="number" v-model="modelParams[param.name]"
              :step="param.step || 1" :min="param.min" :max="param.max" />

            <input v-else-if="param.type === 'float'" type="number" v-model="modelParams[param.name]" step="0.001"
              :min="param.min" :max="param.max" />

            <select v-else-if="param.type === 'select'" v-model="modelParams[param.name]">
              <option v-for="option in param.options" :key="option" :value="option">{{ option }}</option>
            </select>

            <input v-else-if="param.type === 'checkbox'" type="checkbox" v-model="modelParams[param.name]" />

            <input v-else-if="param.type === 'text'" type="text" v-model="modelParams[param.name]" />
          </div>
        </div>

        <!-- Classifier truth specification (moved here) -->
        <div v-if="showTruthSpec" class="form-group truth-spec">
          <label>Target truth specification:</label>
          <div class="truth-row">
            <span class="target-name">{{ targetColumn }}</span>
            <select v-model="truthSpec.operator" :disabled="isTraining">
              <option v-for="op in allowedOperators" :key="op" :value="op">{{ op }}</option>
            </select>
            <input v-if="showValueInput" type="text" v-model="truthSpec.value" :disabled="isTraining" />
          </div>
          <small class="type-hint" v-if="targetColumn">Type: {{ targetType }}</small>
          <small class="hint">Treats the target column as true when the expression is satisfied. For numeric columns the input is parsed as number for comparisons.</small>
        </div>

  <button :disabled="!canSubmit || isTraining" @click="submitOptions" class="train-btn">Train Model</button>
        <div v-if="errorMessage" class="error-box">{{ errorMessage }}</div>
      </div>
    </div>

    <div class="right-column">
      <ModelMetrics v-if="modelResults" :data="modelResults" />
    </div>
  </div>
</template>

<style scoped>
.ml-dashboard {
  display: grid;
  grid-template-columns: 360px 1fr;
  gap: 20px 30px;
  font-family: Arial, sans-serif;
  padding: 20px;
  background-color: #f4f6f8;
}

.left-column {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.right-column {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* Card layout */
.card {
  background: #fff;
  border-radius: 15px;
  padding: 25px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

/* Form styling */
.form-group {
  margin-bottom: 20px;
  display: flex;
  flex-direction: column;
}

label {
  font-weight: bold;
  margin-bottom: 8px;
  color: #333;
}

select,
input[type="number"],
input[type="range"] {
  padding: 10px;
  border-radius: 8px;
  border: 1px solid #ccc;
  font-size: 1em;
  transition: border 0.3s;
}

select:focus,
input:focus {
  outline: none;
  border-color: #667eea;
}

/* Checkbox inline */
.param input[type="checkbox"] {
  width: auto;
  margin-left: 5px;
}

/* Train button */
.train-btn {
  padding: 12px 25px;
  background-color: #667eea;
  color: white;
  font-weight: bold;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  margin-top: 15px;
  transition: background 0.3s;
}

.train-btn:disabled {
  background-color: #aaa;
  cursor: not-allowed;
}

.train-btn:hover:not(:disabled) {
  background-color: #5a67d8;
}

/* Error message */
.error-box {
  margin-top: 15px;
  color: red;
  font-weight: bold;
}

/* Results section */
.results-card h2,
.results-card h3 {
  margin-bottom: 10px;
  color: #2c3e50;
}

/* Feature table */
table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
}

th,
td {
  border: 1px solid #ddd;
  padding: 8px;
}

th {
  background-color: #667eea;
  color: white;
  text-align: left;
}

/* Plots */
.plots {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.plot-card {
  background: #f9f9f9;
  border-radius: 10px;
  padding: 10px;
  width: 100%;
  text-align: center;
}

.plot-card img {
  max-width: 100%;
  border-radius: 5px;
  margin-top: 5px;
}

/* Selected dataset text */
.selected {
  margin-top: 5px;
  font-style: italic;
  color: #555;
}

/* Range input styling */
input[type="range"] {
  width: 50%;
  height: 3px;
  background: #ddd;
  border-radius: 100px;
  outline: none;
}

input[type="range"]::-webkit-slider-thumb {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: #667eea;
  cursor: pointer;
  transition: background 0.3s;
}

input[type="range"]::-webkit-slider-thumb:hover {
  background: #5a67d8;
}

/* Training overlay */
.training-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.35);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1200;
}
.training-box { background: white; padding: 20px 28px; border-radius: 10px; display:flex; gap:12px; align-items:center }
.training-text { font-weight: 600 }
.spinner { width: 36px; height: 36px; border-radius: 50%; border: 4px solid #e5e7eb; border-top-color: #667eea; animation: spin 1s linear infinite }
@keyframes spin { to { transform: rotate(360deg) } }
</style>


<script setup>
import { ref, onMounted, computed, reactive, watch, nextTick } from "vue";
import axios from "axios";
import ModelMetrics from '../components/ModelMetrics.vue'
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
const errorMessage = ref(null)
const modelResults = ref(null);
const isTraining = ref(false)
// Truth specification state for classifiers
const truthSpec = reactive({ operator: '==', value: '' });

// Determine column types by fetching the dataset config when columns are loaded
const columnTypes = ref({});

const allowedOpsNumeric = ['>', '>=', '<', '<=', '==', '!='];
const allowedOpsCategorical = ['==', '!='];

const allowedOperators = computed(() => {
  if (!targetColumn.value) return allowedOpsCategorical;
  const t = columnTypes.value[targetColumn.value];
  if (!t) return allowedOpsCategorical;
  if (t.includes('int') || t.includes('float') || t.includes('double') || t.includes('numeric')) return allowedOpsNumeric;
  return allowedOpsCategorical;
});

const showValueInput = computed(() => true);

// Show truth spec UI when the selected model is marked classifier-capable or modelParams.classifier === true
const showTruthSpec = computed(() => {
  // If a specific model param 'classifier' exists, show when it's checked
  if (modelParams.hasOwnProperty('classifier')) return !!modelParams.classifier;
  // Otherwise, show for models that are known classifiers
  const classifierModels = ['logistic_regression', 'decision_tree', 'random_forest', 'svm', 'bagging', 'boosting', 'custom_dnn'];
  return classifierModels.includes(selectedModel.value);
});

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
    // ask backend for column dtype info (from preprocessing config)
    try {
      const resp2 = await axios.get('http://localhost:8000/dashboard/datasets/column_info', {
        params: { filename: selectedDataset.value },
        headers: { Authorization: `Bearer ${token}` }
      });
      columnTypes.value = resp2.data.dtypes || {};
    } catch (e) {
      columnTypes.value = {};
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
      {
        name: "fit_intercept",      // key sent to backend
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
      { name: "max_iter", label: "Max Iterations", type: "number", min: 1000, max: 10000, step: 1 },
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
      { name: "lr", label: "Learning Rate", type: "float", min: 0.0001, max: 1, step: 0.0001, default: .001 },
      { name: "max_iter", label: "Max Iterations", type: "number", min: 1, max: 10000, default: 1000 },
      { name: "hidden_layer_sizes", label: "Hidden Layer Sizes (comma-separated)", type: "text" },
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
    isTraining.value = true
    // prepare params copy and normalize DNN hidden layer sizes (comma-separated string -> number[])
    const paramsToSend = JSON.parse(JSON.stringify(modelParams));
    if (selectedModel.value === 'custom_dnn' && paramsToSend.hidden_layer_sizes && typeof paramsToSend.hidden_layer_sizes === 'string') {
      const parts = paramsToSend.hidden_layer_sizes.split(',').map(s => s.trim()).filter(s => s !== '');
      const parsed = parts.map(p => {
        const n = parseInt(p, 10);
        return Number.isNaN(n) ? null : n;
      }).filter(x => x !== null);
      paramsToSend.hidden_layer_sizes = parsed;
    }

    const payload = {
      filename: selectedDataset.value,
      features: selectedColumns.value,
      target: targetColumn.value,
      test_split: testSplit.value,
      model: selectedModel.value,
      params: paramsToSend,
      truth_spec: (showTruthSpec.value && truthSpec && truthSpec.operator) ? { ...truthSpec } : undefined,
    };

    const response = await axios.post(
      "http://localhost:8000/dashboard/modelevaluation",
      payload,
      { headers: { Authorization: `Bearer ${token}` } }
    );

    console.log("Backend response:", response.data);
    if (response.data.error) {
      errorMessage.value = response.data.error;
    } else {
      // Assign the response data to a variable first
      const results = response.data;

      // Assign results; ModelMetrics component will render tables and plots
      modelResults.value = results;
    }
  } catch (error) {
    console.error("Failed to submit options:", error);
  } finally {
    isTraining.value = false
  }
};



// Watch for model change and reset params
watch(selectedModel, (newModel) => {
  if (newModel) {
    // clear previous
    Object.keys(modelParams).forEach(key => delete modelParams[key]);
    modelMap[newModel].params.forEach(p => {
      // If an explicit default is provided, use it
      if (p.default !== undefined) {
        modelParams[p.name] = p.default;
        return;
      }

      // For select types, choose the first option as the default (if available)
      if (p.type === "select") {
        modelParams[p.name] = (p.options && p.options.length) ? p.options[0] : "";
        return;
      }

      if (p.type === "checkbox") {
        modelParams[p.name] = false;
        return;
      }

      if (p.type === "number" || p.type === "float") {
        modelParams[p.name] = p.min !== undefined ? p.min : 0;
        return;
      }

      // fallback for text/other types
      modelParams[p.name] = "";
    });
  }
});

watch(targetColumn, (newTarget) => {
  // reset truthSpec when target changes
  truthSpec.operator = '==';
  truthSpec.value = '';
});

watch(allowedOperators, (ops) => {
  if (!ops.includes(truthSpec.operator)) {
    truthSpec.operator = ops[0] || '==';
  }
});

const targetType = computed(() => {
  if (!targetColumn.value) return 'unknown';
  const t = columnTypes.value[targetColumn.value];
  if (!t) return 'unknown';
  return t;
});

</script>
