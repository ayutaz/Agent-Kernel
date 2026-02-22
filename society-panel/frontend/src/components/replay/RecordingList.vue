<!-- List of available simulation recordings for replay. -->
<script setup>
import { onMounted } from 'vue'
import { useReplayStore } from '../../stores/replay'

const replayStore = useReplayStore()

onMounted(() => {
  replayStore.fetchRecordings()
})
</script>

<template>
  <div class="panel-container recording-list-panel">
    <div class="list-header">
      <h3>録画一覧</h3>
      <button class="refresh-btn" @click="replayStore.fetchRecordings()" title="更新">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="23,4 23,10 17,10" />
          <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10" />
        </svg>
      </button>
    </div>

    <div v-if="replayStore.loadingList" class="placeholder">
      <p>読み込み中...</p>
    </div>

    <div v-else-if="replayStore.recordings.length === 0" class="placeholder">
      <p>録画が見つかりません。シミュレーションを実行すると自動生成されます。</p>
    </div>

    <ul v-else class="recording-items">
      <li
        v-for="rec in replayStore.recordings"
        :key="rec.filename"
        class="recording-item"
        :class="{ 'recording-item--active': replayStore.recording?.metadata?.created_at === rec.created_at }"
        @click="replayStore.loadRecording(rec.filename)"
      >
        <div class="rec-info">
          <span class="rec-name">{{ rec.filename }}</span>
          <span class="rec-meta" v-if="!rec.error">
            {{ rec.total_ticks_recorded ?? '?' }} ティック / {{ rec.agent_count ?? '?' }} エージェント
          </span>
          <span class="rec-meta rec-meta--error" v-else>{{ rec.error }}</span>
        </div>
        <button
          class="delete-btn"
          @click.stop="replayStore.deleteRecording(rec.filename)"
          title="削除"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="3,6 5,6 21,6" />
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
          </svg>
        </button>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.recording-list-panel h3 {
  margin-top: 0;
  margin-bottom: 0;
  font-size: 1.1rem;
  color: var(--text-primary);
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.refresh-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border: 1px solid var(--border-soft, #ddd);
  border-radius: 6px;
  background: transparent;
  color: var(--text-secondary, #555);
  cursor: pointer;
  transition: all 180ms ease;
  padding: 0;
}

.refresh-btn svg {
  width: 14px;
  height: 14px;
}

.refresh-btn:hover {
  border-color: var(--accent, #6366f1);
  color: var(--accent, #6366f1);
}

.recording-items {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.recording-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.6rem 0.75rem;
  border-radius: 8px;
  border: 1px solid transparent;
  background: var(--bg-inset-light, #f5f5f5);
  cursor: pointer;
  transition: all 180ms ease;
}

[data-theme='dark'] .recording-item {
  background: rgba(255, 255, 255, 0.05);
}

.recording-item:hover {
  border-color: var(--accent, #6366f1);
  background: var(--accent-soft, #e0e7ff);
}

[data-theme='dark'] .recording-item:hover {
  background: rgba(99, 102, 241, 0.15);
}

.recording-item--active {
  border-color: var(--accent, #6366f1);
  background: color-mix(in srgb, var(--accent, #6366f1) 12%, transparent);
}

.rec-info {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  min-width: 0;
}

.rec-name {
  font-size: 0.8rem;
  font-weight: 600;
  font-family: var(--font-family-mono, monospace);
  color: var(--text-primary, #222);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.rec-meta {
  font-size: 0.72rem;
  color: var(--text-muted, #888);
}

.rec-meta--error {
  color: #ef4444;
}

.delete-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: var(--text-muted, #888);
  cursor: pointer;
  transition: all 180ms ease;
  padding: 0;
  flex-shrink: 0;
}

.delete-btn svg {
  width: 14px;
  height: 14px;
}

.delete-btn:hover {
  background: color-mix(in srgb, #ef4444 15%, transparent);
  color: #ef4444;
}

.placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 80px;
}

.placeholder p {
  text-align: center;
  color: var(--text-muted, #888);
  font-size: 0.85rem;
  margin: 0;
}
</style>
