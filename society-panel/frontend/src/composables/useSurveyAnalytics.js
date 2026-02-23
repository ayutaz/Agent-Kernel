import { computed } from 'vue'
import { useReplayStore } from '../stores/replay'

export function useSurveyAnalytics() {
  const replayStore = useReplayStore()

  const frames = computed(() => replayStore.recording?.frames || [])
  const metadata = computed(() => replayStore.recording?.metadata || {})
  const profilesMap = computed(() => metadata.value.profiles || {})

  const isSurveyRecording = computed(() => metadata.value.experiment_type === 'disaster_response_survey')

  const experimentGroup = computed(() => metadata.value.group || 'mixed')

  const summary = computed(() => {
    const f = frames.value
    if (!f.length) return { collectiveRmse: 0, diversityBonus: 0, attributeCoverage: 0, agentCount: 0 }
    const lastMetrics = f[f.length - 1].survey_metrics || {}
    return {
      collectiveRmse: lastMetrics.collective_rmse ?? 0,
      diversityBonus: lastMetrics.diversity_bonus ?? 0,
      attributeCoverage: lastMetrics.attribute_coverage ?? 0,
      agentCount: metadata.value.n_agents || (f[f.length - 1].agents || []).length,
    }
  })

  const rmseTimeSeries = computed(() => {
    const f = frames.value
    if (!f.length) return { ticks: [], collective: [], avgIndividual: [], bestIndividual: [] }
    const ticks = [], collective = [], avgIndividual = [], bestIndividual = []
    for (const frame of f) {
      const m = frame.survey_metrics || {}
      ticks.push(frame.tick)
      collective.push(m.collective_rmse ?? 0)
      avgIndividual.push(m.avg_individual_rmse ?? 0)
      bestIndividual.push(m.best_individual_rmse ?? 0)
    }
    return { ticks, collective, avgIndividual, bestIndividual }
  })

  const diversityTimeSeries = computed(() => {
    const f = frames.value
    if (!f.length) return { ticks: [], bonus: [] }
    const ticks = [], bonus = []
    for (const frame of f) {
      const m = frame.survey_metrics || {}
      ticks.push(frame.tick)
      bonus.push(m.diversity_bonus ?? 0)
    }
    return { ticks, bonus }
  })

  const coverageTimeSeries = computed(() => {
    const f = frames.value
    if (!f.length) return { ticks: [], coverage: [] }
    const ticks = [], coverage = []
    for (const frame of f) {
      const m = frame.survey_metrics || {}
      ticks.push(frame.tick)
      coverage.push(m.attribute_coverage ?? 0)
    }
    return { ticks, coverage }
  })

  const specialistDistribution = computed(() => {
    const profiles = profilesMap.value
    const dist = {}
    for (const p of Object.values(profiles)) {
      const occ = p.occupation || 'unknown'
      dist[occ] = (dist[occ] || 0) + 1
    }
    return dist
  })

  const lastFrameAgents = computed(() => {
    const f = frames.value
    if (!f.length) return []
    return f[f.length - 1].agents || []
  })

  const regions = [
    { name: 'Site Alpha', position: [50, 50], radius: 40 },
    { name: 'Site Beta', position: [250, 50], radius: 40 },
    { name: 'Site Gamma', position: [150, 150], radius: 40 },
    { name: 'Site Delta', position: [50, 250], radius: 40 },
    { name: 'Site Epsilon', position: [250, 250], radius: 40 },
  ]

  return {
    isSurveyRecording,
    experimentGroup,
    summary,
    rmseTimeSeries,
    diversityTimeSeries,
    coverageTimeSeries,
    specialistDistribution,
    lastFrameAgents,
    regions,
    profilesMap,
  }
}
