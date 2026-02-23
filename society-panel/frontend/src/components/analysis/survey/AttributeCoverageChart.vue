<script setup>
import { computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, MarkLineComponent } from 'echarts/components'

use([CanvasRenderer, LineChart, GridComponent, TooltipComponent, MarkLineComponent])

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
      formatter: (params) => `Tick ${params[0].name}<br/>Coverage: ${Math.round(params[0].value * 100)}%`
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
      name: 'Coverage',
      min: 0,
      max: 1,
      axisLabel: { formatter: v => Math.round(v * 100) + '%' },
      axisLine: { lineStyle: { color: textColor } },
      splitLine: { lineStyle: { color: props.isDark ? '#374151' : '#e5e7eb' } }
    },
    series: [{
      type: 'line',
      step: 'end',
      data: props.data.coverage || [],
      areaStyle: { opacity: 0.15, color: '#8b5cf6' },
      itemStyle: { color: '#8b5cf6' },
      lineStyle: { width: 2, color: '#8b5cf6' },
      symbol: 'circle',
      symbolSize: 6,
      markLine: {
        silent: true,
        symbol: 'none',
        lineStyle: { color: '#8b5cf6', type: 'dashed', width: 1 },
        data: [{ yAxis: 1.0, label: { formatter: '100%', position: 'end', color: textColor } }]
      }
    }],
  }
})
</script>

<template>
  <v-chart :option="option" autoresize style="height: 350px;" />
</template>
