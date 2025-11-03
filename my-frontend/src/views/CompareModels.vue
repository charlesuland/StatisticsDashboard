<template>
  <div class="ml-dashboard-compare">
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

    <div class="right-column">
      <div v-if="comparisonResult && comparisonResult.length" class="card results-card">
        <h2>Model Comparison for Dataset: {{ selectedDataset }}</h2>

        <div class="comparison-grid">
          <div v-for="(model, index) in comparisonResult" :key="index" class="model-card card">
            <h3>Model {{ index + 1 }}</h3>
            <p><strong>Type:</strong> {{ model.model_type }}</p>
            <p><strong>ID:</strong> {{ model.model_id }}</p>
            <p><strong>Training time:</strong> {{ model.training_time ?? 'n/a' }}</p>

            <div>
              <h4>Configuration</h4>
              <div :id="`config-table-${index}`"></div>
            </div>

            <div>
              <h4>Metrics</h4>
              <div :id="`metrics-table-${index}`"></div>
            </div>

            <div v-if="model.metrics && (model.metrics.learning_curve || model.metrics.roc_curve || model.metrics.pr_curve)">
              <h4>Plots</h4>
              <div class="plots">
                <div v-if="model.metrics.roc_curve" :id="`plot-roc-${index}`" class="plot-div"></div>
                <div v-if="model.metrics.pr_curve" :id="`plot-pr-${index}`" class="plot-div"></div>
                <div v-if="model.metrics.learning_curve" :id="`plot-lc-${index}`" class="plot-div"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>




<style scoped>
.ml-dashboard-compare {
  display: grid;
  grid-template-columns: 360px 1fr;
  gap: 18px;
  align-items: start;
  padding: 12px;
}
.card {
  background: var(--card-bg, #ffffff);
  border: 1px solid rgba(0,0,0,0.06);
  border-radius: 8px;
  padding: 12px;
  box-shadow: 0 1px 2px rgba(16,24,40,0.03);
}
.left-column .form-group { margin-bottom: 12px }
.train-btn { background: var(--accent, #2563eb); color: white; padding: 8px 12px; border-radius: 6px; border: none }
.results-card { padding: 16px }
.comparison-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(360px, 1fr)); gap: 12px }
.model-card { min-height: 260px }
.plots { display: flex; gap: 8px; flex-wrap: wrap }
.plot-div { flex: 1 1 280px; min-width: 240px; height: 260px }

/* Make Tabulator tables fit */
.tabulator { font-size: 13px }

.export-btn { background: #0ea5e9; color: white; border: none; padding: 6px 10px; border-radius: 6px; cursor: pointer }
.export-btn:hover { opacity: 0.9 }

</style>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import axios from 'axios'
import Plotly from 'plotly.js-dist-min'
import "tabulator-tables/dist/css/tabulator_simple.css";
import {TabulatorFull as Tabulator} from 'tabulator-tables';

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

function buildTableForObject(obj, containerId) {
  function formatValue(v) {
    if (v === null || v === undefined) return ''
    if (Array.isArray(v)) {
      // Keep arrays readable but avoid huge output
      if (v.length > 20) return JSON.stringify(v.slice(0, 20)) + '...'
      return JSON.stringify(v)
    }
    if (typeof v === 'object') {
      try {
        const s = JSON.stringify(v)
        return s.length > 200 ? s.slice(0, 200) + '...' : s
      } catch (e) {
        return String(v)
      }
    }
    return String(v)
  }

  const rows = Object.keys(obj || {}).map(k => ({ key: k, value: formatValue(obj[k]) }))
  // clear container
  const container = document.getElementById(containerId)
  if (!container) return
  container.innerHTML = ''
  // add small toolbar
  const toolbar = document.createElement('div')
  toolbar.style.display = 'flex'
  toolbar.style.justifyContent = 'flex-end'
  toolbar.style.marginBottom = '6px'
  const exportBtn = document.createElement('button')
  exportBtn.textContent = 'Export CSV'
  exportBtn.className = 'export-btn'
  toolbar.appendChild(exportBtn)
  container.appendChild(toolbar)

  const table = document.createElement('div')
  container.appendChild(table)

  const tab = new Tabulator(table, {
    data: rows,
    layout: 'fitDataFill',
    columns: [
      { title: 'Name', field: 'key', headerFilter: 'input' },
      { title: 'Value', field: 'value' }
    ],
    height: '200px',
    clipboard: true,
  })

  exportBtn.addEventListener('click', () => {
    tab.download('csv', `${containerId}.csv`)
  })
}

function renderModelPlots(model, index) {
  // expecting model.metrics.roc_curve = { fpr:[], tpr:[], auc: number }
  if (model.metrics?.roc_curve) {
    const r = model.metrics.roc_curve
    const trace = {
      x: r.fpr,
      y: r.tpr,
      mode: 'lines',
      name: `ROC (AUC=${(r.auc||0).toFixed(3)})`,
      line: { color: '#1f77b4' }
    }
    const layout = { title: 'ROC Curve', xaxis: { title: 'FPR' }, yaxis: { title: 'TPR' }, margin: { t: 30 } }
    Plotly.newPlot(`plot-roc-${index}`, [trace], layout, { responsive: true })
  }

  if (model.metrics?.pr_curve) {
    const p = model.metrics.pr_curve
    const trace = {
      x: p.recall,
      y: p.precision,
      mode: 'lines',
      name: `PR`,
      line: { color: '#ff7f0e' }
    }
    const layout = { title: 'Precision-Recall', xaxis: { title: 'Recall' }, yaxis: { title: 'Precision' }, margin: { t: 30 } }
    Plotly.newPlot(`plot-pr-${index}`, [trace], layout, { responsive: true })
  }

  if (model.metrics?.learning_curve) {
    const lc = model.metrics.learning_curve
    console.log(lc)
    const traceTrain = { x: lc.train_sizes, y: lc.train_scores_mean, mode: 'lines+markers', name: 'Train' }
    const traceTest = { x: lc.train_sizes, y: lc.test_scores_mean, mode: 'lines+markers', name: 'Test' }
    const layout = { title: 'Learning Curve', xaxis: { title: 'Training set size' }, yaxis: { title: 'Score' }, margin: { t: 30 } }
    Plotly.newPlot(`plot-lc-${index}`, [traceTrain, traceTest], layout, { responsive: true })
  }
}

// Compare two selected models
async function compareModels() {
  if (selectedModels.value.length !== 2) return;

  try {
    const modelIds = selectedModels.value.map(m => parseInt(m.split("_").pop()));

    // Build repeated query params: model_ids=1&model_ids=2
    const params = new URLSearchParams();
    modelIds.forEach(id => params.append('model_ids', String(id)));
    const response = await axios.get("http://localhost:8000/dashboard/compare_models?" + params.toString(), {
      headers: { Authorization: `Bearer ${token}` },
    });

    // backend returns dataset1 and dataset2; normalize to array
    const r = [response.data.dataset1, response.data.dataset2]
    comparisonResult.value = r

    // Wait for DOM to render tables/plots containers
    await nextTick()
    r.forEach((m, i) => {
      buildTableForObject(m.parameters || m.config || {}, `config-table-${i}`)
      buildTableForObject(m.metrics || {}, `metrics-table-${i}`)
      renderModelPlots(m, i)
    })
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
