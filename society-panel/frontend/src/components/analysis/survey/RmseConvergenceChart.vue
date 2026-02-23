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

const option = computed(() => {
  const textColor = props.isDark ? '#e5e7eb' : '#374151'
  return {
    backgroundColor: 'transparent',
    textStyle: { color: textColor },
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        let html = `Tick ${params[0].axisValue}<br/>`
        for (const p of params) {
          html += `${p.marker} ${p.seriesName}: ${p.value.toFixed(2)}<br/>`
        }
        return html
      }
    },
    legend: {
      data: ['Collective RMSE', 'Avg Individual RMSE', 'Best Individual RMSE'],
      textStyle: { color: textColor }
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
      name: 'RMSE',
      min: 0,
      axisLine: { lineStyle: { color: textColor } },
      splitLine: { lineStyle: { color: props.isDark ? '#374151' : '#e5e7eb' } }
    },
    series: [
      {
        name: 'Collective RMSE',
        type: 'line',
        data: props.data.collective || [],
        itemStyle: { color: '#ef4444' },
        lineStyle: { width: 3, color: '#ef4444' },
        symbol: 'circle',
        symbolSize: 6,
      },
      {
        name: 'Avg Individual RMSE',
        type: 'line',
        data: props.data.avgIndividual || [],
        itemStyle: { color: '#6b7280' },
        lineStyle: { width: 2, color: '#6b7280', type: 'dashed' },
        symbol: 'none',
      },
      {
        name: 'Best Individual RMSE',
        type: 'line',
        data: props.data.bestIndividual || [],
        itemStyle: { color: '#3b82f6' },
        lineStyle: { width: 1.5, color: '#3b82f6', type: 'dotted' },
        symbol: 'none',
      },
    ],
  }
})
</script>

<template>
  <v-chart :option="option" autoresize style="height: 350px;" />
</template>
