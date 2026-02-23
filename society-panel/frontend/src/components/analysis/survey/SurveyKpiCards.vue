<script setup>
const props = defineProps({
  summary: { type: Object, required: true }
})

const cards = [
  { label: 'Collective RMSE', key: 'collectiveRmse', icon: '\uD83D\uDCCA', color: '#ef4444', format: v => v.toFixed(2) },
  { label: 'Diversity Bonus', key: 'diversityBonus', icon: '\uD83C\uDFAF', color: '#22c55e', format: v => v.toFixed(2) },
  { label: 'Attribute Coverage', key: 'attributeCoverage', icon: '\uD83D\uDD0D', color: '#3b82f6', format: v => Math.round(v * 100) + '%' },
  { label: 'Agent Count', key: 'agentCount', icon: '\uD83D\uDC65', color: '#8b5cf6', format: v => v },
]

function formatValue(card) {
  const val = props.summary[card.key]
  if (val == null) return '--'
  return card.format(val)
}
</script>

<template>
  <div class="summary-cards">
    <div v-for="card in cards" :key="card.key" class="panel-container summary-card">
      <div class="card-icon" :style="{ color: card.color }">{{ card.icon }}</div>
      <div class="card-value" :style="{ color: card.color }">{{ formatValue(card) }}</div>
      <div class="card-label">{{ card.label }}</div>
    </div>
  </div>
</template>

<style scoped>
.summary-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
}
.summary-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.4rem;
  padding: 1.5rem 1rem;
  text-align: center;
}
.card-icon {
  font-size: 1.8rem;
}
.card-value {
  font-size: 2rem;
  font-weight: 700;
  letter-spacing: -0.02em;
}
.card-label {
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--text-muted);
}
@media (max-width: 768px) {
  .summary-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
