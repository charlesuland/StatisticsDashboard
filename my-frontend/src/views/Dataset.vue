<template>
  <div class="dataset-container">
    <!-- Upload Section -->
    <div class="upload-section card">
      <h3>Upload a Dataset</h3>
      <input type="file" @change="onFileChange" />
      <button @click="uploadFile" :disabled="!selectedFile">Upload</button>
      <p v-if="uploadStatus" class="status">{{ uploadStatus }}</p>
    </div>

    <!-- Current Datasets -->
    <div class="curr-datasets card">
      <h3>Current Datasets</h3>
      <ul>
        <li v-for="file in files" :key="file" class="dataset-item">
          {{ file }}
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

const selectedFile = ref(null);
const uploadStatus = ref('');
const files = ref([]);
const token = localStorage.getItem("token"); 

function onFileChange(event) {
  selectedFile.value = event.target.files[0];
}

async function uploadFile() {
  if (!selectedFile.value) return;

  const formData = new FormData();
  formData.append('file', selectedFile.value);

  try {
    const response = await axios.post(
      'http://localhost:8000/dashboard/addDataSet',
      formData,
      { headers: { 'Content-Type': 'multipart/form-data',  Authorization: `Bearer ${token}`} }
    );

    uploadStatus.value = `Upload successful: ${response.data.filename}`;
  } catch (error) {
    console.error(error);
    uploadStatus.value = 'Upload failed';
  }
  getDatasets();
}

onMounted(() => getDatasets());

async function getDatasets() {
  try {
    const response = await axios.get("http://localhost:8000/dashboard/datasets", {
      headers: { Authorization: `Bearer ${token}` },
    });
    files.value = response.data.files;
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
