<script setup>
import { computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { ScatterChart, EffectScatterChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'

use([CanvasRenderer, ScatterChart, EffectScatterChart, GridComponent, TooltipComponent, LegendComponent])

const props = defineProps({
  agents: { type: Array, required: true },
  regions: { type: Array, required: true },
  profiles: { type: Object, required: true },
  isDark: { type: Boolean, default: false }
})

const SPECIALIST_COLORS = {
  structural_engineer: '#ef4444',
  medical_officer: '#3b82f6',
  logistics_coordinator: '#22c55e',
  safety_inspector: '#f59e0b',
  community_liaison: '#8b5cf6',
}

function formatLabel(key) {
  return key.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')
}

const option = computed(() => {
  const textColor = props.isDark ? '#e5e7eb' : '#374151'

  // Region series (EffectScatter for pulsing effect on evacuation sites)
  const regionSeries = {
    name: 'Evacuation Sites',
    type: 'effectScatter',
    data: props.regions.map(r => ({
      value: [...r.position, r.radius],
      name: r.name,
    })),
    symbolSize: 80,
    rippleEffect: { brushType: 'stroke', scale: 3, period: 4 },
    itemStyle: {
      color: 'rgba(59, 130, 246, 0.08)',
      borderColor: 'rgba(59, 130, 246, 0.3)',
      borderWidth: 2,
    },
    label: {
      show: true,
      formatter: '{b}',
      position: 'inside',
      color: textColor,
      fontSize: 11,
    },
    zlevel: 0,
  }

  // Agent series: group by occupation
  const byOccupation = {}
  for (const agent of props.agents) {
    const profile = props.profiles[agent.id] || {}
    const occ = profile.occupation || 'unknown'
    if (!byOccupation[occ]) byOccupation[occ] = []
    byOccupation[occ].push(agent)
  }

  const agentSeriesList = Object.entries(byOccupation).map(([occ, agents]) => ({
    name: formatLabel(occ),
    type: 'scatter',
    data: agents.map(a => ({
      value: a.position,
      name: a.id,
    })),
    symbolSize: 10,
    itemStyle: { color: SPECIALIST_COLORS[occ] || '#6b7280' },
    zlevel: 1,
  }))

  const legendData = ['Evacuation Sites', ...Object.keys(byOccupation).map(formatLabel)]

  return {
    backgroundColor: 'transparent',
    textStyle: { color: textColor },
    tooltip: {
      trigger: 'item',
      formatter: (params) => {
        if (params.seriesName === 'Evacuation Sites') return params.name
        return `${params.name}<br/>${params.seriesName}`
      }
    },
    legend: {
      data: legendData,
      textStyle: { color: textColor },
      bottom: 0,
    },
    grid: { left: '3%', right: '4%', bottom: '12%', top: '3%', containLabel: true },
    xAxis: {
      type: 'value',
      min: 0,
      max: 300,
      name: 'X',
      axisLine: { lineStyle: { color: textColor } },
      splitLine: { lineStyle: { color: props.isDark ? '#374151' : '#e5e7eb' } }
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 300,
      name: 'Y',
      axisLine: { lineStyle: { color: textColor } },
      splitLine: { lineStyle: { color: props.isDark ? '#374151' : '#e5e7eb' } }
    },
    series: [regionSeries, ...agentSeriesList],
  }
})
</script>

<template>
  <v-chart :option="option" autoresize style="height: 400px;" />
</template>
