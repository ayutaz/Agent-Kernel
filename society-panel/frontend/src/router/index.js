// Vue Router configuration with routes for Dashboard, Files, and Configs views.

import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from '../views/DashboardView.vue'
import FilesView from '../views/FilesView.vue'
import ConfigsView from '../views/ConfigsView.vue'
import MapView from '../views/MapView.vue'
import ReplayView from '../views/ReplayView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: DashboardView
    },
    {
      path: '/files',
      name: 'files',
      component: FilesView
    },
    {
      path: '/configs',
      name: 'configs',
      component: ConfigsView
    },
    {
      path: '/map',
      name: 'map',
      component: MapView
    },
    {
      path: '/replay',
      name: 'replay',
      component: ReplayView
    },
    {
      path: '/analysis',
      name: 'analysis',
      component: () => import('../views/AnalysisView.vue')
    }
  ]
})

export default router
