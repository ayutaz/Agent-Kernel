<!-- Canvas-based agent map visualization with hover tooltips and click selection. -->
<script setup>
import { ref, watch, onMounted, onUnmounted, computed } from 'vue'
import { useMapStore } from '../../stores/map'
import { useThemeStore } from '../../stores/theme'

const props = defineProps({
  agentsOverride: { type: Array, default: null },
  mapSizeOverride: { type: Number, default: null },
  selectedAgentIdOverride: { type: String, default: null },
  hoveredAgentIdOverride: { type: String, default: null },
})
const emit = defineEmits(['agent-click', 'agent-hover'])

const mapStore = useMapStore()
const themeStore = useThemeStore()

const canvasRef = ref(null)
const containerRef = ref(null)
const canvasWidth = ref(600)
const canvasHeight = ref(600)
const tooltip = ref({ visible: false, x: 0, y: 0, text: '' })

const effectiveAgents = computed(() => props.agentsOverride ?? mapStore.agents)
const effectiveMapSize = computed(() => props.mapSizeOverride ?? mapStore.mapSize)
const effectiveSelectedAgentId = computed(() =>
  props.agentsOverride !== null ? props.selectedAgentIdOverride : mapStore.selectedAgentId)
const effectiveHoveredAgentId = computed(() =>
  props.agentsOverride !== null ? props.hoveredAgentIdOverride : mapStore.hoveredAgentId)

const isOverrideMode = computed(() => props.agentsOverride !== null)

const scale = computed(() => canvasWidth.value / effectiveMapSize.value)

let resizeObserver = null

function getColors() {
  const isDark = themeStore.isDark

  return {
    bg: isDark ? '#1a1a2e' : '#f8f9fc',
    grid: isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)',
    gridLabel: isDark ? 'rgba(255,255,255,0.25)' : 'rgba(0,0,0,0.25)',
    dot: isDark ? '#60a5fa' : '#3b82f6',
    dotHover: isDark ? '#fbbf24' : '#f59e0b',
    dotSelected: isDark ? '#f472b6' : '#ec4899',
    border: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)',
  }
}

function draw() {
  const canvas = canvasRef.value
  if (!canvas) return

  const dpr = window.devicePixelRatio || 1
  const w = canvasWidth.value
  const h = canvasHeight.value

  canvas.width = w * dpr
  canvas.height = h * dpr
  canvas.style.width = `${w}px`
  canvas.style.height = `${h}px`

  const ctx = canvas.getContext('2d')
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0)

  const colors = getColors()
  const s = scale.value
  const mSize = effectiveMapSize.value

  // Background
  ctx.fillStyle = colors.bg
  ctx.fillRect(0, 0, w, h)

  // Grid lines every 50 units
  ctx.strokeStyle = colors.grid
  ctx.lineWidth = 1
  const gridStep = 50
  for (let i = 0; i <= mSize; i += gridStep) {
    const pos = i * s
    ctx.beginPath()
    ctx.moveTo(pos, 0)
    ctx.lineTo(pos, h)
    ctx.stroke()
    ctx.beginPath()
    ctx.moveTo(0, pos)
    ctx.lineTo(w, pos)
    ctx.stroke()
  }

  // Grid labels
  ctx.fillStyle = colors.gridLabel
  ctx.font = '10px monospace'
  ctx.textAlign = 'left'
  ctx.textBaseline = 'top'
  for (let i = 0; i <= mSize; i += gridStep) {
    if (i === 0) continue
    const pos = i * s
    ctx.fillText(String(i), pos + 2, 2)
    ctx.fillText(String(i), 2, pos + 2)
  }

  // Agent dots
  const agents = effectiveAgents.value
  const selId = effectiveSelectedAgentId.value
  const hovId = effectiveHoveredAgentId.value
  for (const agent of agents) {
    const [ax, ay] = agent.position
    const cx = ax * s
    const cy = ay * s

    let radius = 4
    let fillColor = colors.dot

    if (agent.id === selId) {
      fillColor = colors.dotSelected
      radius = 6
    } else if (agent.id === hovId) {
      fillColor = colors.dotHover
      radius = 5
    }

    ctx.beginPath()
    ctx.arc(cx, cy, radius, 0, Math.PI * 2)
    ctx.fillStyle = fillColor
    ctx.fill()

    // Glow for selected
    if (agent.id === selId) {
      ctx.beginPath()
      ctx.arc(cx, cy, 10, 0, Math.PI * 2)
      ctx.strokeStyle = fillColor
      ctx.globalAlpha = 0.3
      ctx.lineWidth = 2
      ctx.stroke()
      ctx.globalAlpha = 1
      ctx.lineWidth = 1
    }
  }

  // Border
  ctx.strokeStyle = colors.border
  ctx.lineWidth = 1
  ctx.strokeRect(0, 0, w, h)
}

