<script setup>
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import { useReplayStore } from '../../stores/replay'

const replayStore = useReplayStore()

const totalMessages = computed(() => {
  if (!replayStore.recording) return 0
  return replayStore.recording.frames.reduce((sum, f) => sum + (f.messages?.length || 0), 0)
})

const avgHappiness = computed(() => {
  if (!replayStore.recording) return 0
  const frames = replayStore.recording.frames
  if (!frames.length) return 0
  const lastFrame = frames[frames.length - 1]
  const agents = lastFrame.agents || []
  if (!agents.length) return 0
  const avg = agents.reduce((sum, a) => sum + (a.status?.happiness || 0), 0) / agents.length
  return Math.round(avg * 10) / 10
})

const avgEnergy = computed(() => {
  if (!replayStore.recording) return 0
  const frames = replayStore.recording.frames
  if (!frames.length) return 0
  const lastFrame = frames[frames.length - 1]
  const agents = lastFrame.agents || []
  if (!agents.length) return 0
  const avg = agents.reduce((sum, a) => sum + (a.status?.energy || 0), 0) / agents.length
  return Math.round(avg * 10) / 10
})
</script>

<template>
  <div class="summary-strip">
    <div class="strip-kpis">
      <div class="strip-kpi">
        <span class="kpi-value">{{ totalMessages }}</span>
        <span class="kpi-label">メッセージ</span>
      </div>
      <div class="strip-kpi">
        <span class="kpi-value">{{ avgHappiness }}</span>
        <span class="kpi-label">平均幸福度</span>
      </div>
      <div class="strip-kpi">
        <span class="kpi-value">{{ avgEnergy }}</span>
        <span class="kpi-label">平均エネルギー</span>
      </div>
    </div>
    <RouterLink to="/analysis" class="analysis-link">
      詳細分析へ →
    </RouterLink>
  </div>
</template>

<style scoped>
.summary-strip {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1.25rem;
  border-radius: 12px;
  background: var(--card-bg);
  border: 1px solid var(--border-soft);
  backdrop-filter: blur(8px);
}
.strip-kpis {
  display: flex;
  gap: 2rem;
}
.strip-kpi {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.15rem;
}
.kpi-value {
  font-size: 1.25rem;
  font-weight: 700;
  font-family: var(--font-family-mono, monospace);
  color: var(--text-primary);
}
.kpi-label {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.analysis-link {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--accent);
  text-decoration: none;
  padding: 0.4rem 1rem;
  border-radius: 8px;
  border: 1px solid var(--accent);
  transition: all 200ms ease;
}
.analysis-link:hover {
  background: var(--accent);
  color: white;
}
@media (max-width: 640px) {
  .summary-strip {
    flex-direction: column;
    gap: 0.75rem;
  }
}
</style>
