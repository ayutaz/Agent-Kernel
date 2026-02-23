<script setup>
import { computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'

use([CanvasRenderer, LineChart, GridComponent, TooltipComponent])

const props = defineProps({
  data: { type: Object, required: true },
  isDark: { type: Boolean, default: false }
})

const option = computed(() => {
  const textColor = props.isDark ? '#e5e7eb' : '#374151'
  return {
    backgroundColor: 'transparent',
    textStyle: { color: textColor },
    tooltip: {
      trigger: 'axis',
      formatter: (params) => `Tick ${params[0].name}<br/>Diversity Bonus: ${params[0].value.toFixed(2)}`
    },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: props.data.ticks || [],
      name: 'Tick',
      axisLine: { lineStyle: { color: textColor } }
    },
    yAxis: {
      type: 'value',
      name: 'Diversity Bonus',
      axisLine: { lineStyle: { color: textColor } },
      splitLine: { lineStyle: { color: props.isDark ? '#374151' : '#e5e7eb' } }
    },
    series: [{
      type: 'line',
      smooth: true,
      data: props.data.bonus || [],
      areaStyle: { opacity: 0.2, color: '#22c55e' },
      itemStyle: { color: '#22c55e' },
      lineStyle: { width: 2, color: '#22c55e' },
      symbol: 'none',
    }],
  }
})
</script>

<template>
  <v-chart :option="option" autoresize style="height: 350px;" />
</template>
