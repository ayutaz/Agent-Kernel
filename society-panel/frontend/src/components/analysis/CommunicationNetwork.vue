<script setup>
import { computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { GraphChart } from 'echarts/charts'
import { TooltipComponent, LegendComponent } from 'echarts/components'

use([CanvasRenderer, GraphChart, TooltipComponent, LegendComponent])

const props = defineProps({
  data: { type: Object, required: true },
  isDark: { type: Boolean, default: false }
})

const emit = defineEmits(['select-agent'])

const OCCUPATION_COLORS = {
  explorer: '#ef4444',
  socialite: '#f59e0b',
  scholar: '#3b82f6',
  merchant: '#22c55e',
  healer: '#ec4899',
  artist: '#8b5cf6',
  leader: '#f97316',
  guard: '#6366f1',
  farmer: '#84cc16',
  craftsman: '#06b6d4',
  unknown: '#6b7280',
}

const option = computed(() => {
  const textColor = props.isDark ? '#e5e7eb' : '#374151'
  const nodes = (props.data.nodes || []).map(n => ({
    id: n.id,
    name: n.name,
    value: n.value,
    symbolSize: Math.max(10, Math.min(50, 8 + Math.sqrt(n.value) * 4)),
    category: n.occupation || 'unknown',
    itemStyle: { color: OCCUPATION_COLORS[n.occupation] || OCCUPATION_COLORS.unknown },
    label: { show: n.value > 5, color: textColor, fontSize: 10 },
  }))
  const edges = (props.data.edges || []).map(e => ({
    source: e.source,
    target: e.target,
    value: e.value,
    lineStyle: {
      width: Math.max(1, Math.min(6, e.value / 2)),
      opacity: 0.4,
      color: props.isDark ? '#4b5563' : '#d1d5db',
    },
  }))
  const categories = [...new Set(nodes.map(n => n.category))].map(name => ({
    name,
    itemStyle: { color: OCCUPATION_COLORS[name] || OCCUPATION_COLORS.unknown },
  }))
  return {
    backgroundColor: 'transparent',
    textStyle: { color: textColor },
    tooltip: {
      trigger: 'item',
      formatter: (params) => {
        if (params.dataType === 'node') {
          return `<b>${params.name}</b><br/>職業: ${params.data.category}<br/>メッセージ: ${params.data.value}`
        }
        if (params.dataType === 'edge') {
          return `${params.data.source} ↔ ${params.data.target}<br/>メッセージ: ${params.data.value}`
        }
        return ''
      }
    },
    legend: {
      data: categories.map(c => c.name),
      textStyle: { color: textColor },
      orient: 'vertical',
      right: 10,
      top: 20,
    },
    series: [{
      type: 'graph',
      layout: 'force',
      data: nodes,
      edges,
      categories,
      roam: true,
      force: {
        repulsion: 200,
        edgeLength: [80, 200],
        gravity: 0.1,
      },
      emphasis: {
        focus: 'adjacency',
        lineStyle: { width: 4 },
      },
      draggable: true,
    }],
  }
})

function onChartClick(params) {
  if (params.dataType === 'node') {
    emit('select-agent', params.data.id)
  }
}
</script>

<template>
  <v-chart :option="option" autoresize style="height: 500px;" @click="onChartClick" />
</template>
