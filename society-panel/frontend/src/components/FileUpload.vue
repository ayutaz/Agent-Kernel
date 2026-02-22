<!-- File upload component with directory targeting and drag-drop support. -->
<template>
  <div class="upload-container">
    <h3>カスタムファイルのアップロード</h3>
    <div class="form-group">
      <label for="target-dir">保存先ディレクトリ:</label>
      <input
        type="text"
        id="target-dir"
        v-model="targetDir"
        placeholder="e.g., plugins/agent/profile"
      />
      <small>ワークスペースルートからの相対パス。例: `plugins/action/other` またはルートの場合は `.`</small>
    </div>
    <div class="form-group">
      <label for="file-input">ファイルを選択:</label>
      <input
        type="file"
        id="file-input"
        multiple
        @change="handleFileChange"
      />
    </div>
    <button @click="handleUpload" :disabled="!files.length || !targetDir || isLoading">
      {{ isLoading ? 'アップロード中...' : 'アップロード' }}
    </button>
    <div v-if="message" :class="['message', messageType]">
      {{ message }}
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';

const files = ref([]);
const targetDir = ref('plugins/agent/act');
const isLoading = ref(false);
const message = ref('');
const messageType = ref('success');

const handleFileChange = (event) => {
  files.value = Array.from(event.target.files);
};

const handleUpload = async () => {
  if (!files.value.length || !targetDir.value) {
    message.value = 'ファイルと保存先ディレクトリを指定してください。';
    messageType.value = 'error';
    return;
  }

  isLoading.value = true;
  message.value = '';

  const formData = new FormData();
  files.value.forEach(file => {
    formData.append('files', file);
  });
  formData.append('target_dir', targetDir.value);

  try {
    const response = await axios.post('http://localhost:8001/api/files/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    message.value = response.data.message;
    messageType.value = 'success';
  } catch (error) {
    message.value = error.response?.data?.detail || 'アップロード中にエラーが発生しました。';
    messageType.value = 'error';
  } finally {
    isLoading.value = false;
    document.getElementById('file-input').value = '';
    files.value = [];
  }
};
</script>

<style scoped>
.upload-container {
  border: 1px solid var(--vp-c-border);
  padding: 20px;
  border-radius: 8px;
  background-color: var(--vp-c-bg-soft);
}
.form-group {
  margin-bottom: 15px;
}
label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
}
input[type="text"], input[type="file"] {
  width: 100%;
  padding: 8px;
  box-sizing: border-box;
  border: 1px solid var(--vp-c-border);
  border-radius: 4px;
}
small {
  display: block;
  margin-top: 5px;
  color: #666;
  font-size: 0.875rem;
}
button {
  padding: 10px 15px;
  border: none;
  background-color: var(--vp-c-brand);
  color: white;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.25s;
}
button:hover {
  background-color: var(--vp-c-brand-light);
}
button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}
.message {
  margin-top: 15px;
  padding: 10px;
  border-radius: 4px;
}
.success {
  background-color: #e0f2e9;
  color: #1e8752;
  border: 1px solid #a3d9b8;
}
.error {
  background-color: #fbe9e7;
  color: #c62828;
  border: 1px solid #f4c7c3;
}
</style>
