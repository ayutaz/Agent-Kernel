<script setup>
import { ref, onMounted, computed } from 'vue'
import { useReplayStore } from '../stores/replay'
import { useThemeStore } from '../stores/theme'
import { useAnalytics } from '../composables/useAnalytics'
import { useSurveyAnalytics } from '../composables/useSurveyAnalytics'

import SummaryCards from '../components/analysis/SummaryCards.vue'
import StatusTimeSeriesChart from '../components/analysis/StatusTimeSeriesChart.vue'
import ActionDistributionChart from '../components/analysis/ActionDistributionChart.vue'
import OccupationComparisonChart from '../components/analysis/OccupationComparisonChart.vue'
import CommunicationNetwork from '../components/analysis/CommunicationNetwork.vue'
import WealthDistributionChart from '../components/analysis/WealthDistributionChart.vue'
import AgentDetailChart from '../components/analysis/AgentDetailChart.vue'

import SurveyKpiCards from '../components/analysis/survey/SurveyKpiCards.vue'
import RmseConvergenceChart from '../components/analysis/survey/RmseConvergenceChart.vue'
import DiversityBonusChart from '../components/analysis/survey/DiversityBonusChart.vue'
import AttributeCoverageChart from '../components/analysis/survey/AttributeCoverageChart.vue'
import SpecialistDistributionChart from '../components/analysis/survey/SpecialistDistributionChart.vue'
import SurveyRegionMapChart from '../components/analysis/survey/SurveyRegionMapChart.vue'

const replayStore = useReplayStore()
const themeStore = useThemeStore()
const analytics = useAnalytics()
const surveyAnalytics = useSurveyAnalytics()

const selectedAgentId = ref(null)
const activeTab = ref('auto')

function onSelectAgent(agentId) {
  selectedAgentId.value = agentId
}

const showSurveyCharts = computed(() => {
  if (activeTab.value === 'general') return false
  if (activeTab.value === 'survey') return true
  return surveyAnalytics.isSurveyRecording.value
})

const agentIds = computed(() => {
  const frames = analytics.frames.value
  if (!frames.length) return []
  return (frames[frames.length - 1].agents || []).map(a => a.id).sort()
})

onMounted(() => {
  if (!replayStore.recordings.length) {
    replayStore.fetchRecordings()
  }
})
</script>