function findAgentAt(clientX, clientY) {
  const canvas = canvasRef.value
  if (!canvas) return null

  const rect = canvas.getBoundingClientRect()
  const mx = clientX - rect.left
  const my = clientY - rect.top
  const s = scale.value
  const hitRadius = 10

  let closest = null
  let closestDist = hitRadius

  for (const agent of effectiveAgents.value) {
    const [ax, ay] = agent.position
    const cx = ax * s
    const cy = ay * s
    const dist = Math.sqrt((mx - cx) ** 2 + (my - cy) ** 2)
    if (dist < closestDist) {
      closestDist = dist
      closest = agent
    }
  }

  return closest
}

function onMouseMove(e) {
  const agent = findAgentAt(e.clientX, e.clientY)
  if (agent) {
    if (isOverrideMode.value) {
      emit('agent-hover', agent.id)
    } else {
      mapStore.hoverAgent(agent.id)
    }
    const rect = canvasRef.value.getBoundingClientRect()
    tooltip.value = {
      visible: true,
      x: e.clientX - rect.left + 12,
      y: e.clientY - rect.top - 8,
      text: `${agent.id} (${agent.position[0]}, ${agent.position[1]})`
    }
  } else {
    if (isOverrideMode.value) {
      emit('agent-hover', null)
    } else {
      mapStore.hoverAgent(null)
    }
    tooltip.value.visible = false
  }
  draw()
}

function onMouseLeave() {
  if (isOverrideMode.value) {
    emit('agent-hover', null)
  } else {
    mapStore.hoverAgent(null)
  }
  tooltip.value.visible = false
  draw()
}

function onClick(e) {
  const agent = findAgentAt(e.clientX, e.clientY)
  if (isOverrideMode.value) {
    emit('agent-click', agent ? agent.id : null)
  } else {
    mapStore.selectAgent(agent ? agent.id : null)
  }
  draw()
}

function updateSize() {
  const container = containerRef.value
  if (!container) return
  const w = container.clientWidth
  canvasWidth.value = w
  canvasHeight.value = w
  draw()
}

onMounted(() => {
  resizeObserver = new ResizeObserver(updateSize)
  if (containerRef.value) {
    resizeObserver.observe(containerRef.value)
  }
  updateSize()
})

onUnmounted(() => {
  if (resizeObserver) {
    resizeObserver.disconnect()
  }
})

watch(() => effectiveAgents.value, draw, { deep: true })
watch(() => themeStore.isDark, draw)
watch(() => effectiveSelectedAgentId.value, draw)
watch(() => effectiveHoveredAgentId.value, draw)
</script>

<template>
  <div ref="containerRef" class="canvas-container">
    <canvas
      ref="canvasRef"
      @mousemove="onMouseMove"
      @mouseleave="onMouseLeave"
      @click="onClick"
    />
    <div
      v-if="tooltip.visible"
      class="map-tooltip"
      :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }"
    >
      {{ tooltip.text }}
    </div>
  </div>
</template>

<style scoped>
.canvas-container {
  position: relative;
  width: 100%;
  aspect-ratio: 1 / 1;
}

canvas {
  display: block;
  border-radius: var(--border-radius-lg, 12px);
  cursor: crosshair;
}

.map-tooltip {
  position: absolute;
  pointer-events: none;
  background: var(--card-bg, #fff);
  border: 1px solid var(--border-soft, #ddd);
  border-radius: 6px;
  padding: 4px 8px;
  font-size: 0.8rem;
  font-family: var(--font-family-mono, monospace);
  color: var(--text-primary, #222);
  white-space: nowrap;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  z-index: 10;
}
</style>
