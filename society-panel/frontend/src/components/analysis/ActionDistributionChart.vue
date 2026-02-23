<script setup>
import { computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart } from 'echarts/charts'
import { TooltipComponent, LegendComponent } from 'echarts/components'

use([CanvasRenderer, PieChart, TooltipComponent, LegendComponent])

const props = defineProps({
  data: { type: Object, required: true },
  isDark: { type: Boolean, default: false }
})

const ACTION_COLORS = {
  move: '#3b82f6',
  chat: '#22c55e',
  rest: '#f59e0b',
  give: '#ec4899',
  help: '#8b5cf6',
  unknown: '#6b7280',
}

const option = computed(() => {
  const textColor = props.isDark ? '#e5e7eb' : '#374151'
  const entries = Object.entries(props.data).map(([name, value]) => ({
    name,
    value,
    itemStyle: { color: ACTION_COLORS[name] || '#6b7280' }
  }))
  return {
    backgroundColor: 'transparent',
    textStyle: { color: textColor },
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { orient: 'vertical', right: '5%', top: 'center', textStyle: { color: textColor } },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['40%', '50%'],
      avoidLabelOverlap: true,
      label: { show: false },
      emphasis: { label: { show: true, fontSize: 14 } },
      data: entries,
    }],
  }
})
</script>

<template>
  <v-chart :option="option" autoresize style="height: 350px;" />
</template>
