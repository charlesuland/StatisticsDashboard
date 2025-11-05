<template>
  <div class="model-metrics">
    <div class="card results-card">
      <h2>Model Evaluation Results</h2>

      <div class="model-info" v-if="infoAvailable">
        <div><strong>Model:</strong> {{ prettyModelType }}</div>
        <div><strong>Classifier:</strong> {{ isClassifier ? 'Yes' : 'No' }}</div>
        <div v-if="data.training_time"><strong>Training time:</strong> {{ data.training_time }}</div>
        <div v-if="data.dataset"><strong>Dataset:</strong> {{ data.dataset }}</div>
      </div>

      <section v-if="hasMetrics(data)">
        <h3>Performance Metrics</h3>
        <div :id="metricsId"></div>
      </section>

      <section v-if="data && (data.cv_mean || data.cv_std)">
        <h3>Cross-Validation</h3>
        <div :id="cvId"></div>
      </section>

      <section v-if="data && data.feature_importance && data.feature_importance.length">
        <h3>Feature Importance</h3>
        <div :id="featureId"></div>
      </section>

      <section v-if="data.parameters && Object.keys(data.parameters).length">
        <h3>Model Parameters</h3>
        <div :id="paramsId"></div>
      </section>

      <section v-if="data">
        <h3>Model Plot</h3>
        <div :id="mainPlotId" class="main-plot-div"></div>
        <div v-if="isRegression && !hasPredictions" class="muted">No prediction points were returned by the backend so
          the best-fit line cannot be shown. To enable this, save predicted and actual values when training.</div>
      </section>

      <section v-if="data.plot_data && data.plot_data.length">
        <h3>Plots</h3>
        <div class="plots">
          <div v-for="(pd, idx) in data.plot_data" :key="pd.key" class="plot-card">
            <p>{{ pd.name }}</p>
            <div :id="plotId(idx)" class="plot-div"></div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, nextTick } from 'vue'
import { onBeforeUnmount, computed } from 'vue'
import Chart from 'chart.js/auto'
import Plotly from 'plotly.js-dist-min'
import { TabulatorFull as Tabulator } from 'tabulator-tables'
import 'tabulator-tables/dist/css/tabulator_simple.css'

const props = defineProps({ data: { type: Object, required: true }, showChart: { type: Boolean, default: true } })
const data = props.data

// generate unique ids per component instance
const uid = Math.random().toString(36).slice(2, 9)
const metricsId = `metrics-${uid}`
const cvId = `cv-${uid}`
const featureId = `feature-${uid}`
const paramsId = `params-${uid}`
const learningChart = ref(null)
let chartInstance = null
const tableInstances = {}
const mainPlotId = `main-plot-${uid}`

const hasPredictions = () => {
  if (!data) return false
  if (data.predictions && Array.isArray(data.predictions.y_true) && Array.isArray(data.predictions.y_pred)) return true
  if (Array.isArray(data.y_test) && Array.isArray(data.y_pred)) return true
  // support alternative keys
  if (Array.isArray(data.y_true) && Array.isArray(data.y_pred)) return true
  return false
}

const hasMetrics = (result) => {
  return result && ("r2" in result || "mse" in result || "mae" in result || (result.metrics && Object.keys(result.metrics).length))
}

const modelPrettyMap = {
  linear_regression: 'Linear Regression',
  logistic_regression: 'Logistic Regression',
  decision_tree: 'Decision Tree',
  random_forest: 'Random Forest',
  svm: 'Support Vector Machine',
  bagging: 'Bagging',
  boosting: 'Boosting',
  custom_dnn: 'Custom Neural Network'
}

const classifierModelTypes = ['logistic_regression', 'decision_tree', 'random_forest', 'svm', 'bagging', 'boosting', 'custom_dnn']

const infoAvailable = computed(() => {
  return !!(data && (data.model_type || data.training_time || data.dataset || data.parameters))
})

function humanizeModelType(t) {
  if (!t) return 'Unknown'
  if (modelPrettyMap[t]) return modelPrettyMap[t]
  return t.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
}

const prettyModelType = computed(() => humanizeModelType(data.model_type))

const isClassifier = computed(() => {
  // explicit parameter flag wins
  if (data && data.parameters && typeof data.parameters === 'object' && 'classifier' in data.parameters) return !!data.parameters.classifier
  // explicit is_classifier flag
  if (data && data.is_classifier !== undefined) return !!data.is_classifier
  // try model_type string matching (case-insensitive, substring checks)
  try {
    const mt = (data && data.model_type) ? String(data.model_type).toLowerCase() : ''
    if (mt) {
      const keys = ['logistic', 'classifier', 'decision_tree', 'random_forest', 'randomforest', 'svm', 'svc', 'bagging', 'boosting', 'dnn', 'neural']
      for (const k of keys) if (mt.includes(k)) return true
      // also check known exact names
      if (classifierModelTypes.includes(mt)) return true
    }
  } catch (e) {
    // ignore and fall through
  }
  return false
})

