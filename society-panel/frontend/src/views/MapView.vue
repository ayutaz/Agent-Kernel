<!-- Map view for visualizing agent positions in the simulation space. -->
<script setup>
import { onMounted, onUnmounted } from 'vue'
import { useMapStore } from '../stores/map'
import AgentMapCanvas from '../components/map/AgentMapCanvas.vue'
import AgentDetailPanel from '../components/map/AgentDetailPanel.vue'

const mapStore = useMapStore()

onMounted(() => {
  mapStore.startPolling(3000)
})

onUnmounted(() => {
  mapStore.stopPolling()
})
</script>

<template>
  <div class="map-view">
    <div class="page-header">
      <h1>エージェントマップ</h1>
      <p>シミュレーション空間におけるエージェント位置のリアルタイム表示。</p>
    </div>

    <div class="map-grid">
      <div class="main-panel">
        <div class="panel-container map-panel">
          <div class="map-header">
            <h3>マップビュー</h3>
            <div class="map-meta">
              <span v-if="mapStore.status === 'ok'" class="meta-chip meta-chip--ok">
                Tick {{ mapStore.currentTick ?? '-' }}
              </span>
              <span v-else-if="mapStore.status === 'not_running'" class="meta-chip meta-chip--idle">
                停止中
              </span>
              <span v-else class="meta-chip meta-chip--error">
                エラー
              </span>
              <span class="meta-chip">
                {{ mapStore.agentCount }} エージェント
              </span>
            </div>
          </div>

          <div v-if="mapStore.status === 'ok' && mapStore.agents.length > 0" class="map-canvas-wrapper">
            <AgentMapCanvas />
          </div>
          <div v-else class="map-placeholder">
            <p v-if="mapStore.status === 'not_running'">
              ダッシュボードからシミュレーションを開始すると、エージェントの位置が表示されます。
            </p>
            <p v-else-if="mapStore.status === 'error'">
              エージェント位置の取得に失敗しました。バックエンド接続を確認してください。
            </p>
            <p v-else>
              エージェントデータを待機中...
            </p>
          </div>
        </div>
      </div>

      <div class="side-panel">
        <AgentDetailPanel />
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-header {
  margin-bottom: 2rem;
}

.map-grid {
  display: grid;
  grid-template-columns: minmax(0, 3fr) minmax(0, 1fr);
  gap: 2rem;
  align-items: start;
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

.meta-chip--idle {
  background: color-mix(in srgb, #f59e0b 15%, transparent);
  color: #d97706;
  border-color: color-mix(in srgb, #f59e0b 30%, transparent);
}

[data-theme='dark'] .meta-chip--idle {
  color: #fbbf24;
}

.meta-chip--error {
  background: color-mix(in srgb, #ef4444 15%, transparent);
  color: #dc2626;
  border-color: color-mix(in srgb, #ef4444 30%, transparent);
}

[data-theme='dark'] .meta-chip--error {
  color: #f87171;
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

@media (max-width: 1024px) {
  .map-grid {
    grid-template-columns: 1fr;
  }
}
</style>
