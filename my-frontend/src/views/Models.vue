<template>
    <div class="models-page">
        <div class="actions-card card">
            <div class="actions-row">
                <!-- Place Train above Compare per request -->
                <button class="train-new-btn" @click="trainNew">Train New Model</button>
                <span class="hint">Select two models to enable comparison</span>
                <button class="compare-btn" :disabled="!(selectedIds.length === 2 && selectedDatasetForCompare)"
                    @click="compareSelected">Compare
                    Selected</button>
            </div>
        </div>

        <h1>Your Models</h1>

        <!-- Empty state when no models are present -->
        <div v-if="!hasAnyModels" class="no-models card">
            <h3>No models trained yet</h3>
            <p>You haven't trained any models. Start by training a new model on one of your datasets.</p>
            <button class="train-new-btn" @click="trainNew">Train your first model</button>
        </div>

        <div v-else class="datasets-grid">
            <div v-for="(models, dataset) in grouped" :key="dataset" class="dataset-card card">
                <h3>{{ dataset }}</h3>
                <ul>
                    <li v-for="m in models" :key="m.id" class="model-item">
                        <label>
                            <input type="checkbox" :value="m.id" :checked="selectedIds.includes(m.id)"
                                @change="(e) => toggleSelect(m.id, dataset, e)" />
                            <a @click.prevent="openModel(dataset, m.id)" href="#">{{ m.model_type }}_{{ m.id }}</a>
                            <span class="created">{{ m.created_at ? '(' + m.created_at.split('T')[0] + ')' : ''
                                }}</span>
                        </label>
                    </li>
                </ul>
                <div class="dataset-actions">
                    <button class="train-dataset-btn" @click="trainOnDataset(dataset)">Train on this dataset</button>
                    <button class="compare-dataset-btn" @click="compareOnDataset(dataset)">Compare models for this dataset</button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick } from 'vue';
import axios from 'axios';
import { useRouter, useRoute } from 'vue-router';

const grouped = ref({});
const token = localStorage.getItem('token');
const router = useRouter();
const route = useRoute();
const selectedIds = ref([]);
const selectedDatasetForCompare = ref(null);

// computed helper: true if grouped contains at least one model
const hasAnyModels = computed(() => {
    try {
        // grouped is an object mapping dataset -> array
        return Object.values(grouped.value || {}).some(arr => Array.isArray(arr) && arr.length > 0);
    } catch (e) {
        return false;
    }
});

function toggleSelect(id, dataset, e) {
    const checked = e.target.checked;
    if (checked) {
        // if no dataset chosen yet, set it
        if (!selectedDatasetForCompare.value) {
            selectedDatasetForCompare.value = dataset;
        }
        // only allow selecting if same dataset
        if (selectedDatasetForCompare.value === dataset) {
            selectedIds.value.push(id);
        } else {
            // ignore and uncheck
            e.target.checked = false;
            return;
        }
    } else {
        // remove id
        selectedIds.value = selectedIds.value.filter(x => x !== id);
        // if no more selected, clear dataset
        if (selectedIds.value.length === 0) selectedDatasetForCompare.value = null;
    }
}

async function fetchModels() {
    try {
        const r = await axios.get('http://localhost:8000/dashboard/models', { headers: { Authorization: `Bearer ${token}` } });
        grouped.value = r.data || {};
    } catch (e) {
        console.error('Failed to fetch models', e);
    }
}

function openModel(dataset, id) {
    router.push({ path: `/dashboard/model/${encodeURIComponent(dataset)}/${id}` });
}

function trainNew() {
    // navigate to model evaluation page without preselected dataset
    router.push({ path: '/dashboard/modelevaluation' });
}

function trainOnDataset(dataset) {
    // navigate to model evaluation and pre-fill filename via query param
    router.push({ path: '/dashboard/modelevaluation', query: { filename: dataset } });
}

function compareOnDataset(dataset) {
    // navigate to compare page with dataset preselected
    router.push({ path: '/dashboard/comparemodels', query: { dataset } });
}

onMounted(async () => {
    // if navigated with a dataset query param, preselect dataset-for-compare
    const qd = route.query.dataset;
    if (qd && typeof qd === 'string') {
        selectedDatasetForCompare.value = qd;
        // clear any existing selections
        selectedIds.value = [];
    }
    await nextTick();
    fetchModels();
});

function compareSelected() {
    if (selectedIds.value.length !== 2) return;
    // navigate to compare page with model_ids as repeated query params
    router.push({ path: '/dashboard/comparemodels', query: { model_ids: selectedIds.value.map(String) } })
}
</script>

<style scoped>
.models-page {
    padding: 20px
}

.datasets-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 16px
}

.dataset-card {
    /* flexible cards: allow variable widths, but keep a sensible minimum */
    flex: 1 1 40%;
    min-width: 25%;
    max-width: 50%;
    padding: 12px;
    box-sizing: border-box;
}

.model-item a {
    color: #3b82f6;
    text-decoration: none;
    cursor: pointer;
    /* allow truncation when space is limited */
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    display: inline-block;
    vertical-align: middle;
    max-width: 100%;
}

.model-item a:hover {
    text-decoration: underline
}

.created {
    color: #888;
    margin-left: 6px;
    white-space: nowrap;
    flex: 0 0 auto;
}

.actions-row {
    display: flex;
    gap: 12px;
    margin-bottom: 12px;
}

/* Ensure label contents (checkbox, name, date) stay on one line */
.model-item label {
    display: flex;
    align-items: center;
    gap: 8px;
    white-space: nowrap;
}

/* Allow the link to shrink inside the flex container */
.model-item label a {
    flex: 1 1 auto;
    min-width: 0; /* needed for overflow to work inside flex */
}

.compare-btn,
.train-new-btn,
.train-dataset-btn {
    padding: 8px 12px;
    background: #2563eb;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer
}

.compare-dataset-btn {
    padding: 6px 10px;
    background: #0ea5e9;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    margin-left: 8px;
    margin-top: 8px;
}

.compare-btn:disabled {
    background: #9bb7ff;
    cursor: not-allowed
}

.dataset-actions {
    margin-top: 8px
}

.actions-card {
    margin-bottom: 16px;
    padding: 12px;
    display: flex;
    align-items: center;
    justify-content: space-between
}

.actions-left {
    display: flex;
    gap: 12px
}

.hint {
    color: #666;
    font-size: 0.95rem
}
</style>