const isRegression = computed(() => !isClassifier.value)

function plotId(idx) { return `plot-${uid}-${idx}` }

function buildTables(results) {
  // Metrics
  const metricsData = []
  if (results.r2 !== undefined) metricsData.push({ metric: 'R²', value: results.r2 })
  if (results.mse !== undefined) metricsData.push({ metric: 'MSE', value: results.mse })
  if (results.mae !== undefined) metricsData.push({ metric: 'MAE', value: results.mae })

  // create metrics table only if container exists
  {
    const el = document.getElementById(metricsId)
    if (tableInstances[metricsId] && typeof tableInstances[metricsId].destroy === 'function') {
      tableInstances[metricsId].destroy()
      delete tableInstances[metricsId]
    }
    if (el) {
      el.innerHTML = ''
      tableInstances[metricsId] = new Tabulator(el, { data: metricsData, layout: 'fitColumns', columns: [{ title: 'Metric', field: 'metric' }, { title: 'Value', field: 'value', hozAlign: 'left', sorter: 'number' }], movableColumns: true })
    }
  }

  // CV
  const cvData = [
    { metric: 'R²', mean: results.cv_mean?.r2_mean ?? null, std: results.cv_std?.r2_std ?? null },
    { metric: 'MSE', mean: results.cv_mean?.mse_mean ?? null, std: results.cv_std?.mse_std ?? null },
    { metric: 'MAE', mean: results.cv_mean?.mae_mean ?? null, std: results.cv_std?.mae_std ?? null },
  ]
  // cross-validation table — only build if element exists
  {
    const el = document.getElementById(cvId)
    if (tableInstances[cvId] && typeof tableInstances[cvId].destroy === 'function') {
      tableInstances[cvId].destroy()
      delete tableInstances[cvId]
    }
    if (el) {
      el.innerHTML = ''
      tableInstances[cvId] = new Tabulator(el, { data: cvData, layout: 'fitColumns', columns: [{ title: 'Metric', field: 'metric' }, { title: 'Mean', field: 'mean', sorter: 'number' }, { title: 'Std', field: 'std', sorter: 'number' }] })
    }
  }

  // Feature importance
  const feat = (results.feature_importance || []).map(f => ({ feature: f.name, importance: f.importance }))
  // feature importance table
  {
    const el = document.getElementById(featureId)
    if (tableInstances[featureId] && typeof tableInstances[featureId].destroy === 'function') {
      tableInstances[featureId].destroy()
      delete tableInstances[featureId]
    }
    if (el) {
      el.innerHTML = ''
      tableInstances[featureId] = new Tabulator(el, { data: feat, layout: 'fitColumns', columns: [{ title: 'Feature', field: 'feature' }, { title: 'Importance', field: 'importance', sorter: 'number' }] })
    }
  }

  // Params
  const params = []
  for (const k in results.parameters || {}) params.push({ param: k, value: results.parameters[k] })
  // parameters table
  {
    const el = document.getElementById(paramsId)
    if (tableInstances[paramsId] && typeof tableInstances[paramsId].destroy === 'function') {
      tableInstances[paramsId].destroy()
      delete tableInstances[paramsId]
    }
    if (el) {
      el.innerHTML = ''
      tableInstances[paramsId] = new Tabulator(el, { data: params, layout: 'fitColumns', columns: [{ title: 'Parameter', field: 'param' }, { title: 'Value', field: 'value' }] })
    }
  }
}

