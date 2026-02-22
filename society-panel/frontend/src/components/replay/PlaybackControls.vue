<!-- Playback controls for simulation recording replay. -->
<script setup>
import { useReplayStore } from '../../stores/replay'

const replayStore = useReplayStore()

const speeds = [0.5, 1, 2, 4]
</script>

<template>
  <div class="panel-container playback-panel">
    <div class="controls-row">
      <button class="ctrl-btn" @click="replayStore.stepBackward()" title="前のフレーム">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <polyline points="11,17 6,12 11,7" />
          <line x1="18" y1="12" x2="6" y2="12" />
        </svg>
      </button>

      <button
        class="ctrl-btn ctrl-btn--play"
        @click="replayStore.togglePlayPause()"
        :title="replayStore.isPlaying ? '一時停止' : '再生'"
      >
        <svg v-if="!replayStore.isPlaying" viewBox="0 0 24 24" fill="currentColor">
          <polygon points="6,4 20,12 6,20" />
        </svg>
        <svg v-else viewBox="0 0 24 24" fill="currentColor">
          <rect x="5" y="4" width="4" height="16" />
          <rect x="15" y="4" width="4" height="16" />
        </svg>
      </button>

      <button class="ctrl-btn" @click="replayStore.stepForward()" title="次のフレーム">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <polyline points="13,7 18,12 13,17" />
          <line x1="6" y1="12" x2="18" y2="12" />
        </svg>
      </button>

      <button class="ctrl-btn" @click="replayStore.stop()" title="停止">
        <svg viewBox="0 0 24 24" fill="currentColor">
          <rect x="6" y="6" width="12" height="12" rx="1" />
        </svg>
      </button>
    </div>

    <div class="speed-row">
      <span class="speed-label">速度</span>
      <button
        v-for="s in speeds"
        :key="s"
        class="speed-btn"
        :class="{ 'speed-btn--active': replayStore.playbackSpeed === s }"
        @click="replayStore.setSpeed(s)"
      >
        {{ s }}x
      </button>
    </div>

    <div class="timeline-row">
      <span class="tick-label">
        Tick {{ replayStore.currentTick ?? '-' }}
        <span class="frame-counter" v-if="replayStore.totalFrames > 0">
          ({{ replayStore.currentFrameIndex + 1 }}/{{ replayStore.totalFrames }})
        </span>
      </span>
      <input
        type="range"
        class="timeline-slider"
        :min="0"
        :max="Math.max(0, replayStore.totalFrames - 1)"
        :value="replayStore.currentFrameIndex"
        @input="replayStore.seekTo(Number($event.target.value))"
      />
    </div>
  </div>
</template>

<style scoped>
.playback-panel {
  padding: 16px 20px;
}

.controls-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.ctrl-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: 1px solid var(--border-soft, #ddd);
  border-radius: 8px;
  background: var(--bg-inset-light, #f5f5f5);
  color: var(--text-primary, #222);
  cursor: pointer;
  transition: all 180ms ease;
  padding: 0;
}

.ctrl-btn svg {
  width: 16px;
  height: 16px;
}

.ctrl-btn:hover {
  background: var(--accent-soft, #e0e7ff);
  border-color: var(--accent, #6366f1);
}

.ctrl-btn--play {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: var(--accent, #6366f1);
  color: #fff;
  border-color: var(--accent, #6366f1);
}

.ctrl-btn--play svg {
  width: 20px;
  height: 20px;
}

.ctrl-btn--play:hover {
  background: var(--accent-strong, #4f46e5);
  transform: scale(1.05);
}

[data-theme='dark'] .ctrl-btn {
  background: rgba(255, 255, 255, 0.06);
}

.speed-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  margin-bottom: 0.75rem;
}

.speed-label {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-muted, #888);
  margin-right: 0.25rem;
}

.speed-btn {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.2rem 0.55rem;
  border: 1px solid var(--border-soft, #ddd);
  border-radius: 999px;
  background: transparent;
  color: var(--text-secondary, #555);
  cursor: pointer;
  transition: all 180ms ease;
}

.speed-btn:hover {
  border-color: var(--accent, #6366f1);
  color: var(--accent, #6366f1);
}

.speed-btn--active {
  background: var(--accent, #6366f1);
  color: #fff;
  border-color: var(--accent, #6366f1);
}

.timeline-row {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.tick-label {
  font-size: 0.85rem;
  font-weight: 600;
  font-family: var(--font-family-mono, monospace);
  color: var(--text-primary, #222);
  text-align: center;
}

.frame-counter {
  color: var(--text-muted, #888);
  font-weight: 400;
}

.timeline-slider {
  width: 100%;
  height: 6px;
  -webkit-appearance: none;
  appearance: none;
  background: var(--border-soft, #ddd);
  border-radius: 3px;
  outline: none;
  cursor: pointer;
}

.timeline-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: var(--accent, #6366f1);
  cursor: pointer;
  border: 2px solid #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.2);
}

.timeline-slider::-moz-range-thumb {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: var(--accent, #6366f1);
  cursor: pointer;
  border: 2px solid #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.2);
}
</style>
