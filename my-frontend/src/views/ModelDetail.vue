<template>
  <div class="model-detail">
    <div class="card">
      <h2>Model Detail</h2>
      <p><strong>Dataset:</strong> {{ dataset }}</p>
      <p><strong>Model ID:</strong> {{ modelId }}</p>
      <p v-if="meta.created_at"><strong>Trained at:</strong> {{ meta.created_at }}</p>

      <h3>Parameters</h3>
      <div id="params-table"></div>

      <h3>Metrics</h3>
      <div id="metrics-table"></div>

      <h3 v-if="plotData.length">Plots</h3>
      <div class="plots" v-if="plotData.length">
        <div v-for="(pd, idx) in plotData" :key="pd.key" class="plot-card">
          <p>{{ pd.name }}</p>
          <div :id="`plot-${idx}`" class="plot-div"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import axios from 'axios'
import Plotly from 'plotly.js-dist-min'
import "tabulator-tables/dist/css/tabulator_simple.css";
import { TabulatorFull as Tabulator } from 'tabulator-tables';

const props = defineProps({ dataset: String, modelId: [String, Number] })
const dataset = props.dataset
const modelId = props.modelId
const meta = ref({})
const plotData = ref([])
const token = localStorage.getItem('token')

async function fetchModel() {
  try {
    const res = await axios.get(`http://localhost:8000/dashboard/models/${modelId}`, { headers: { Authorization: `Bearer ${token}` } })
    meta.value = res.data || {}

    // metrics and parameters
    await nextTick()
    buildTableForObject(meta.value.parameters || {}, 'params-table')
    buildTableForObject(meta.value.metrics || {}, 'metrics-table')

    // try to render plots from metrics if present
    const pd = []
    if (meta.value.metrics?.roc_curve) pd.push({ name: 'ROC Curve', key: 'roc_curve', type: 'roc', data: { fpr: meta.value.metrics.roc_curve.fpr, tpr: meta.value.metrics.roc_curve.tpr, auc: meta.value.metrics.roc_auc } })
    if (meta.value.metrics?.pr_curve) pd.push({ name: 'PR Curve', key: 'pr_curve', type: 'pr', data: { recall: meta.value.metrics.pr_curve.recall, precision: meta.value.metrics.pr_curve.precision, ap: meta.value.metrics.pr_auc } })
    if (meta.value.metrics?.learning_curve) pd.push({ name: 'Learning Curve', key: 'learning_curve', type: 'learning_curve', data: { train_sizes: meta.value.metrics.learning_curve.train_sizes, train_scores_mean: meta.value.metrics.learning_curve.train_scores_mean, test_scores_mean: meta.value.metrics.learning_curve.test_scores_mean } })

    plotData.value = pd
    await nextTick()
    plotData.value.forEach((p, i) => renderPlot(p, i))

  } catch (e) {
    console.error('Failed to fetch model', e)
  }
}

function buildTableForObject(obj, containerId) {
  const rows = Object.keys(obj || {}).map(k => ({ key: k, value: stringify(obj[k]) }))
  const container = document.getElementById(containerId)
  if (!container) return
  container.innerHTML = ''
  const tableDiv = document.createElement('div')
  container.appendChild(tableDiv)
  new Tabulator(tableDiv, { data: rows, layout: 'fitDataFill', columns: [{ title: 'Name', field: 'key' }, { title: 'Value', field: 'value' }], height: '200px' })
}

function stringify(v) {
  if (v === null || v === undefined) return ''
  if (Array.isArray(v)) return JSON.stringify(v)
  if (typeof v === 'object') return JSON.stringify(v)
  return String(v)
}

function renderPlot(pd, idx) {
  const el = document.getElementById(`plot-${idx}`)
  if (!el) return
  if (pd.type === 'roc') {
    Plotly.newPlot(el, [{ x: pd.data.fpr, y: pd.data.tpr, mode: 'lines', name: `ROC (AUC=${pd.data.auc||'n/a'})` }], { xaxis:{title:'FPR'}, yaxis:{title:'TPR'} }, { responsive: true })
  } else if (pd.type === 'pr') {
    Plotly.newPlot(el, [{ x: pd.data.recall, y: pd.data.precision, mode: 'lines' }], { xaxis:{title:'Recall'}, yaxis:{title:'Precision'} }, { responsive: true })
  } else if (pd.type === 'learning_curve') {
    Plotly.newPlot(el, [{ x: pd.data.train_sizes, y: pd.data.train_scores_mean, name:'Train' }, { x: pd.data.train_sizes, y: pd.data.test_scores_mean, name:'Test' }], { xaxis:{title:'Train size'}, yaxis:{title:'Score'} }, { responsive: true })
  }
}

onMounted(fetchModel)
</script>

<style scoped>
.model-detail .card { padding: 20px; border-radius: 12px }
.plots { display:flex; gap:12px; flex-wrap:wrap }
.plot-div { width: 320px; height: 260px }
</style>