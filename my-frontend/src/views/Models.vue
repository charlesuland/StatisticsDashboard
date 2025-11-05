<template>
  <div class="models-page">
    <h1>Your Models</h1>
    <div class="datasets-grid">
      <div v-for="(models, dataset) in grouped" :key="dataset" class="dataset-card card">
        <h3>{{ dataset }}</h3>
        <ul>
          <li v-for="m in models" :key="m.id" class="model-item">
            <a @click.prevent="openModel(dataset, m.id)" href="#">{{ m.model_type }}_{{ m.id }} <span class="created">{{ m.created_at ? '(' + m.created_at.split('T')[0] + ')' : '' }}</span></a>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

const grouped = ref({});
const token = localStorage.getItem('token');
const router = useRouter();

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

onMounted(fetchModels);
</script>

<style scoped>
.models-page { padding: 20px }
.datasets-grid { display:flex; flex-wrap:wrap; gap:16px }
.dataset-card { width: 320px; padding:12px }
.model-item a { color: #3b82f6; text-decoration: none; cursor: pointer }
.model-item a:hover { text-decoration: underline }
.created { color:#888; margin-left:6px }
</style>
