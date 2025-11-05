<template>
  <div class="dataset-detail card">
    <h2>{{ filename }}</h2>
    <div class="meta-row">
      <div>Rows: <strong>{{ info.row_count ?? '-' }}</strong></div>
      <div>Columns: <strong>{{ columns.length }}</strong></div>
      <div>Missing cells: <strong>{{ totalMissing }}</strong></div>
    </div>

    <div class="actions">
      <button @click="downloadDataset">Download CSV</button>
    </div>

    <section class="columns card">
      <h3>Columns</h3>
      <div ref="columnsEl" class="tabulator-wrap"></div>
    </section>

    <section class="models card">
      <h3>Models trained on this dataset</h3>
      <div ref="modelsEl" class="tabulator-wrap"></div>
    </section>

    <section class="preview card" v-if="preview.length">
      <h3>Preview (first {{ preview.length }} rows)</h3>
      <div ref="previewEl" class="tabulator-wrap"></div>
    </section>

  </div>
</template>

<script setup>
import { ref, onMounted, computed, onBeforeUnmount, nextTick } from 'vue';
import axios from 'axios';
import { useRoute, useRouter } from 'vue-router';
import { TabulatorFull as Tabulator } from 'tabulator-tables'
import 'tabulator-tables/dist/css/tabulator_simple.css'


const route = useRoute();
const router = useRouter();
const filename = decodeURIComponent(route.params.filename || route.query.filename || '');
const token = localStorage.getItem('token');

const columns = ref([]);
const dtypes = ref({});
const missing = ref({});
const info = ref({});
const models = ref([]);
const preview = ref([]);

// Tabulator refs & instances
const columnsEl = ref(null);
const modelsEl = ref(null);
const previewEl = ref(null);
let columnsTable = null;
let modelsTable = null;
let previewTable = null;

const totalMissing = computed(() => Object.values(missing.value || {}).reduce((a,b)=>a+(Number(b)||0),0));

async function fetchInfo() {
  try {
    const resp = await axios.get('http://localhost:8000/dashboard/datasets/columns', { params: { filename }, headers: { Authorization: `Bearer ${token}` } });
    columns.value = resp.data.columns || [];
  } catch (e) {
    console.error('Failed to fetch columns', e);
  }

  try {
    const r2 = await axios.get('http://localhost:8000/dashboard/datasets/column_info', { params: { filename }, headers: { Authorization: `Bearer ${token}` } });
    dtypes.value = r2.data.dtypes || {};
  } catch (e) {
    console.error('Failed to fetch column info', e);
  }

  try {
    const r3 = await axios.get('http://localhost:8000/dashboard/datasets/models', { params: { filename }, headers: { Authorization: `Bearer ${token}` } });
    models.value = r3.data.models || [];
  } catch (e) {
    console.error('Failed to fetch models for dataset', e);
  }

  try {
    const r4 = await axios.get('http://localhost:8000/dashboard/datasets/info', { params: { filename }, headers: { Authorization: `Bearer ${token}` } });
    info.value = r4.data || {};
    missing.value = info.value.missing_values || {};
  } catch (e) {
    console.error('Failed to fetch dataset info', e);
  }

  try {
    const r5 = await axios.get('http://localhost:8000/dashboard/datasets/preview', { params: { filename, n: 10 }, headers: { Authorization: `Bearer ${token}` } });
    preview.value = r5.data.rows || [];
  } catch (e) {
    console.error('Failed to fetch preview', e);
  }

  // build tabulator tables after DOM update
  await nextTick();
  buildColumnsTable();
  buildModelsTable();
  buildPreviewTable();
}

function buildColumnsTable() {
  // destroy if exists
  try { if (columnsTable && typeof columnsTable.destroy === 'function') columnsTable.destroy(); } catch(e){}
  const data = columns.value.map(col => ({ name: col, type: dtypes.value[col] || 'unknown', missing: missing.value[col] ?? 0 }));
  columnsTable = new Tabulator(columnsEl.value, {
    data,
    layout: 'fitColumns',
    columns: [
      { title: 'Name', field: 'name' },
      { title: 'Type', field: 'type' },
      { title: 'Missing', field: 'missing', hozAlign: 'right' },
    ],
    height: 'auto'
  });
}

function buildModelsTable() {
  try { if (modelsTable && typeof modelsTable.destroy === 'function') modelsTable.destroy(); } catch(e){}
  const data = (models.value || []).map(m => ({ label: m, id: m.split('_').pop() }));
  modelsTable = new Tabulator(modelsEl.value, {
    data,
    layout: 'fitColumns',
    columns: [
      { title: 'Model', field: 'label', formatter: function(cell, formatterParams){
          // create a button/link element that uses router.push for SPA navigation
          const row = cell.getRow().getData();
          const modelLabel = cell.getValue();
          const wrapper = document.createElement('span');
          wrapper.style.cursor = 'pointer';
          wrapper.style.color = '#3b82f6';
          wrapper.style.textDecoration = 'underline';
          wrapper.innerText = modelLabel;
          wrapper.addEventListener('click', function(e){
            // model string is expected to be like "modeltype_id" — id is last segment
            const id = row.label || modelLabel || '';
            // const parts = raw.split('_');
            // const id = parts[parts.length - 1];
            // navigate using router to preserve SPA behavior
            router.push({ path: `/dashboard/model/${encodeURIComponent(filename)}/${id}` });
          });
          return wrapper;
        },
      }
    ],
    height: 'auto'
  });
}

function buildPreviewTable() {
  try { if (previewTable && typeof previewTable.destroy === 'function') previewTable.destroy(); } catch(e){}
  const data = preview.value || [];
  const cols = (columns.value || []).map(c => ({ title: c, field: c }));
  previewTable = new Tabulator(previewEl.value, {
    data,
    layout: 'fitDataStretch',
    columns: cols,
    height: 'auto'
  });
}

onMounted(() => {
  if (!filename) {
    router.push('/dashboard/datasets');
    return;
  }
  fetchInfo();
});

onBeforeUnmount(() => {
  try { if (columnsTable && typeof columnsTable.destroy === 'function') columnsTable.destroy(); } catch(e){}
  try { if (modelsTable && typeof modelsTable.destroy === 'function') modelsTable.destroy(); } catch(e){}
  try { if (previewTable && typeof previewTable.destroy === 'function') previewTable.destroy(); } catch(e){}
});

async function downloadDataset() {
  try {
    const r = await axios.get('http://localhost:8000/dashboard/datasets/download', { params: { filename }, headers: { Authorization: `Bearer ${token}` }, responseType: 'blob' });
    const url = window.URL.createObjectURL(new Blob([r.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename + '_processed.csv');
    document.body.appendChild(link);
    link.click();
    link.remove();
  } catch (e) {
    console.error('Failed to download', e);
  }
}
</script>

<style scoped>
.dataset-detail {
  padding: 20px;
}
.meta-row {
  display:flex;
  gap:20px;
  margin-bottom:10px;
}
.card { margin-top:12px; padding:12px }
.columns table, .preview table { width:100%; border-collapse:collapse }
.col-table td, .col-table th, .preview td, .preview th { border:1px solid #ddd; padding:8px }
.dataset-link { display:flex; justify-content:space-between; align-items:center; text-decoration:none; color:inherit }
.actions { margin-top:10px }
</style>
