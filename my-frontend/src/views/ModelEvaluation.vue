<template>
  <div class="ml-dashboard">
    <!-- Dataset Selection -->
    <div class="card">
      <h2>Dataset Selection</h2>
      <div class="form-group">
        <label for="dataset-select">Choose a dataset:</label>
        <select id="dataset-select" v-model="selectedDataset" @change="onFileChange">
          <option disabled value="">-- select a dataset --</option>
          <option v-for="(dataset, index) in datasets" :key="index" :value="dataset">
            {{ dataset }}
          </option>
        </select>
        <p class="selected">Selected Dataset: {{ selectedDataset }}</p>
      </div>

      <div class="form-group">
        <label for="columns-select">Select columns:</label>
        <select id="columns-select" v-model="selectedColumns" multiple>
          <option v-for="(col, index) in columns" :key="index" :value="col">{{ col }}</option>
        </select>
      </div>

      <div class="form-group">
        <label for="target-column">Target column:</label>
        <select id="target-column" v-model="targetColumn">
          <option disabled value="">-- select target --</option>
          <option v-for="col in columns" :key="col" :value="col">{{ col }}</option>
        </select>
      </div>

      <div class="form-group range-group">
        <label for="testSplit">Test set percentage: {{ testSplit }}%</label>
        <input type="range" id="testSplit" min="10" max="40" v-model="testSplit" />
      </div>
    </div>

    <!-- Model Selection -->
    <div class="card">
      <h2>Model Selection</h2>
      <div class="form-group">
        <label for="model">Choose ML Model:</label>
        <select id="model" v-model="selectedModel">
          <option value="" disabled>Select a model</option>
          <option v-for="model in models" :key="model.value" :value="model.value">{{ model.label }}</option>
        </select>
      </div>

      <!-- Dynamic model parameters -->
      <div v-if="selectedModel" class="params">
        <h3>Parameters for {{ modelMap[selectedModel].label }}</h3>
        <div v-for="param in modelMap[selectedModel].params" :key="param.name" class="param">
          <label :for="param.name">{{ param.label }}:</label>

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
            <option v-for="option in param.options" :key="option" :value="option">{{ option }}</option>
          </select>

          <input
            v-else-if="param.type === 'checkbox'"
            type="checkbox"
            v-model="modelParams[param.name]"
          />
        </div>
      </div>

      <button :disabled="!canSubmit" @click="submitOptions" class="train-btn">Train Model</button>
      <div v-if="errorMessage" class="error-box">{{ errorMessage }}</div>
    </div>

    <!-- Model Results -->
    <div v-if="modelResults" class="card results-card">
      <h2>Model Evaluation Results</h2>

      <!-- Metrics -->
      <section v-if="hasMetrics(modelResults)">
        <h3>Performance Metrics</h3>
        <ul>
          <li><strong>R²:</strong> {{ modelResults.r2 }}</li>
          <li><strong>MSE:</strong> {{ modelResults.mse }}</li>
          <li><strong>MAE:</strong> {{ modelResults.mae }}</li>
        </ul>
      </section>

      <!-- Cross-Validation -->
      <section v-if="modelResults.cv_mean">
        <h3>Cross-Validation (Mean)</h3>
        <ul>
          <li>R² Mean: {{ modelResults.cv_mean.r2_mean }}</li>
          <li>MSE Mean: {{ modelResults.cv_mean.mse_mean }}</li>
          <li>MAE Mean: {{ modelResults.cv_mean.mae_mean }}</li>
        </ul>
      </section>

      <section v-if="modelResults.cv_std">
        <h3>Cross-Validation (Std)</h3>
        <ul>
          <li>R² Std: {{ modelResults.cv_std.r2_std }}</li>
          <li>MSE Std: {{ modelResults.cv_std.mse_std }}</li>
          <li>MAE Std: {{ modelResults.cv_std.mae_std }}</li>
        </ul>
      </section>

      <!-- Feature Importance -->
      <section v-if="modelResults.feature_importance && modelResults.feature_importance.length">
        <h3>Feature Importance</h3>
        <table>
          <thead>
            <tr>
              <th>Feature</th>
              <th>Importance</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="f in modelResults.feature_importance" :key="f.name">
              <td>{{ f.name }}</td>
              <td>{{ f.importance }}</td>
            </tr>
          </tbody>
        </table>
      </section>

      <!-- Learning Curve -->
      <section v-if="modelResults.learning_curve">
        <h3>Learning Curve</h3>
        <div>
          <p><strong>Train Sizes:</strong> {{ modelResults.learning_curve.train_sizes.join(", ") }}</p>
          <p><strong>Train Scores Mean:</strong> {{ modelResults.learning_curve.train_scores_mean.join(", ") }}</p>
          <p><strong>Test Scores Mean:</strong> {{ modelResults.learning_curve.test_scores_mean.join(", ") }}</p>
        </div>
      </section>

      <!-- Plots -->
      <section v-if="modelResults.plots && modelResults.plots.length">
        <h3>Generated Plots</h3>
        <div class="plots">
          <div v-for="plot in modelResults.plots" :key="plot.id" class="plot-card">
            <p>{{ plot.name }}</p>
            <img :src="plot.url" alt="Plot image" />
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.ml-dashboard {
  display: flex;
  flex-direction: column;
  gap: 25px;
  font-family: Arial, sans-serif;
  padding: 20px;
  background-color: #f4f6f8;
}

/* Card layout */
.card {
  background: #fff;
  border-radius: 15px;
  padding: 25px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
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

select, input[type="number"], input[type="range"] {
  padding: 10px;
  border-radius: 8px;
  border: 1px solid #ccc;
  font-size: 1em;
  transition: border 0.3s;
}

select:focus, input:focus {
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
.results-card h2, .results-card h3 {
  margin-bottom: 10px;
  color: #2c3e50;
}

/* Feature table */
table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
}

th, td {
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
  width: 250px;
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
  -webkit-appearance: none;
  width: 100%;
  height: 6px;
  background: #ddd;
  border-radius: 3px;
  outline: none;
}

input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #667eea;
  cursor: pointer;
  transition: background 0.3s;
}

input[type="range"]::-webkit-slider-thumb:hover {
  background: #5a67d8;
}
</style>


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
const errorMessage = ref(null)
const modelResults = ref(null);

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
    if (response.data.error) {
      errorMessage.value = response.data.error;
    } else {
      // Assign the response data to a variable first
      const results = response.data;

      // Fetch plot images if any
      if (results.plots && results.plots.length) {
        await Promise.all(
          results.plots.map(async (plot) => {
            plot.url = await fetchPlotImage(plot.id);
          })
        );
      }

      // Now assign to reactive modelResults
      modelResults.value = results;
      // Fetch plot images for each plot in results
    }
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
const isPrimitive = (val) => val === null || ['string', 'number', 'boolean'].includes(typeof val);
const isObject = (val) => val && typeof val === 'object' && !Array.isArray(val);
const isArrayOfObjects = (val) => Array.isArray(val) && val.length > 0 && val.every(v => typeof v === 'object' && !Array.isArray(v));
const formatKey = (key) => key.replace(/_/g, ' ');
const getPlotUrl  = (plotId) => {
  return `http://localhost:8000/dashboard/plot/${plotId}`;
};
const hasMetrics = (result) => {
  return result && ("r2" in result || "mse" in result || "mae" in result);
};
async function fetchPlotImage(plotId) {
  const response = await axios.get(`http://localhost:8000/dashboard/plot/${plotId}`, {
    responseType: 'blob', // important
    headers: { Authorization: `Bearer ${token}` }
  });

  return URL.createObjectURL(response.data);
}
</script>

