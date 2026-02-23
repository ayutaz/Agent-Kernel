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
  const entries = Object.entries(props.data).map(([name, value]) => ({
    name: formatLabel(name),
    value,
    itemStyle: { color: SPECIALIST_COLORS[name] || '#6b7280' }
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
