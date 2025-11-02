
    <!-- option for form-->
<template>
  <div class="upload-section">
    <h3>Upload a Dataset</h3>
    <input type="file" @change="onFileChange" />
    <button @click="uploadFile" :disabled="!selectedFile">Upload</button>

    <p v-if="uploadStatus">{{ uploadStatus }}</p>
  </div>

  <div class="curr-datasets">
    <h3>Current Datasets</h3>
    <ul>
        <li v-for="file in files">
            {{ file }}
        </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

const selectedFile = ref(null);
const uploadStatus = ref('');
const files = ref(null)

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
      { headers: { 'Content-Type': 'multipart/form-data' } }
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
        const response = await axios.get(
            'http://localhost:8000/dashboard/datasets',
        );
        files.value = response.data.files;
        
    }

    catch (error) {
        console.log(error);
    }
}
</script>



    <!-- detected datasets -->