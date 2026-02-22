<!-- Editor for core simulation parameters, module configs, and data paths. -->
<template>
  <div class="config-editor-container">
    <div v-if="isLoading" class="loading">設定を読み込み中...</div>
    <div v-else-if="error" class="message error">{{ error }}</div>

    <div v-if="configData">
      <div class="form-grid">
        <div class="form-group">
          <label for="pod-size">ポッドサイズ</label>
          <input id="pod-size" type="number" v-model.number="configData.simulation.pod_size" />
          <small>ポッドあたりの最大エージェント数。</small>
        </div>
        <div class="form-group">
          <label for="init-batch-size">初期バッチサイズ</label>
          <input id="init-batch-size" type="number" v-model.number="configData.simulation.init_batch_size" />
          <small>各初期化バッチで作成するエージェント数。</small>
        </div>
        <div class="form-group">
          <label for="max-ticks">最大Tick数</label>
          <input id="max-ticks" type="number" v-model.number="configData.simulation.max_ticks" />
          <small>シミュレーションを実行する最大タイムステップ数。</small>
        </div>
      </div>

      <h4 class="sub-header">モジュール設定パス</h4>
      <div class="form-grid path-grid">
        <div v-for="(path, key) in configData.configs" :key="key" class="form-group">
          <label :for="`config-path-${key}`">{{ key }}</label>
          <input :id="`config-path-${key}`" type="text" v-model="configData.configs[key]" />
        </div>
      </div>

      <h4 class="sub-header">データソースパス</h4>
      <div class="form-grid path-grid">
        <div v-for="(path, key) in configData.data" :key="key" class="form-group">
          <label :for="`data-path-${key}`">{{ key }}</label>
          <input :id="`data-path-${key}`" type="text" v-model="configData.data[key]" />
        </div>
      </div>

      <div class="actions">
        <button @click="saveConfig" :disabled="isSaving">
          {{ isSaving ? '保存中...' : 'シミュレーション設定を保存' }}
        </button>
        <div v-if="saveMessage" :class="['message', saveMessageType]">
          {{ saveMessage }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

const CONFIG_NAME = 'simulation_config.yaml';
const API_URL = `http://localhost:8001/api/configs/${CONFIG_NAME}`;

const configData = ref(null);
const isLoading = ref(true);
const isSaving = ref(false);
const error = ref('');
const saveMessage = ref('');
const saveMessageType = ref('success');

onMounted(async () => {
  try {
    const response = await axios.get(API_URL);
    if (!response.data.configs) response.data.configs = {};
    if (!response.data.data) response.data.data = {};
    configData.value = response.data;
  } catch (err) {
    error.value = `Failed to load config: ${err.response?.data?.detail || err.message}`;
  } finally {
    isLoading.value = false;
  }
});

const saveConfig = async () => {
  if (!configData.value) return;
  isSaving.value = true;
  saveMessage.value = '';
  try {
    const response = await axios.post(API_URL, configData.value);
    saveMessage.value = response.data.message;
    saveMessageType.value = 'success';
  } catch (err) {
    saveMessage.value = `Failed to save config: ${err.response?.data?.detail || err.message}`;
    saveMessageType.value = 'error';
  } finally {
    isSaving.value = false;
    setTimeout(() => { saveMessage.value = ''; }, 3000);
  }
};
</script>

<style scoped>
</style>
