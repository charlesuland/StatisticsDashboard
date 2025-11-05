<template>
  <div class="ml-dashboard-compare">
    <div class="selection-row">
      <div class="left-column card">
        <h2>Compare Models</h2>
        <div class="form-group">
          <label for="dataset-select">Choose a dataset:</label>
          <select id="dataset-select" v-model="selectedDataset" @change="onDatasetChange">
            <option disabled value="">-- select a dataset --</option>
            <option v-for="dataset in datasets" :key="dataset" :value="dataset">
              {{ dataset }}
            </option>
          </select>
        </div>

        <div class="form-group" v-if="availableModels.length > 0">
          <label for="model-select">Select two models to compare:</label>
          <select id="model-select" v-model="selectedModels" multiple>
            <option v-for="model in availableModels" :key="model" :value="model">
              {{ model }}
            </option>
          </select>
        </div>

        <button class="train-btn" @click="compareModels" :disabled="selectedModels.length !== 2">
          Compare Models
        </button>
      </div>
    </div>

    <div class="results-row" v-if="comparisonResult && comparisonResult.length">
      <h2 class="results-title">Model Comparison for Dataset: {{ selectedDataset }}</h2>
      <div class="results-grid">
        <div v-for="(model, index) in comparisonResult" :key="index" class="result-col">
          <div class="model-card card">
            <h3>Model {{ index + 1 }}</h3>
            <p><strong>Type:</strong> {{ model.model_type }}</p>
            <p><strong>ID:</strong> {{ model.model_id }}</p>
            <p><strong>Training time:</strong> {{ model.training_time ?? 'n/a' }}</p>
            <ModelMetrics :data="model._metricsData" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>




<style scoped>
.ml-dashboard-compare {
  display: flex;
  flex-direction: column;
  gap: 18px;
  padding: 12px;
  min-height: 100vh;
}

