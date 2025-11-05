<template>
  <div class="dataset-container">
    <!-- Upload Section -->
    <div class="upload-section card">
      <h3>Upload a Dataset</h3>
      <input type="file" @change="onFileChange" />
      <div style="margin-top:10px;">
        <label for="customName">Custom filename (optional):</label>
        <input id="customName" v-model="customName" type="text" placeholder="my_dataset.csv"  />
        <div v-if="customName && !isCustomNameValid" style="color: #e74c3c; margin-top:6px">Invalid filename — use letters, numbers, spaces, . _ - and max 100 chars. No slashes.</div>
      </div>
      <button @click="uploadFile" :disabled="!selectedFile || (customName !== '' && !isCustomNameValid)">Upload</button>
      <p v-if="uploadStatus" :class="uploadStatusClass">{{ uploadStatus }}</p>
    </div>

    <!-- Current Datasets -->
    <div class="curr-datasets card">
      <h3>Current Datasets</h3>
      <ul>
        <li v-for="file in files" :key="file" class="dataset-item">
          <router-link :to="`/dashboard/datasets/${encodeURIComponent(file)}`" class="dataset-link">
            <div class="dataset-name">{{ file }}</div>
            <div class="dataset-meta">Models: <strong>{{ counts[file] ?? '-' }}</strong></div>
          </router-link>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

const selectedFile = ref(null);
const customName = ref('');
const uploadStatus = ref('');
const uploadStatusClass = ref('status');
const files = ref([]);
const counts = ref({});
const token = localStorage.getItem("token"); 

// Validation rules
const MAX_FILENAME_LENGTH = 100;
const filenameRegex = /^[A-Za-z0-9 _.-]+$/; // allow letters, numbers, space, dot, underscore, dash

const isCustomNameValid = (name => {
  if (!name) return true;
  if (name.length > MAX_FILENAME_LENGTH) return false;
  if (name.includes('/') || name.includes('\\')) return false;
  return filenameRegex.test(name);
});

function onFileChange(event) {
  selectedFile.value = event.target.files[0];
}

async function uploadFile() {
  if (!selectedFile.value) return;

  const formData = new FormData();
  let filenameToUse = null;
  if (customName.value && customName.value.trim().length > 0) {
    filenameToUse = customName.value.trim();
    // auto-append .csv if user omitted extension
    if (!/\.[a-zA-Z0-9]{1,5}$/.test(filenameToUse)) filenameToUse += '.csv';
  }
  if (filenameToUse) {
    formData.append('file', selectedFile.value, filenameToUse);
  } else {
    formData.append('file', selectedFile.value);
  }

  try {
    const response = await axios.post(
      'http://localhost:8000/dashboard/addDataSet',
      formData,
      { headers: { 'Content-Type': 'multipart/form-data',  Authorization: `Bearer ${token}`} }
    );

  uploadStatus.value = `Upload successful: ${response.data.filename}`;
  uploadStatusClass.value = 'status success';
  // clear selection and custom name
  selectedFile.value = null;
  customName.value = '';
  } catch (error) {
    console.error(error);
    uploadStatus.value = 'Upload failed';
    uploadStatusClass.value = 'status error';
  }
  getDatasets();
}

onMounted(() => getDatasets());

async function getDatasets() {
  try {
    const response = await axios.get("http://localhost:8000/dashboard/datasets", {
      headers: { Authorization: `Bearer ${token}` },
    });
    files.value = response.data.files || [];
    // initialize counts as unknown
    files.value.forEach(f => counts.value[f] = '-');
    // fetch model counts for each file
    for (const f of files.value) {
      try {
        const resp = await axios.get('http://localhost:8000/dashboard/datasets/models', { params: { filename: f }, headers: { Authorization: `Bearer ${token}` } });
        const models = resp.data.models || [];
        counts.value[f] = models.length;
      } catch (e) {
        counts.value[f] = '-';
      }
    }
  } catch (error) {
    console.log(error);
  }
}
</script>

<style scoped>
.dataset-container {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
  margin-top: 20px;
}

/* Card styling */
.card {
  background-color: #fff;
  border-radius: 15px;
  padding: 25px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
  flex: 1 1 300px;
  min-width: 300px;
}

/* Upload section */
.upload-section h3,
.curr-datasets h3 {
  margin-bottom: 20px;
  color: #333;
}

.upload-section input[type="file"] {
  display: block;
  margin-bottom: 15px;
}

.upload-section button {
  padding: 10px 25px;
  background-color: #667eea;
  color: white;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: background 0.3s;
}

.upload-section button:disabled {
  background-color: #aaa;
  cursor: not-allowed;
}

.upload-section button:hover:not(:disabled) {
  background-color: #5a67d8;
}

/* Status message */
.status {
  margin-top: 10px;
  font-weight: bold;
}

.status.error {
  color: #e74c3c;
}

.status.success {
  color: #2ecc71;
}

/* Current datasets */
.curr-datasets ul {
  list-style: none;
  padding: 0;
}

.dataset-item {
  padding: 12px 15px;
  margin-bottom: 10px;
  border-radius: 8px;
  background-color: #f4f6f8;
  transition: background 0.3s;
  cursor: pointer;
}

.dataset-item:hover {
  background-color: #e1e6f0;
}
</style>
