<script setup>
const props = defineProps({
  summary: { type: Object, required: true }
})

const cards = [
  { label: 'Ticks', key: 'ticks', icon: '\u23F1', color: '#3b82f6' },
  { label: '\u30E1\u30C3\u30BB\u30FC\u30B8\u6570', key: 'messages', icon: '\uD83D\uDCAC', color: '#22c55e' },
  { label: '\u30A8\u30FC\u30B8\u30A7\u30F3\u30C8\u6570', key: 'agents', icon: '\uD83D\uDC65', color: '#8b5cf6' },
  { label: '\u5E73\u5747\u5E78\u798F\u5EA6', key: 'avgHappiness', icon: '\uD83D\uDE0A', color: '#f59e0b' },
]
</script>

<template>
  <div class="summary-cards">
    <div
      v-for="card in cards"
      :key="card.key"
      class="panel-container summary-card"
    >
      <div class="card-icon" :style="{ color: card.color }">{{ card.icon }}</div>
      <div class="card-value" :style="{ color: card.color }">
        {{ typeof props.summary[card.key] === 'number'
          ? (Number.isInteger(props.summary[card.key])
            ? props.summary[card.key]
            : props.summary[card.key].toFixed(1))
          : props.summary[card.key] ?? '--' }}
      </div>
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
