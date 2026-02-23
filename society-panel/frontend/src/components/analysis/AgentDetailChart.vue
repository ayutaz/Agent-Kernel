<script setup>
import { computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'

use([CanvasRenderer, LineChart, GridComponent, TooltipComponent, LegendComponent])

const props = defineProps({
  agentId: { type: String, required: true },
  history: { type: Object, required: true },
  profile: { type: Object, default: null },
  isDark: { type: Boolean, default: false }
})

const STATUS_COLORS = {
  energy: '#f59e0b',
  happiness: '#22c55e',
  stress: '#8b5cf6',
  socialization: '#3b82f6',
  money: '#06b6d4',
}
const STATUS_LABELS = {
  energy: 'エネルギー',
  happiness: '幸福度',
  stress: 'ストレス',
  socialization: '社交性',
  money: '資金',
}

const option = computed(() => {
  const textColor = props.isDark ? '#e5e7eb' : '#374151'
  const keys = ['energy', 'happiness', 'stress', 'socialization', 'money']
  const series = keys.map(key => ({
    name: STATUS_LABELS[key],
    type: 'line',
    smooth: true,
    data: props.history[key] || [],
    itemStyle: { color: STATUS_COLORS[key] },
    lineStyle: { width: 2 },
    symbol: 'none',
  }))
  return {
    backgroundColor: 'transparent',
    textStyle: { color: textColor },
    tooltip: { trigger: 'axis' },
    legend: { data: Object.values(STATUS_LABELS), textStyle: { color: textColor } },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: props.history.ticks || [], name: 'Tick', axisLine: { lineStyle: { color: textColor } } },
    yAxis: { type: 'value', axisLine: { lineStyle: { color: textColor } }, splitLine: { lineStyle: { color: props.isDark ? '#374151' : '#e5e7eb' } } },
    series,
  }
})
</script>

<template>
  <div class="agent-detail">
    <div v-if="profile" class="profile-info">
      <div class="profile-row">
        <span class="profile-label">ID</span>
        <span class="profile-value">{{ agentId }}</span>
      </div>
      <div class="profile-row">
        <span class="profile-label">性格</span>
        <span class="profile-value">{{ profile.personality }}</span>
      </div>
      <div class="profile-row">
        <span class="profile-label">職業</span>
        <span class="profile-value">{{ profile.occupation }}</span>
      </div>
      <div class="profile-row">
        <span class="profile-label">目標</span>
        <span class="profile-value">{{ profile.goal }}</span>
      </div>
    </div>
    <v-chart :option="option" autoresize style="height: 350px;" />
  </div>
</template>

<style scoped>
.agent-detail {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.profile-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 0.5rem;
}
.profile-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 0.75rem;
  border-radius: 8px;
  background: var(--bg-inset-light, #f5f5f5);
}
[data-theme='dark'] .profile-row {
  background: rgba(255, 255, 255, 0.05);
}
.profile-label {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-muted, #888);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  white-space: nowrap;
}
.profile-value {
  font-size: 0.9rem;
  color: var(--text-primary, #222);
}
</style>
