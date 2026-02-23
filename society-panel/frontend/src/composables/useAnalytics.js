import { computed } from 'vue'
import { useReplayStore } from '../stores/replay'

export function useAnalytics() {
  const replayStore = useReplayStore()

  const frames = computed(() => replayStore.recording?.frames || [])
  const metadata = computed(() => replayStore.recording?.metadata || {})
  const profilesMap = computed(() => metadata.value.profiles || {})

  // Summary KPIs
  const summary = computed(() => {
    const f = frames.value
    if (!f.length) return { ticks: 0, messages: 0, agents: 0, avgHappiness: 0 }
    const totalMessages = f.reduce((sum, frame) => sum + (frame.messages?.length || 0), 0)
    const lastFrame = f[f.length - 1]
    const agents = lastFrame.agents || []
    const avgHappiness = agents.length
      ? agents.reduce((sum, a) => sum + (a.status?.happiness || 0), 0) / agents.length
      : 0
    return {
      ticks: f.length,
      messages: totalMessages,
      agents: agents.length,
      avgHappiness: Math.round(avgHappiness * 10) / 10,
    }
  })

  // Status time series: tick毎の全エージェント平均
  const statusTimeSeries = computed(() => {
    const f = frames.value
    if (!f.length)
      return { ticks: [], energy: [], happiness: [], stress: [], socialization: [], money: [] }
    const keys = ['energy', 'happiness', 'stress', 'socialization', 'money']
    const result = { ticks: [] }
    keys.forEach((k) => (result[k] = []))
    for (const frame of f) {
      result.ticks.push(frame.tick)
      const agents = frame.agents || []
      const count = agents.length || 1
      for (const key of keys) {
        const avg = agents.reduce((sum, a) => sum + (a.status?.[key] || 0), 0) / count
        result[key].push(Math.round(avg * 10) / 10)
      }
    }
    return result
  })

  // Action distribution: アクション種別ごとの総回数
  const actionDistribution = computed(() => {
    const f = frames.value
    const dist = {}
    for (const frame of f) {
      for (const agent of frame.agents || []) {
        let action = agent.action
        if (!action) {
          // 後方互換: actionフィールドがない古い録画
          action = 'unknown'
        }
        dist[action] = (dist[action] || 0) + 1
      }
    }
    // 古い録画の後方互換: メッセージからchatを推定
    if (!f.some((frame) => frame.agents?.some((a) => a.action))) {
      for (const frame of f) {
        const senders = new Set((frame.messages || []).map((m) => m.from_id))
        for (const agent of frame.agents || []) {
          if (senders.has(agent.id)) {
            dist['chat'] = (dist['chat'] || 0) + 1
            dist['unknown'] = Math.max(0, (dist['unknown'] || 0) - 1)
          }
        }
      }
      // 位置変化からmoveを推定
      for (let i = 1; i < f.length; i++) {
        const prevAgents = {}
        for (const a of f[i - 1].agents || []) {
          prevAgents[a.id] = a.position
        }
        for (const a of f[i].agents || []) {
          const prev = prevAgents[a.id]
          if (prev && (prev[0] !== a.position[0] || prev[1] !== a.position[1])) {
            dist['move'] = (dist['move'] || 0) + 1
            dist['unknown'] = Math.max(0, (dist['unknown'] || 0) - 1)
          }
        }
      }
    }
    // unknownが0以下なら削除
    if (dist['unknown'] !== undefined && dist['unknown'] <= 0) delete dist['unknown']
    return dist
  })

  // Occupation stats: 職業ごとの最終tick平均ステータス
  const occupationStats = computed(() => {
    const profiles = profilesMap.value
    if (!Object.keys(profiles).length) return []
    const f = frames.value
    if (!f.length) return []
    const lastFrame = f[f.length - 1]
    const byOcc = {}
    for (const agent of lastFrame.agents || []) {
      const profile = profiles[agent.id]
      const occ = profile?.occupation || 'unknown'
      if (!byOcc[occ]) byOcc[occ] = { agents: [], occupation: occ }
      byOcc[occ].agents.push(agent)
    }
    const keys = ['energy', 'happiness', 'stress', 'socialization', 'money']
    return Object.values(byOcc)
      .map((group) => {
        const avgs = {}
        for (const key of keys) {
          avgs[key] = group.agents.length
            ? Math.round(
                (group.agents.reduce((s, a) => s + (a.status?.[key] || 0), 0) /
                  group.agents.length) *
                  10,
              ) / 10
            : 0
        }
        return { occupation: group.occupation, count: group.agents.length, ...avgs }
      })
      .sort((a, b) => b.count - a.count)
  })

  // Communication network: nodes + edges
  const communicationNetwork = computed(() => {
    const f = frames.value
    const profiles = profilesMap.value
    const edgeMap = {}
    const nodeMessageCount = {}
    for (const frame of f) {
      for (const msg of frame.messages || []) {
        const key = [msg.from_id, msg.to_id].sort().join('::')
        edgeMap[key] = (edgeMap[key] || 0) + 1
        nodeMessageCount[msg.from_id] = (nodeMessageCount[msg.from_id] || 0) + 1
        nodeMessageCount[msg.to_id] = (nodeMessageCount[msg.to_id] || 0) + 1
      }
    }
    const nodeIds = new Set()
    if (f.length) {
      for (const agent of f[f.length - 1].agents || []) {
        nodeIds.add(agent.id)
      }
    }
    Object.keys(nodeMessageCount).forEach((id) => nodeIds.add(id))
    const nodes = Array.from(nodeIds).map((id) => ({
      id,
      name: id,
      value: nodeMessageCount[id] || 0,
      occupation: profiles[id]?.occupation || 'unknown',
    }))
    const edges = Object.entries(edgeMap).map(([key, count]) => {
      const [source, target] = key.split('::')
      return { source, target, value: count }
    })
    return { nodes, edges }
  })

  // Wealth Gini: tick毎のジニ係数
  const wealthGini = computed(() => {
    const f = frames.value
    if (!f.length) return { ticks: [], gini: [] }
    const ticks = []
    const gini = []
    for (const frame of f) {
      ticks.push(frame.tick)
      const moneys = (frame.agents || [])
        .map((a) => a.status?.money || 0)
        .sort((a, b) => a - b)
      const n = moneys.length
      if (n === 0) {
        gini.push(0)
        continue
      }
      const mean = moneys.reduce((s, v) => s + v, 0) / n
      if (mean === 0) {
        gini.push(0)
        continue
      }
      let sumDiff = 0
      for (let i = 0; i < n; i++) {
        sumDiff += (2 * (i + 1) - n - 1) * moneys[i]
      }
      gini.push(Math.round((sumDiff / (n * n * mean)) * 1000) / 1000)
    }
    return { ticks, gini }
  })

  // Agent history: 指定エージェントの全tick推移
  function agentHistory(agentId) {
    const f = frames.value
    const keys = ['energy', 'happiness', 'stress', 'socialization', 'money']
    const result = { ticks: [] }
    keys.forEach((k) => (result[k] = []))
    for (const frame of f) {
      const agent = (frame.agents || []).find((a) => a.id === agentId)
      if (!agent) continue
      result.ticks.push(frame.tick)
      for (const key of keys) {
        result[key].push(agent.status?.[key] || 0)
      }
    }
    return result
  }

  return {
    frames,
    metadata,
    profilesMap,
    summary,
    statusTimeSeries,
    actionDistribution,
    occupationStats,
    communicationNetwork,
    wealthGini,
    agentHistory,
  }
}
