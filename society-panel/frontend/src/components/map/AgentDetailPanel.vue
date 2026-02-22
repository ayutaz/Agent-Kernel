<!-- Detail panel showing selected agent information. -->
<script setup>
import { computed } from 'vue'
import { useMapStore } from '../../stores/map'

const mapStore = useMapStore()

const selectedAgent = computed(() => {
  if (!mapStore.selectedAgentId) return null
  return mapStore.agents.find(a => a.id === mapStore.selectedAgentId) || null
})
</script>

<template>
  <div class="panel-container detail-panel">
    <h3>Agent Detail</h3>
    <div v-if="selectedAgent" class="agent-info">
      <div class="info-row">
        <span class="info-label">ID</span>
        <span class="info-value">{{ selectedAgent.id }}</span>
      </div>
      <div class="info-row">
        <span class="info-label">X</span>
        <span class="info-value">{{ selectedAgent.position[0] }}</span>
      </div>
      <div class="info-row">
        <span class="info-label">Y</span>
        <span class="info-value">{{ selectedAgent.position[1] }}</span>
      </div>
    </div>
    <div v-else class="placeholder">
      <p>Click an agent on the map to view details.</p>
    </div>
  </div>
</template>

<style scoped>
.detail-panel h3 {
  margin-top: 0;
  margin-bottom: 1rem;
  font-size: 1.1rem;
  color: var(--text-primary);
}

.agent-info {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  background: var(--bg-inset-light, #f5f5f5);
}

[data-theme='dark'] .info-row {
  background: rgba(255, 255, 255, 0.05);
}

.info-label {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-muted, #888);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.info-value {
  font-size: 0.95rem;
  font-weight: 500;
  font-family: var(--font-family-mono, monospace);
  color: var(--text-primary, #222);
}

.placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100px;
}

.placeholder p {
  text-align: center;
  color: var(--text-muted, #888);
  font-size: 0.9rem;
  margin: 0;
}
</style>