.card {
  background: var(--card-bg, #ffffff);
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 8px;
  padding: 12px;
  box-shadow: 0 1px 2px rgba(16, 24, 40, 0.03);
}

.left-column .form-group {
  margin-bottom: 12px;
}

.selection-row .left-column {
  width: 100%;
}

.selection-row .card {
  width: 100%;
  box-sizing: border-box;
  padding: 16px;
}

.train-btn {
  background: var(--accent, #2563eb);
  color: white;
  padding: 8px 12px;
  border-radius: 6px;
  border: none
}

.results-card {
  padding: 16px
}

.results-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  /* 50/50 side-by-side */
  gap: 16px;
  align-items: start;
}

.results-row {
  flex: 1 1 auto;
  overflow: auto;
}

.model-card {
  min-height: 260px
}

.plots {
  display: flex;
  gap: 8px;
  flex-wrap: wrap
}

.plot-div {
  flex: 1 1 280px;
  min-width: 240px;
  height: 260px
}

/* Make Tabulator tables fit */
.tabulator {
  font-size: 13px
}

.export-btn {
  background: #0ea5e9;
  color: white;
  border: none;
  padding: 6px 10px;
  border-radius: 6px;
  cursor: pointer
}

.export-btn:hover {
  opacity: 0.9
}
</style>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import axios from 'axios'
import ModelMetrics from '../components/ModelMetrics.vue'
import { useRoute } from 'vue-router'

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

function buildResultsFromModel(m) {
  // defensive: if m is falsy or not an object, return an empty results object
  if (!m || typeof m !== 'object') {
    return {
      parameters: {},
      r2: undefined,
      mse: undefined,
      mae: undefined,
      cv_mean: undefined,
      cv_std: undefined,
      feature_importance: [],
      learning_curve: undefined,
      plot_data: []
    }
  }

  // shape the model object into the `data` shape expected by ModelMetrics
  const dr = {
    parameters: m.parameters || m.config || {},
    r2: m.metrics?.r2 ?? m.r2,
    mse: m.metrics?.mse ?? m.mse,
    mae: m.metrics?.mae ?? m.mae,
    cv_mean: m.metrics?.cv_mean ?? m.cv_mean,
    cv_std: m.metrics?.cv_std ?? m.cv_std,
    feature_importance: m.metrics?.feature_importance ?? m.feature_importance ?? [],
    learning_curve: m.metrics?.learning_curve ?? m.learning_curve,
    plot_data: []
  }

  // include metadata
  dr.model_type = m.model_type || m.type || undefined
  dr.training_time = m.training_time || undefined
  dr.dataset = m.dataset || undefined
  dr.is_classifier = m.parameters?.classifier ?? undefined

  // Copy prediction arrays (if present) so ModelMetrics can render predicted vs actual
  // Backend may return predictions under m.predictions or m.metrics.predictions or top-level keys
  const predsSource = m.predictions || m.metrics?.predictions || {};
  if (predsSource && (Array.isArray(predsSource.y_true) || Array.isArray(predsSource.y_test) || Array.isArray(predsSource.y_pred))) {
    dr.predictions = {}
    if (Array.isArray(predsSource.y_true)) dr.predictions.y_true = predsSource.y_true
    if (Array.isArray(predsSource.y_test)) dr.predictions.y_test = predsSource.y_test
    // ensure y_true alias exists for frontend compatibility
    if (!dr.predictions.y_true && dr.predictions.y_test) dr.predictions.y_true = dr.predictions.y_test
    if (Array.isArray(predsSource.y_pred)) dr.predictions.y_pred = predsSource.y_pred
  } else {
    // also support top-level properties on the model object
    if (Array.isArray(m.y_true) || Array.isArray(m.y_test) || Array.isArray(m.y_pred)) {
      dr.predictions = {}
      if (Array.isArray(m.y_true)) dr.predictions.y_true = m.y_true
      if (Array.isArray(m.y_test)) dr.predictions.y_test = m.y_test
      if (!dr.predictions.y_true && dr.predictions.y_test) dr.predictions.y_true = dr.predictions.y_test
      if (Array.isArray(m.y_pred)) dr.predictions.y_pred = m.y_pred
    }
  }

  if (m.metrics?.roc_curve) dr.plot_data.push({ name: 'ROC Curve', key: 'roc_curve', type: 'roc', data: { fpr: m.metrics.roc_curve.fpr, tpr: m.metrics.roc_curve.tpr, auc: m.metrics.roc_auc ?? m.metrics.roc_curve.auc } })
  if (m.metrics?.pr_curve) dr.plot_data.push({ name: 'PR Curve', key: 'pr_curve', type: 'pr', data: { recall: m.metrics.pr_curve.recall, precision: m.metrics.pr_curve.precision, ap: m.metrics.pr_auc ?? m.metrics.pr_curve.ap } })
  if (m.metrics?.learning_curve) dr.plot_data.push({ name: 'Learning Curve', key: 'learning_curve', type: 'learning_curve', data: { train_sizes: m.metrics.learning_curve.train_sizes, train_scores_mean: m.metrics.learning_curve.train_scores_mean, test_scores_mean: m.metrics.learning_curve.test_scores_mean } })

  return dr
}

// Safely parse a model identifier into a numeric id
function parseModelId(m) {
  if (m == null) return NaN;
  if (typeof m === 'number') return m;
  if (typeof m === 'string') {
    // if string contains underscore like "type_123", take last segment
    const parts = m.split('_');
    const last = parts[parts.length - 1];
    if (/^\d+$/.test(last)) return parseInt(last, 10);
    if (/^\d+$/.test(m)) return parseInt(m, 10);
    const asNum = parseInt(m, 10);
    if (!isNaN(asNum)) return asNum;
    return NaN;
  }
  if (typeof m === 'object') {
    if ('id' in m && Number.isInteger(m.id)) return m.id;
    if ('model_id' in m && Number.isInteger(m.model_id)) return m.model_id;
    if (m.id && /^\d+$/.test(String(m.id))) return parseInt(String(m.id), 10);
    if (m.model_id && /^\d+$/.test(String(m.model_id))) return parseInt(String(m.model_id), 10);
  }
  return NaN;
}

// Compare two selected models
async function compareModels() {
  if (!selectedModels.value || selectedModels.value.length !== 2) return;

  try {
    const modelIds = selectedModels.value.map(parseModelId).filter(id => !isNaN(id));
    if (modelIds.length !== 2) {
      console.warn('Could not parse two valid model ids for comparison', selectedModels.value);
      return;
    }

    // Build repeated query params: model_ids=1&model_ids=2
    const params = new URLSearchParams();
    modelIds.forEach(id => params.append('model_ids', String(id)));
    const response = await axios.get("http://localhost:8000/dashboard/compare_models?" + params.toString(), {
      headers: { Authorization: `Bearer ${token}` },
    });

    // backend may return dataset1/dataset2 or an array; normalize to array and filter undefined
    let r = [];
    if (Array.isArray(response.data)) {
      r = response.data.slice();
    } else {
      if (response.data.dataset1) r.push(response.data.dataset1);
      if (response.data.dataset2) r.push(response.data.dataset2);
      // fallback: if keys not present but a top-level object exists, try to use it
      if (r.length === 0 && response.data) r.push(response.data);
    }

    // attach shaped metrics data used by ModelMetrics (guard against undefined)
    r = r.filter(m => m !== undefined && m !== null);
    r.forEach(m => { if (m) m._metricsData = buildResultsFromModel(m); });
    comparisonResult.value = r;
  } catch (error) {
    console.error("Failed to compare models:", error);
  }
}

// Utility to prettify keys
const formatKey = (key) => key.replace(/_/g, " ").toUpperCase();

onMounted(fetchDatasets);
// If model_ids are present in the query, pre-select and run comparison
const route = useRoute()
onMounted(() => {
  const ids = route.query.model_ids;
  if (!ids) return;

  let arr = [];
  if (Array.isArray(ids)) arr = ids.slice();
  else if (typeof ids === 'string') {
    // comma or single-separated string
    arr = ids.split(',').map(s => s.trim()).filter(Boolean);
  }

  if (arr.length === 2) {
    selectedModels.value = arr.map(String);
    if (route.query.dataset) {
      selectedDataset.value = route.query.dataset;
      // load available models for this dataset, then compare
      nextTick(async () => { await onDatasetChange(); compareModels(); });
    } else {
      nextTick(() => compareModels());
    }
  }
})
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
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
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