<template>
  <div class="analysis-view">
    <div class="page-header">
      <h1>分析ダッシュボード</h1>
      <div class="header-controls">
        <div v-if="surveyAnalytics.isSurveyRecording.value" class="tab-bar">
          <button
            class="tab-btn" :class="{ active: !showSurveyCharts }"
            @click="activeTab = 'general'"
          >一般分析</button>
          <button
            class="tab-btn" :class="{ active: showSurveyCharts }"
            @click="activeTab = 'survey'"
          >災害調査分析</button>
        </div>
        <select
          v-if="replayStore.recordings.length"
          class="recording-select"
          @change="e => e.target.value && replayStore.loadRecording(e.target.value)"
        >
          <option value="">録画を選択...</option>
          <option
            v-for="rec in replayStore.recordings"
            :key="rec.filename"
            :value="rec.filename"
            :selected="replayStore.recording && rec.filename === replayStore.recording?.metadata?.filename"
          >
            {{ rec.filename }}
          </option>
        </select>
        <p v-else class="no-recordings">録画データがありません</p>
      </div>
    </div>

    <div v-if="replayStore.loadingRecording" class="loading">読み込み中...</div>

    <template v-else-if="replayStore.recording">
      <template v-if="!showSurveyCharts">
        <SummaryCards :summary="analytics.summary.value" />

        <div class="charts-grid">
          <div class="panel-container chart-panel">
            <h3>ステータス時系列</h3>
            <StatusTimeSeriesChart :data="analytics.statusTimeSeries.value" :isDark="themeStore.isDark" />
          </div>
          <div class="panel-container chart-panel">
            <h3>アクション分布</h3>
            <ActionDistributionChart :data="analytics.actionDistribution.value" :isDark="themeStore.isDark" />
          </div>
        </div>

        <div class="charts-grid">
          <div class="panel-container chart-panel" v-if="analytics.occupationStats.value.length">
            <h3>職業別ステータス比較</h3>
            <OccupationComparisonChart :data="analytics.occupationStats.value" :isDark="themeStore.isDark" />
          </div>
          <div class="panel-container chart-panel">
            <h3>資金分布（ジニ係数推移）</h3>
            <WealthDistributionChart :data="analytics.wealthGini.value" :isDark="themeStore.isDark" />
          </div>
        </div>

        <div class="panel-container chart-panel full-width">
          <h3>コミュニケーションネットワーク</h3>
          <CommunicationNetwork
            :data="analytics.communicationNetwork.value"
            :isDark="themeStore.isDark"
            @select-agent="onSelectAgent"
          />
        </div>

        <div class="panel-container chart-panel full-width">
          <h3>エージェント詳細</h3>
          <div class="agent-select-row">
            <select class="agent-select" v-model="selectedAgentId">
              <option :value="null">エージェントを選択...</option>
              <option v-for="id in agentIds" :key="id" :value="id">{{ id }}</option>
            </select>
          </div>
          <AgentDetailChart
            v-if="selectedAgentId"
            :agentId="selectedAgentId"
            :history="analytics.agentHistory(selectedAgentId)"
            :profile="analytics.profilesMap.value[selectedAgentId]"
            :isDark="themeStore.isDark"
          />
          <div v-else class="placeholder">
            <p>ネットワーク上のノードをクリックするか、ドロップダウンからエージェントを選択してください。</p>
          </div>
        </div>
      </template>

      <template v-else>
        <SurveyKpiCards :summary="surveyAnalytics.summary.value" />

        <div class="charts-grid">
          <div class="panel-container chart-panel">
            <h3>RMSE収束曲線</h3>
            <RmseConvergenceChart :data="surveyAnalytics.rmseTimeSeries.value" :isDark="themeStore.isDark" />
          </div>
          <div class="panel-container chart-panel">
            <h3>多様性ボーナス</h3>
            <DiversityBonusChart :data="surveyAnalytics.diversityTimeSeries.value" :isDark="themeStore.isDark" />
          </div>
        </div>

        <div class="charts-grid">
          <div class="panel-container chart-panel">
            <h3>属性カバレッジ</h3>
            <AttributeCoverageChart :data="surveyAnalytics.coverageTimeSeries.value" :isDark="themeStore.isDark" />
          </div>
          <div class="panel-container chart-panel">
            <h3>専門家構成</h3>
            <SpecialistDistributionChart :data="surveyAnalytics.specialistDistribution.value" :isDark="themeStore.isDark" />
          </div>
        </div>

        <div class="panel-container chart-panel full-width">
          <h3>候補地マップ</h3>
          <SurveyRegionMapChart
            :agents="surveyAnalytics.lastFrameAgents.value"
            :regions="surveyAnalytics.regions"
            :profiles="surveyAnalytics.profilesMap.value"
            :isDark="themeStore.isDark"
          />
        </div>
      </template>
    </template>

    <div v-else class="empty-state">
      <p>録画を選択して分析を開始してください。</p>
    </div>
  </div>
</template>

<style scoped>
.analysis-view {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}
.header-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.tab-bar {
  display: flex;
  gap: 0.25rem;
  background: var(--card-bg);
  border: 1px solid var(--border-soft);
  border-radius: 8px;
  padding: 0.2rem;
}
.tab-btn {
  padding: 0.4rem 0.8rem;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: var(--text-muted);
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
}
.tab-btn:hover {
  color: var(--text-primary);
}
.tab-btn.active {
  background: var(--accent, #4f8cff);
  color: #fff;
}
.recording-select, .agent-select {
  padding: 0.5rem 1rem;
  border-radius: 8px;
  border: 1px solid var(--border-soft);
  background: var(--card-bg);
  color: var(--text-primary);
  font-size: 0.9rem;
  cursor: pointer;
}
.charts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}
.chart-panel h3 {
  margin-top: 0;
  margin-bottom: 1rem;
}
.full-width {
  width: 100%;
}
.agent-select-row {
  margin-bottom: 1rem;
}
.loading, .empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 200px;
}
.placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100px;
}
.placeholder p, .empty-state p, .no-recordings {
  color: var(--text-muted);
  font-size: 0.95rem;
}
@media (max-width: 768px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }
}
</style>
