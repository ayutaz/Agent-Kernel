<script setup>
import { computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'

use([CanvasRenderer, LineChart, GridComponent, TooltipComponent, LegendComponent])

const props = defineProps({
  data: { type: Object, required: true },
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
  energy: '\u30A8\u30CD\u30EB\u30AE\u30FC',
  happiness: '\u5E78\u798F\u5EA6',
  stress: '\u30B9\u30C8\u30EC\u30B9',
  socialization: '\u793E\u4EA4\u6027',
  money: '\u8CC7\u91D1',
}

const option = computed(() => {
  const textColor = props.isDark ? '#e5e7eb' : '#374151'
  const series = Object.keys(STATUS_COLORS).map(key => ({
    name: STATUS_LABELS[key],
    type: 'line',
    smooth: true,
    data: props.data[key] || [],
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
    xAxis: { type: 'category', data: props.data.ticks || [], axisLine: { lineStyle: { color: textColor } } },
    yAxis: { type: 'value', axisLine: { lineStyle: { color: textColor } }, splitLine: { lineStyle: { color: props.isDark ? '#374151' : '#e5e7eb' } } },
    series,
  }
})
</script>

<template>
  <v-chart :option="option" autoresize style="height: 350px;" />
</template>
