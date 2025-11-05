<template>
  <div class="model-detail">
    <div class="card">
        <h2>Model Detail</h2>
        <p><strong>Dataset:</strong> {{ dataset }}</p>
        <p><strong>Model ID:</strong> {{ modelId }}</p>
        <p v-if="meta.created_at"><strong>Trained at:</strong> {{ meta.created_at }}</p>

        <ModelMetrics v-if="detailResults" :data="detailResults" />
      </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import axios from 'axios'
import ModelMetrics from '../components/ModelMetrics.vue'

const props = defineProps({ dataset: String, modelId: [String, Number] })
const dataset = props.dataset
const modelId = props.modelId
const meta = ref({})
const detailResults = ref(null)
const token = localStorage.getItem('token')

async function fetchModel() {
  try {
    const res = await axios.get(`http://localhost:8000/dashboard/models/${modelId}`, { headers: { Authorization: `Bearer ${token}` } })
    meta.value = res.data || {}

    // Build a results-like object for the metrics component
    const dr = {
      parameters: meta.value.parameters || {},
      // backend may store metrics under metrics or top-level keys
      r2: meta.value.metrics?.r2 ?? meta.value.r2,
      mse: meta.value.metrics?.mse ?? meta.value.mse,
      mae: meta.value.metrics?.mae ?? meta.value.mae,
      cv_mean: meta.value.metrics?.cv_mean ?? meta.value.cv_mean,
      cv_std: meta.value.metrics?.cv_std ?? meta.value.cv_std,
      feature_importance: meta.value.metrics?.feature_importance ?? meta.value.feature_importance ?? [],
      learning_curve: meta.value.metrics?.learning_curve ?? meta.value.learning_curve,
      plot_data: []
    }

    // include metadata
    dr.model_type = meta.value.model_type || meta.value.model || undefined
    dr.training_time = meta.value.training_time || undefined
    dr.dataset = dataset || meta.value.dataset || undefined
    // allow explicit classifier flag if stored
    dr.is_classifier = meta.value.parameters?.classifier ?? undefined

    if (meta.value.metrics?.roc_curve) dr.plot_data.push({ name: 'ROC Curve', key: 'roc_curve', type: 'roc', data: { fpr: meta.value.metrics.roc_curve.fpr, tpr: meta.value.metrics.roc_curve.tpr, auc: meta.value.metrics.roc_auc } })
    if (meta.value.metrics?.pr_curve) dr.plot_data.push({ name: 'PR Curve', key: 'pr_curve', type: 'pr', data: { recall: meta.value.metrics.pr_curve.recall, precision: meta.value.metrics.pr_curve.precision, ap: meta.value.metrics.pr_auc } })
    if (meta.value.metrics?.learning_curve) dr.plot_data.push({ name: 'Learning Curve', key: 'learning_curve', type: 'learning_curve', data: { train_sizes: meta.value.metrics.learning_curve.train_sizes, train_scores_mean: meta.value.metrics.learning_curve.train_scores_mean, test_scores_mean: meta.value.metrics.learning_curve.test_scores_mean } })

    detailResults.value = dr
  } catch (e) {
    console.error('Failed to fetch model', e)
  }
}

onMounted(fetchModel)
</script>

<style scoped>
.model-detail .card { padding: 20px; border-radius: 12px }
.plots { display:flex; gap:12px; flex-wrap:wrap }
.plot-div { width: 320px; height: 260px }
</style>