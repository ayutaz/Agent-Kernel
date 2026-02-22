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

const STATUS_DEFS = [
  { key: 'health', label: '体力', color: '#ef4444' },
  { key: 'energy', label: 'エネルギー', color: '#f59e0b' },
  { key: 'happiness', label: '幸福度', color: '#22c55e' },
  { key: 'stress', label: 'ストレス', color: '#8b5cf6' },
  { key: 'socialization', label: '社交性', color: '#3b82f6' },
  { key: 'money', label: '資金', color: '#06b6d4' },
]

const statusBars = computed(() => {
  if (!selectedAgent.value?.status) return []
  const st = selectedAgent.value.status
  return STATUS_DEFS.map(d => {
    const raw = st[d.key] ?? 0
    // money can exceed 100 — cap percentage at 100
    const pct = d.key === 'money' ? Math.min(100, raw / 100) : Math.min(100, raw)
    return { ...d, value: raw, pct }
  })
})

const filteredMessages = computed(() => {
  return replayStore.messages
})
</script>

<template>
  <div class="replay-view">
    <div class="page-header">
      <h1>録画再生</h1>
      <p>過去のシミュレーション実行を再生し、エージェントの動きを確認できます。</p>
    </div>

    <div class="replay-grid">
      <div class="main-panel">
        <div class="panel-container map-panel">
          <div class="map-header">
            <h3>再生ビュー</h3>
            <div class="map-meta" v-if="replayStore.recording">
              <span class="meta-chip meta-chip--ok">
                Tick {{ replayStore.currentTick ?? '-' }}
              </span>
              <span class="meta-chip">
                {{ replayStore.agents.length }} エージェント
              </span>
            </div>
          </div>

          <div v-if="replayStore.recording && replayStore.agents.length > 0" class="map-canvas-wrapper">
            <AgentMapCanvas
              :agents-override="replayStore.agents"
              :map-size-override="replayStore.mapSize"
              :selected-agent-id-override="selectedAgentId"
              :hovered-agent-id-override="hoveredAgentId"
              :agent-trails="replayStore.agentTrails"
              @agent-click="onAgentClick"
              @agent-hover="onAgentHover"
            />
          </div>
          <div v-else class="map-placeholder">
            <p v-if="replayStore.loadingRecording">録画を読み込み中...</p>
            <p v-else>一覧から録画を選択して再生を開始してください。</p>
          </div>
        </div>

        <PlaybackControls v-if="replayStore.recording" />
      </div>

      <div class="side-panel">
        <RecordingList />

        <div class="panel-container detail-panel" v-if="replayStore.recording">
          <h3>エージェント詳細</h3>
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

            <template v-if="selectedAgent.status">
              <div class="status-section-title">ステータス</div>
              <div v-for="stat in statusBars" :key="stat.key" class="status-bar-row">
                <span class="status-label">{{ stat.label }}</span>
                <div class="status-bar-track">
                  <div class="status-bar-fill" :style="{ width: stat.pct + '%', background: stat.color }"></div>
                </div>
                <span class="status-value">{{ stat.value }}</span>
              </div>
            </template>
          </div>
          <div v-else class="placeholder">
            <p>マップ上のエージェントをクリックすると詳細が表示されます。</p>
          </div>
        </div>

        <div class="panel-container message-panel" v-if="replayStore.recording">
          <h3>メッセージログ</h3>
          <div v-if="filteredMessages.length > 0" class="message-list">
            <div
              v-for="(msg, idx) in filteredMessages"
              :key="idx"
              class="message-item"
              :class="{ 'message-highlight': selectedAgentId && (msg.from_id === selectedAgentId || msg.to_id === selectedAgentId) }"
            >
              <span class="msg-from">{{ msg.from_id }}</span>
              <span class="msg-arrow">→</span>
              <span class="msg-to">{{ msg.to_id }}</span>
              <span class="msg-content">{{ msg.content }}</span>
            </div>
          </div>
          <div v-else class="placeholder">
            <p>このTickにメッセージはありません</p>
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

.status-section-title {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-muted, #888);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-top: 0.5rem;
}

.status-bar-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0;
}

.status-label {
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--text-secondary, #555);
  width: 5em;
  flex-shrink: 0;
}

.status-bar-track {
  flex: 1;
  height: 8px;
  background: var(--bg-inset-light, #eee);
  border-radius: 4px;
  overflow: hidden;
}

[data-theme='dark'] .status-bar-track {
  background: rgba(255, 255, 255, 0.1);
}

.status-bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.status-value {
  font-size: 0.8rem;
  font-family: var(--font-family-mono, monospace);
  color: var(--text-primary, #222);
  width: 3em;
  text-align: right;
  flex-shrink: 0;
}

.message-panel h3 {
  margin-top: 0;
  margin-bottom: 0.75rem;
  font-size: 1.1rem;
  color: var(--text-primary);
}

.message-list {
  max-height: 300px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.message-item {
  display: flex;
  align-items: baseline;
  gap: 0.35rem;
  padding: 0.4rem 0.6rem;
  border-radius: 6px;
  font-size: 0.85rem;
  background: var(--bg-inset-light, #f5f5f5);
}

[data-theme='dark'] .message-item {
  background: rgba(255, 255, 255, 0.05);
}

.message-highlight {
  background: color-mix(in srgb, #3b82f6 15%, transparent) !important;
  border-left: 3px solid #3b82f6;
}

[data-theme='dark'] .message-highlight {
  background: color-mix(in srgb, #60a5fa 20%, transparent) !important;
  border-left-color: #60a5fa;
}

.msg-from {
  font-weight: 600;
  color: var(--text-primary, #222);
  white-space: nowrap;
}

.msg-arrow {
  color: var(--text-muted, #888);
  flex-shrink: 0;
}

.msg-to {
  font-weight: 600;
  color: var(--text-primary, #222);
  white-space: nowrap;
}

.msg-content {
  color: var(--text-secondary, #555);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-left: 0.25rem;
}

@media (max-width: 1024px) {
  .replay-grid {
    grid-template-columns: 1fr;
  }
}
</style>
