// Store for managing agent map state, polling, and selection.

import { ref } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'

export const useMapStore = defineStore('map', () => {
  const agents = ref([])
  const currentTick = ref(null)
  const agentCount = ref(0)
  const mapSize = ref(300)
  const status = ref('not_running')

  const selectedAgentId = ref(null)
  const hoveredAgentId = ref(null)

  let pollingTimer = null

  async function fetchPositions() {
    try {
      const res = await axios.get('/api/simulation/map/agents')
      const data = res.data
      status.value = data.status
      currentTick.value = data.tick
      agentCount.value = data.agent_count
      agents.value = data.agents || []
    } catch {
      status.value = 'error'
      agents.value = []
      agentCount.value = 0
      currentTick.value = null
    }
  }

  function startPolling(interval = 3000) {
    stopPolling()
    fetchPositions()
    pollingTimer = setInterval(fetchPositions, interval)
  }

  function stopPolling() {
    if (pollingTimer) {
      clearInterval(pollingTimer)
      pollingTimer = null
    }
  }

  function selectAgent(id) {
    selectedAgentId.value = selectedAgentId.value === id ? null : id
  }

  function hoverAgent(id) {
    hoveredAgentId.value = id
  }

  return {
    agents,
    currentTick,
    agentCount,
    mapSize,
    status,
    selectedAgentId,
    hoveredAgentId,
    fetchPositions,
    startPolling,
    stopPolling,
    selectAgent,
    hoverAgent
  }
})
