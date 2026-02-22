// Store for managing simulation recording replay state and playback controls.

import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'

export const useReplayStore = defineStore('replay', () => {
  const recordings = ref([])
  const recording = ref(null)
  const currentFrameIndex = ref(0)
  const isPlaying = ref(false)
  const playbackSpeed = ref(1)
  const loadingList = ref(false)
  const loadingRecording = ref(false)

  let playbackTimer = null

  const currentFrame = computed(() => {
    if (!recording.value || !recording.value.frames.length) return null
    return recording.value.frames[currentFrameIndex.value] || null
  })

  const agents = computed(() => {
    return currentFrame.value ? currentFrame.value.agents : []
  })

  const currentTick = computed(() => {
    return currentFrame.value ? currentFrame.value.tick : null
  })

  const totalFrames = computed(() => {
    return recording.value ? recording.value.frames.length : 0
  })

  const mapSize = computed(() => {
    if (!recording.value) return 300
    return recording.value.metadata?.map_size || 300
  })

  const messages = computed(() => {
    return currentFrame.value ? (currentFrame.value.messages || []) : []
  })

  const agentTrails = computed(() => {
    if (!recording.value) return {}
    const trailLength = 5
    const startIdx = Math.max(0, currentFrameIndex.value - trailLength)
    const endIdx = currentFrameIndex.value + 1
    const trails = {}
    for (let i = startIdx; i < endIdx; i++) {
      const frame = recording.value.frames[i]
      if (!frame) continue
      for (const agent of frame.agents) {
        if (!trails[agent.id]) trails[agent.id] = []
        trails[agent.id].push(agent.position)
      }
    }
    return trails
  })

  async function fetchRecordings() {
    loadingList.value = true
    try {
      const res = await axios.get('/api/recordings/list')
      recordings.value = res.data
    } catch {
      recordings.value = []
    } finally {
      loadingList.value = false
    }
  }

  async function loadRecording(filename) {
    loadingRecording.value = true
    stop()
    try {
      const res = await axios.get(`/api/recordings/${filename}`)
      recording.value = res.data
      currentFrameIndex.value = 0
    } catch {
      recording.value = null
    } finally {
      loadingRecording.value = false
    }
  }

  async function deleteRecording(filename) {
    try {
      await axios.delete(`/api/recordings/${filename}`)
      recordings.value = recordings.value.filter(r => r.filename !== filename)
      if (recording.value && recordings.value.length === 0) {
        recording.value = null
      }
    } catch {
      // ignore
    }
  }

  function play() {
    if (!recording.value || totalFrames.value === 0) return
    if (currentFrameIndex.value >= totalFrames.value - 1) {
      currentFrameIndex.value = 0
    }
    isPlaying.value = true
    scheduleNext()
  }

  function pause() {
    isPlaying.value = false
    clearTimer()
  }

  function stop() {
    isPlaying.value = false
    clearTimer()
    currentFrameIndex.value = 0
  }

  function togglePlayPause() {
    if (isPlaying.value) {
      pause()
    } else {
      play()
    }
  }

  function setSpeed(speed) {
    playbackSpeed.value = speed
    if (isPlaying.value) {
      clearTimer()
      scheduleNext()
    }
  }

  function seekTo(frameIndex) {
    currentFrameIndex.value = Math.max(0, Math.min(frameIndex, totalFrames.value - 1))
  }

  function stepForward() {
    pause()
    if (currentFrameIndex.value < totalFrames.value - 1) {
      currentFrameIndex.value++
    }
  }

  function stepBackward() {
    pause()
    if (currentFrameIndex.value > 0) {
      currentFrameIndex.value--
    }
  }

  function scheduleNext() {
    clearTimer()
    if (!isPlaying.value) return
    const interval = 1000 / playbackSpeed.value
    playbackTimer = setTimeout(() => {
      if (currentFrameIndex.value < totalFrames.value - 1) {
        currentFrameIndex.value++
        scheduleNext()
      } else {
        isPlaying.value = false
      }
    }, interval)
  }

  function clearTimer() {
    if (playbackTimer) {
      clearTimeout(playbackTimer)
      playbackTimer = null
    }
  }

  return {
    recordings,
    recording,
    currentFrameIndex,
    isPlaying,
    playbackSpeed,
    loadingList,
    loadingRecording,
    currentFrame,
    agents,
    currentTick,
    totalFrames,
    mapSize,
    messages,
    agentTrails,
    fetchRecordings,
    loadRecording,
    deleteRecording,
    play,
    pause,
    stop,
    togglePlayPause,
    setSpeed,
    seekTo,
    stepForward,
    stepBackward,
  }
})
