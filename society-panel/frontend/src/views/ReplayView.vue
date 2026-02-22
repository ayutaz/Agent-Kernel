<!-- Replay view for playing back recorded simulation data. -->
<script setup>
import { ref, computed } from 'vue'
import { useReplayStore } from '../stores/replay'
import AgentMapCanvas from '../components/map/AgentMapCanvas.vue'
import PlaybackControls from '../components/replay/PlaybackControls.vue'
import RecordingList from '../components/replay/RecordingList.vue'

const replayStore = useReplayStore()

const selectedAgentId = ref(null)
const hoveredAgentId = ref(null)

function onAgentClick(id) {
  selectedAgentId.value = selectedAgentId.value === id ? null : id
}

function onAgentHover(id) {
  hoveredAgentId.value = id
}

const selectedAgent = computed(() => {
  if (!selectedAgentId.value) return null
  return replayStore.agents.find(a => a.id === selectedAgentId.value) || null
})
</script>

<template>
  <div class="replay-view">
    <div class="page-header">
      <h1>Replay</h1>
      <p>Play back recorded simulation runs to review agent movements.</p>
    </div>

    <div class="replay-grid">
      <div class="main-panel">
        <div class="panel-container map-panel">
          <div class="map-header">
            <h3>Replay View</h3>
            <div class="map-meta" v-if="replayStore.recording">
              <span class="meta-chip meta-chip--ok">
                Tick {{ replayStore.currentTick ?? '-' }}
              </span>
              <span class="meta-chip">
                {{ replayStore.agents.length }} agents
              </span>
            </div>
          </div>

          <div v-if="replayStore.recording && replayStore.agents.length > 0" class="map-canvas-wrapper">
            <AgentMapCanvas
              :agents-override="replayStore.agents"
              :map-size-override="replayStore.mapSize"
              :selected-agent-id-override="selectedAgentId"
              :hovered-agent-id-override="hoveredAgentId"
              @agent-click="onAgentClick"
              @agent-hover="onAgentHover"
            />
          </div>
          <div v-else class="map-placeholder">
            <p v-if="replayStore.loadingRecording">Loading recording...</p>
            <p v-else>Select a recording from the list to start playback.</p>
          </div>
        </div>

        <PlaybackControls v-if="replayStore.recording" />
      </div>

      <div class="side-panel">
        <RecordingList />

        <div class="panel-container detail-panel" v-if="replayStore.recording">
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
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-header {
  margin-bottom: 2rem;
}

.replay-grid {
  display: grid;
  grid-template-columns: minmax(0, 3fr) minmax(0, 1fr);
  gap: 2rem;
  align-items: start;
}

.main-panel {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.side-panel {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.map-panel h3 {
  margin-top: 0;
  margin-bottom: 0;
}

.map-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.map-meta {
  display: flex;
  gap: 0.5rem;
}

.meta-chip {
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.25rem 0.6rem;
  border-radius: 999px;
  background: var(--chip-bg, #eee);
  color: var(--text-secondary, #555);
  border: 1px solid var(--border-soft, #ddd);
}

.meta-chip--ok {
  background: color-mix(in srgb, #22c55e 15%, transparent);
  color: #16a34a;
  border-color: color-mix(in srgb, #22c55e 30%, transparent);
}

[data-theme='dark'] .meta-chip--ok {
  color: #4ade80;
}

.map-canvas-wrapper {
  width: 100%;
}

.map-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  border: 2px dashed var(--border-soft, #ddd);
  border-radius: var(--border-radius-lg, 12px);
  background: var(--bg-inset-light, #fafafa);
}

[data-theme='dark'] .map-placeholder {
  background: rgba(255, 255, 255, 0.02);
}

.map-placeholder p {
  text-align: center;
  color: var(--text-muted, #888);
  font-size: 0.95rem;
  max-width: 40ch;
}

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

@media (max-width: 1024px) {
  .replay-grid {
    grid-template-columns: 1fr;
  }
}
</style>
