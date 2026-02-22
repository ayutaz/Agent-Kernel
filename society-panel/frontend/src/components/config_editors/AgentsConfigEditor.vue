<!-- Editor for agent templates configuration with plugin selection and parameter management. -->
<template>
  <div class="config-editor-container">
    <div v-if="isLoading" class="loading">データを読み込み中...</div>
    <div v-else-if="error" class="message error">{{ error }}</div>

    <div v-if="configData && availablePlugins">
      <div v-for="(template, templateIndex) in configData.templates" :key="template.name" class="template-section">
        <div class="template-header">
          <h3>テンプレート: {{ template.name }}</h3>
          <button @click="removeTemplate(templateIndex)" class="remove-btn">テンプレート削除</button>
        </div>

        <div class="form-grid">
          <div class="form-group">
            <label>テンプレート名</label>
            <input type="text" v-model="template.name" />
          </div>
          <div class="form-group">
            <label>コンポーネント実行順序</label>
            <input type="text" :value="Array.isArray(template.component_order) ? template.component_order.join(',') : template.component_order" @input="updateComponentOrder(template, $event.target.value)" placeholder="e.g., perceive,plan,act" />
            <small>コンポーネントの実行順序をカンマ区切りで指定。</small>
          </div>
        </div>

        <div class="components-grid">
          <div v-for="(component, componentName) in template.components" :key="componentName" class="component-card">
            <h4>コンポーネント: <code>{{ componentName }}</code></h4>

            <div class="form-group">
              <label>プラグイン</label>
              <select :value="getCurrentPluginName(component)" @change="onPluginChange(component, componentName, $event.target.value)">
                <option disabled value="">プラグインを選択</option>
                <option v-for="plugin in availablePlugins.agent_plugins[componentName]" :key="plugin" :value="plugin">
                  {{ plugin }}
                </option>
              </select>
            </div>

            <div v-if="getCurrentPluginConfig(component)" class="plugin-params">
              <div v-for="(paramValue, paramKey) in getCurrentPluginConfig(component)" :key="paramKey" class="form-group with-delete">
                <label>{{ paramKey }}</label>
                <input type="text" :value="formatParamValue(paramValue)" @input="updatePluginParam(component, paramKey, $event.target.value)" />
                <button @click="removePluginParam(component, paramKey)" class="delete-field-btn" title="パラメータを削除">×</button>
              </div>
              <div class="add-field-section">
                <input type="text" v-model="newParam[template.name][componentName].key" placeholder="新規パラメータ名">
                <input type="text" v-model="newParam[template.name][componentName].value" placeholder="値">
                <button @click="addPluginParam(component, template.name, componentName)">追加</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="add-section">
        <input type="text" v-model="newTemplateName" placeholder="新規テンプレート名">
        <button @click="addTemplate" :disabled="!newTemplateName">新規テンプレート追加</button>
      </div>

      <div class="actions">
        <button @click="saveConfig" :disabled="isSaving">
          {{ isSaving ? '保存中...' : 'エージェント設定を保存' }}
        </button>
        <div v-if="saveMessage" :class="['message', saveMessageType]">
          {{ saveMessage }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue';
import axios from 'axios';

const CONFIG_NAME = 'agents_config.yaml';
const API_URL = `http://localhost:8001/api/configs/${CONFIG_NAME}`;
const PLUGINS_API_URL = 'http://localhost:8001/api/registry/plugins';

const configData = ref(null);
const availablePlugins = ref(null);
const isLoading = ref(true);
const isSaving = ref(false);
const error = ref('');
const saveMessage = ref('');
const saveMessageType = ref('success');
const newTemplateName = ref('');

const newParam = reactive({});

const initializeNewParam = (data) => {
  if (!data || !data.templates) return;
  data.templates.forEach(template => {
    newParam[template.name] = {};
    if (template.components) {
      Object.keys(template.components).forEach(compName => {
        newParam[template.name][compName] = { key: '', value: '' };
      });
    }
  });
};

onMounted(async () => {
  try {
    const [configResponse, pluginsResponse] = await Promise.all([
      axios.get(API_URL),
      axios.get(PLUGINS_API_URL)
    ]);
    configData.value = configResponse.data;
    availablePlugins.value = pluginsResponse.data;
    initializeNewParam(configData.value);
  } catch (err) {
    error.value = `Failed to load initial data: ${err.response?.data?.detail || err.message}`;
  } finally {
    isLoading.value = false;
  }
});

const getCurrentPluginName = (component) => component?.plugin ? Object.keys(component.plugin)[0] || '' : '';
const getCurrentPluginConfig = (component) => {
  const pluginName = getCurrentPluginName(component);
  return pluginName ? component.plugin[pluginName] : null;
};
const formatParamValue = (value) => (typeof value === 'object' && value !== null) ? JSON.stringify(value) : String(value);

const updateComponentOrder = (template, value) => {
  template.component_order = value.split(',').map(s => s.trim()).filter(Boolean);
};

const onPluginChange = (component, componentName, newPluginName) => {
  const oldConfig = getCurrentPluginConfig(component) || { adapters: {} };
  component.plugin = { [newPluginName]: oldConfig };
};

const updatePluginParam = (component, paramKey, newValue) => {
  const pluginConfig = getCurrentPluginConfig(component);
  if (pluginConfig) {
    try {
      pluginConfig[paramKey] = JSON.parse(newValue);
    } catch (e) {
      pluginConfig[paramKey] = newValue;
    }
  }
};

const addPluginParam = (component, templateName, componentName) => {
  const pluginConfig = getCurrentPluginConfig(component);
  const paramData = newParam[templateName][componentName];
  if (!pluginConfig || !paramData.key || pluginConfig.hasOwnProperty(paramData.key)) {
    alert('Please enter a unique parameter name.');
    return;
  }
  updatePluginParam(component, paramData.key, paramData.value);
  paramData.key = '';
  paramData.value = '';
};

const removePluginParam = (component, paramKey) => {
  const pluginConfig = getCurrentPluginConfig(component);
  if (pluginConfig && confirm(`Are you sure you want to remove the parameter "${paramKey}"?`)) {
    delete pluginConfig[paramKey];
  }
};

const addTemplate = () => {
  if (!newTemplateName.value || configData.value.templates.some(t => t.name === newTemplateName.value)) {
    alert('Please enter a unique name for the new template.');
    return;
  }
  const newTpl = {
    name: newTemplateName.value,
    component_order: ["perceive", "plan", "act", "state", "reflect"],
    components: {
      profile: { plugin: { ProfileStoragePlugin: { adapters: { redis: "RedisKVAdapter" }, profile_data: "agent_profiles" } } },
      state: { plugin: { StateStoragePlugin: { adapters: { redis: "RedisKVAdapter" }, state_data: "agent_states" } } },
      plan: { plugin: { LinearPlannerPlugin: { adapters: { redis: "RedisKVAdapter" } } } },
      act: { plugin: { LinearInvokePlugin: { adapters: { redis: "RedisKVAdapter" } } } },
      perceive: { plugin: { BasicPerceptionPlugin: { adapters: { redis: "RedisKVAdapter" } } } },
      reflect: { plugin: { InsightCreationPlugin: { adapters: { redis: "RedisKVAdapter" } } } },
    }
  };
  configData.value.templates.push(newTpl);
  newParam[newTpl.name] = {};
  Object.keys(newTpl.components).forEach(compName => {
    newParam[newTpl.name][compName] = { key: '', value: '' };
  });
  newTemplateName.value = '';
};

const removeTemplate = (index) => {
  if (confirm(`Are you sure you want to remove this template?`)) {
    const templateName = configData.value.templates[index].name;
    configData.value.templates.splice(index, 1);
    delete newParam[templateName];
  }
};

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