function renderPlot(pd, idx) {
  const el = document.getElementById(plotId(idx))
  if (!el) return

  const type = pd.type
  let dataPlot = []
  let layout = { margin: { t: 30, b: 40 }, autosize: true }

  if (type === 'roc') {
    dataPlot = [
      { x: pd.data.fpr, y: pd.data.tpr, mode: 'lines', name: `ROC (AUC=${pd.data.auc || 'n/a'})`, hovertemplate: 'FPR: %{x:.3f}<br>TPR: %{y:.3f}<extra></extra>' },
      { x: [0, 1], y: [0, 1], mode: 'lines', line: { dash: 'dash', color: 'gray' }, showlegend: false, hoverinfo: 'none' }
    ]
    layout.xaxis = { title: 'FPR' }
    layout.yaxis = { title: 'TPR' }
    layout.legend = { orientation: 'h' }
  } else if (type === 'pr') {
    dataPlot = [
      { x: pd.data.recall, y: pd.data.precision, mode: 'lines', name: `PR (AP=${pd.data.ap || 'n/a'})`, hovertemplate: 'Recall: %{x:.3f}<br>Precision: %{y:.3f}<extra></extra>' }
    ]
    layout.xaxis = { title: 'Recall' }
    layout.yaxis = { title: 'Precision' }
    layout.legend = { orientation: 'h' }
  } else if (type === 'confusion_matrix') {
    dataPlot = [{ z: pd.data.matrix, type: 'heatmap', colorscale: 'Blues', hovertemplate: 'Predicted: %{x}<br>Actual: %{y}<br>Count: %{z}<extra></extra>' }]
    layout.xaxis = { title: 'Predicted' }
    layout.yaxis = { title: 'Actual' }
  } else if (type === 'learning_curve') {
    dataPlot = [
      { x: pd.data.train_sizes, y: pd.data.train_scores_mean, mode: 'lines+markers', name: 'Train', hovertemplate: 'Samples: %{x}<br>Score: %{y:.3f}<extra></extra>' },
      { x: pd.data.train_sizes, y: pd.data.test_scores_mean, mode: 'lines+markers', name: 'Test', hovertemplate: 'Samples: %{x}<br>Score: %{y:.3f}<extra></extra>' }
    ]
    layout.xaxis = { title: 'Training Samples' }
    layout.yaxis = { title: 'Score' }
    layout.legend = { orientation: 'h' }
  } else if (type === 'feature_importance' || type === 'shap_summary') {
    const names = pd.data.map(d => d.name)
    const vals = pd.data.map(d => d.importance ?? d.mean_abs_shap ?? d.value ?? 0)
    dataPlot = [{ x: vals.reverse(), y: names.reverse(), type: 'bar', orientation: 'h', hovertemplate: '%{y}: %{x:.4f}<extra></extra>' }]
    layout.xaxis = { title: type === 'shap_summary' ? 'Mean |SHAP value|' : 'Importance' }
  } else {
    el.innerText = 'Unsupported plot type: ' + type
    return
  }

  Plotly.newPlot(el, dataPlot, layout, { responsive: true })
}

watch(() => props.data, async (newVal) => {
  if (!newVal) return
  await nextTick()
  try { buildTables(newVal) } catch (e) { console.error('buildTables failed', e) }

  // render plots
  if (newVal.plot_data && newVal.plot_data.length) {
    newVal.plot_data.forEach((pd, idx) => {
      try { renderPlot(pd, idx) } catch (e) { console.error('renderPlot failed', e) }
    })
  }

  // learning chart
  // main plot (ROC for classifiers or predicted vs actual for regressors)
  try {
    renderMainPlot(newVal)
  } catch (e) {
    console.error('renderMainPlot failed', e)
  }
}, { immediate: true })

onMounted(async () => {
  // DOM might not be ready for Tabulator divs until mounted
  if (props.data) {
    await nextTick()
    try { buildTables(props.data) } catch (e) { console.error('initial buildTables failed', e) }
    if (props.data.plot_data && props.data.plot_data.length) {
      props.data.plot_data.forEach((pd, idx) => { try { renderPlot(pd, idx) } catch (e) { console.error('initial renderPlot', e) } })
    }
    try { renderMainPlot(props.data) } catch (e) { console.error('initial renderMainPlot', e) }
  }
})

function renderMainPlot(result) {
  const el = document.getElementById(mainPlotId)
  if (!el) return
  // clear previous
  el.innerHTML = ''

  // If classifier, prefer ROC curve from plot_data or result.roc_curve
  if (isClassifier.value) {
    // try plot_data first
    const roc = (result.plot_data || []).find(p => p.key === 'roc_curve') || result.roc_curve
    if (roc) {
      // multiclass shape: { classes: [...], fpr: [[...],[...]], tpr: [[...],[...]] }
      const cls = roc.data?.classes || roc.classes || null
      const fpr = roc.data?.fpr || roc.fpr || []
      const tpr = roc.data?.tpr || roc.tpr || []
      const auc = roc.data?.auc ?? result.roc_auc ?? null
      if (cls && Array.isArray(fpr) && Array.isArray(fpr[0])) {
        // per-class traces
        const traces = []
        for (let i = 0; i < cls.length; i++) {
          traces.push({ x: fpr[i] || [], y: tpr[i] || [], mode: 'lines', name: `ROC ${cls[i]}`, hovertemplate: 'FPR: %{x:.3f}<br>TPR: %{y:.3f}<extra></extra>' })
        }
        traces.push({ x: [0, 1], y: [0, 1], mode: 'lines', line: { dash: 'dash', color: 'gray' }, showlegend: false, hoverinfo: 'none' })
        const layout = { title: `ROC Curve (AUC=${auc ?? 'n/a'})`, xaxis: { title: 'FPR' }, yaxis: { title: 'TPR' }, margin: { t: 30, b: 40 }, autosize: true, legend: { orientation: 'h' } }
        Plotly.newPlot(el, traces, layout, { responsive: true })
        return
      }
      // binary or fallback
      const trace = [
        { x: fpr, y: tpr, mode: 'lines', name: `ROC (AUC=${auc ?? 'n/a'})`, hovertemplate: 'FPR: %{x:.3f}<br>TPR: %{y:.3f}<extra></extra>' },
        { x: [0, 1], y: [0, 1], mode: 'lines', line: { dash: 'dash', color: 'gray' }, showlegend: false, hoverinfo: 'none' }
      ]
      const layout = { title: 'ROC Curve', xaxis: { title: 'FPR' }, yaxis: { title: 'TPR' }, margin: { t: 30, b: 40 }, autosize: true, legend: { orientation: 'h' } }
      Plotly.newPlot(el, trace, layout, { responsive: true })
      return
    }
    // no roc data: show message
    el.innerText = 'ROC data not available for this classifier.'
    return
  }

  // Regression: show predicted vs actual scatter + best-fit line if predictions available
  if (!isClassifier.value) {
    // find arrays
    let y_true = null
    let y_pred = null
    if (result.predictions && Array.isArray(result.predictions.y_true) && Array.isArray(result.predictions.y_pred)) {
      y_true = result.predictions.y_true
      y_pred = result.predictions.y_pred
    } else if (Array.isArray(result.y_test) && Array.isArray(result.y_pred)) {
      y_true = result.y_test
      y_pred = result.y_pred
    } else if (Array.isArray(result.y_true) && Array.isArray(result.y_pred)) {
      y_true = result.y_true
      y_pred = result.y_pred
    }

    if (!y_true || !y_pred || y_true.length !== y_pred.length) {
      // fallback: if a learning_curve plot exists, show it; otherwise message
      const lc = (result.plot_data || []).find(p => p.key === 'learning_curve') || result.learning_curve
      if (lc && lc.data) {
        const trace = [
          { x: lc.data.train_sizes, y: lc.data.train_scores_mean, mode: 'lines+markers', name: 'Train' },
          { x: lc.data.train_sizes, y: lc.data.test_scores_mean, mode: 'lines+markers', name: 'Test' }
        ]
        const layout = { title: 'Learning Curve', xaxis: { title: 'Training samples' }, yaxis: { title: 'Score' }, margin: { t: 30, b: 40 }, autosize: true }
        Plotly.newPlot(el, trace, layout, { responsive: true })
        return
      }
      el.innerText = 'No prediction points were returned by the backend so the best-fit line cannot be shown.'
      return
    }

    // compute best-fit line (least squares)
    const n = y_true.length
    const x = y_true.map(v => Number(v))
    const y = y_pred.map(v => Number(v))
    const xMean = x.reduce((a, b) => a + b, 0) / n
    const yMean = y.reduce((a, b) => a + b, 0) / n
    let num = 0; let den = 0
    for (let i = 0; i < n; i++) { num += (x[i] - xMean) * (y[i] - yMean); den += (x[i] - xMean) * (x[i] - xMean) }
    const slope = den === 0 ? 0 : num / den
    const intercept = yMean - slope * xMean

    // prepare traces: scatter and line
    const scatter = { x: x, y: y, mode: 'markers', name: 'Predicted vs Actual', marker: { color: 'blue' }, hovertemplate: 'Actual: %{x:.4f}<br>Predicted: %{y:.4f}<extra></extra>' }
    // best-fit line over range
    const minX = Math.min(...x); const maxX = Math.max(...x)
    const lineX = [minX, maxX]
    const lineY = lineX.map(xv => slope * xv + intercept)
    const line = { x: lineX, y: lineY, mode: 'lines', name: `Best fit (y=${slope.toFixed(3)}x+${intercept.toFixed(3)})`, line: { color: 'red' }, hovertemplate: 'y=%{y:.4f}<extra></extra>' }
    const layout = { title: 'Predicted vs Actual (with best-fit)', xaxis: { title: 'Actual' }, yaxis: { title: 'Predicted' }, margin: { t: 30, b: 40 }, autosize: true, legend: { orientation: 'v' } }
    Plotly.newPlot(el, [scatter, line], layout, { responsive: true })
    return
  }
}

onBeforeUnmount(() => {
  // destroy chart
  try { if (chartInstance && typeof chartInstance.destroy === 'function') chartInstance.destroy() } catch (e) { }
  // destroy tabulator instances
  Object.keys(tableInstances).forEach(k => {
    try { if (tableInstances[k] && typeof tableInstances[k].destroy === 'function') tableInstances[k].destroy() } catch (e) { }
    delete tableInstances[k]
  })
})
</script>

<style scoped>
.model-metrics .card {
  padding: 20px;
  border-radius: 12px
}

.plots {
  display: flex;
  gap: 12px;
  flex-wrap: wrap
}

.plot-div {
  width: 320px;
  height: 260px
}

.learning-chart {
  width: 100%;
  height: 220px
}
</style>
