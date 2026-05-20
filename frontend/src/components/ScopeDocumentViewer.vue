<template>
  <div class="scope-viewer">
    <!-- Streaming Progress -->
    <div v-if="discoveryStore.isStreaming" class="scope-card">
      <h3 class="text-xl font-bold mb-4 text-gray-800">Generating Scope Document</h3>
      
      <!-- Current Phase -->
      <div v-if="discoveryStore.currentPhase" class="mb-4">
        <div class="flex items-center gap-2">
          <div class="w-3 h-3 bg-blue-500 rounded-full animate-pulse"></div>
          <span class="text-sm font-medium text-gray-700">
            {{ formatPhase(discoveryStore.currentPhase) }}
          </span>
        </div>
      </div>

      <!-- Live Token Stream -->
      <div v-if="discoveryStore.currentToken" class="bg-gray-50 rounded-md p-4 font-mono text-sm text-gray-700">
        {{ discoveryStore.currentToken }}
      </div>
    </div>

    <!-- Progressive Results During Streaming -->
    <div v-if="discoveryStore.isStreaming || (!discoveryStore.isStreaming && !discoveryStore.scopeDocument)" class="space-y-6">

      <!-- Complexity Analysis -->
      <div v-if="isPhaseInProgress('classify') || isPhaseCompleted('classify')" class="scope-card">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-xl font-bold text-gray-800">Complexity Assessment</h3>
          <span v-if="isPhaseCompleted('classify')" class="text-green-500 text-sm font-medium">✓ Completed</span>
        </div>
        
        <ComplexitySkeleton v-if="isPhaseInProgress('classify')" />
        
        <div v-else-if="discoveryStore.classificationResult" class="p-4 bg-blue-50 rounded-md">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <span class="text-sm font-medium text-blue-700">Complexity Level:</span>
              <span class="ml-2 text-blue-900 font-bold capitalize">{{ discoveryStore.classificationResult.complexity }}</span>
            </div>
            <div>
              <span class="text-sm font-medium text-blue-700">Reasoning:</span>
              <span class="ml-2 text-blue-900">{{ discoveryStore.classificationResult.reasoning }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Risk Analysis -->
      <div v-if="isPhaseInProgress('analyze_risks') || isPhaseCompleted('analyze_risks')" class="scope-card">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-xl font-bold text-gray-800">Risk Analysis</h3>
          <span v-if="isPhaseCompleted('analyze_risks')" class="text-green-500 text-sm font-medium">✓ Completed</span>
        </div>
        
        <RisksSkeleton v-if="isPhaseInProgress('analyze_risks')" />
        
        <div v-else-if="discoveryStore.riskAnalysisResult" class="space-y-4">
          <div>
            <h4 class="text-lg font-semibold text-gray-800 mb-3">Identified Risks</h4>
            <ul class="space-y-2">
              <li
                v-for="(risk, index) in discoveryStore.riskAnalysisResult.risks"
                :key="index"
                class="flex items-start gap-2 p-3 bg-red-50 rounded-md"
              >
                <span class="text-red-500 mt-1">⚠</span>
                <span class="text-red-900">{{ risk }}</span>
              </li>
            </ul>
          </div>
          
          <div v-if="discoveryStore.riskAnalysisResult.mitigations && Object.keys(discoveryStore.riskAnalysisResult.mitigations).length > 0">
            <h4 class="text-lg font-semibold text-gray-800 mb-3">Risk Mitigations</h4>
            <div class="space-y-3">
              <div
                v-for="(mitigation, risk, index) in discoveryStore.riskAnalysisResult.mitigations"
                :key="index"
                class="p-3 bg-green-50 rounded-md"
              >
                <p class="font-medium text-green-900 mb-1">{{ risk }}</p>
                <p class="text-sm text-green-800">{{ mitigation }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Scope Generation -->
      <div v-if="isPhaseInProgress('generate_scope')" class="scope-card">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-xl font-bold text-gray-800">Generating Scope Document</h3>
        </div>
        
        <div class="space-y-6">
          <DeliverablesSkeleton />
          <TechStackSkeleton />
          <TimelineSkeleton />
        </div>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="discoveryStore.error" class="error-card">
      <h3 class="text-lg font-bold text-red-800 mb-2">Error</h3>
      <p class="text-red-700">{{ discoveryStore.error }}</p>
    </div>

    <!-- Final Scope Document -->
    <div v-if="discoveryStore.scopeDocument && !discoveryStore.isStreaming" class="scope-card">
      <h3 class="text-2xl font-bold mb-6 text-gray-800">Project Scope Document</h3>
      
      <!-- Complexity Analysis -->
      <div class="mb-6 p-4 bg-blue-50 rounded-md">
        <h4 class="text-lg font-semibold text-blue-900 mb-2">Complexity Assessment</h4>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <span class="text-sm font-medium text-blue-700">Complexity Level:</span>
            <span class="ml-2 text-blue-900 font-bold capitalize">{{ discoveryStore.scopeDocument.complexity }}</span>
          </div>
          <div>
            <span class="text-sm font-medium text-blue-700">Reasoning:</span>
            <span class="ml-2 text-blue-900">{{ discoveryStore.scopeDocument.complexity_reason }}</span>
          </div>
        </div>
      </div>

      <!-- Cost & Timeline Estimates -->
      <div v-if="hasEstimates" class="mb-6 p-4 bg-green-50 rounded-md">
        <h4 class="text-lg font-semibold text-green-900 mb-2">Estimates</h4>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <span class="text-sm font-medium text-green-700">Cost Range:</span>
            <span class="ml-2 text-green-900 font-bold">
              ${{ discoveryStore.scopeDocument.estimated_cost_min?.toLocaleString() }} - ${{ discoveryStore.scopeDocument.estimated_cost_max?.toLocaleString() }}
            </span>
          </div>
          <div>
            <span class="text-sm font-medium text-green-700">Timeline:</span>
            <span class="ml-2 text-green-900 font-bold">
              {{ discoveryStore.scopeDocument.estimated_weeks_min }} - {{ discoveryStore.scopeDocument.estimated_weeks_max }} weeks
            </span>
          </div>
        </div>
      </div>

      <!-- Deliverables -->
      <div class="mb-6">
        <h4 class="text-lg font-semibold text-gray-800 mb-3">Deliverables</h4>
        <ul class="space-y-2">
          <li
            v-for="(deliverable, index) in discoveryStore.scopeDocument.deliverables"
            :key="index"
            class="flex items-start gap-2"
          >
            <span class="text-blue-500 mt-1">•</span>
            <span class="text-gray-700">{{ deliverable }}</span>
          </li>
        </ul>
      </div>

      <!-- Tech Stack -->
      <div class="mb-6">
        <h4 class="text-lg font-semibold text-gray-800 mb-3">Recommended Tech Stack</h4>
        <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
          <div
            v-for="(tech, category) in discoveryStore.scopeDocument.tech_stack"
            :key="category"
            class="p-3 bg-gray-50 rounded-md"
          >
            <span class="text-xs font-medium text-gray-500 uppercase">{{ category }}</span>
            <p class="text-sm font-semibold text-gray-800 mt-1">{{ tech }}</p>
          </div>
        </div>
      </div>

      <!-- Timeline Breakdown -->
      <div class="mb-6">
        <h4 class="text-lg font-semibold text-gray-800 mb-3">Timeline Breakdown</h4>
        <div class="space-y-3">
          <div
            v-for="(item, index) in discoveryStore.scopeDocument.timeline_breakdown"
            :key="index"
            class="p-3 border border-gray-200 rounded-md"
          >
            <div class="flex justify-between items-start">
              <span class="font-medium text-gray-800">{{ (item as Record<string, unknown>).phase || (item as Record<string, unknown>).milestone || 'Phase ' + (index + 1) }}</span>
              <span class="text-sm text-gray-500">{{ (item as Record<string, unknown>).duration || (item as Record<string, unknown>).weeks || '' }}</span>
            </div>
            <p v-if="(item as Record<string, unknown>).description || (item as Record<string, unknown>).tasks" class="text-sm text-gray-600 mt-1">
              {{ (item as Record<string, unknown>).description || (Array.isArray((item as Record<string, unknown>).tasks) ? ((item as Record<string, unknown>).tasks as string[]).join(', ') : String((item as Record<string, unknown>).tasks)) }}
            </p>
          </div>
        </div>
      </div>

      <!-- Risks -->
      <div class="mb-6">
        <h4 class="text-lg font-semibold text-gray-800 mb-3">Potential Risks</h4>
        <ul class="space-y-2">
          <li
            v-for="(risk, index) in discoveryStore.scopeDocument.risks"
            :key="index"
            class="flex items-start gap-2 p-3 bg-red-50 rounded-md"
          >
            <span class="text-red-500 mt-1">⚠</span>
            <span class="text-red-900">{{ risk }}</span>
          </li>
        </ul>
      </div>

      <!-- Risk Mitigations -->
      <div v-if="discoveryStore.scopeDocument.mitigations && Object.keys(discoveryStore.scopeDocument.mitigations).length > 0" class="mb-6">
        <h4 class="text-lg font-semibold text-gray-800 mb-3">Risk Mitigations</h4>
        <div class="space-y-3">
          <div
            v-for="(mitigation, risk, index) in discoveryStore.scopeDocument.mitigations"
            :key="index"
            class="p-3 bg-green-50 rounded-md"
          >
            <p class="font-medium text-green-900 mb-1">{{ risk }}</p>
            <p class="text-sm text-green-800">{{ mitigation }}</p>
          </div>
        </div>
      </div>

      <!-- Out of Scope -->
      <div class="mb-6">
        <h4 class="text-lg font-semibold text-gray-800 mb-3">Out of Scope</h4>
        <ul class="space-y-2">
          <li
            v-for="(item, index) in discoveryStore.scopeDocument.out_of_scope"
            :key="index"
            class="flex items-start gap-2 p-3 bg-gray-100 rounded-md"
          >
            <span class="text-gray-500 mt-1">✗</span>
            <span class="text-gray-700">{{ item }}</span>
          </li>
        </ul>
      </div>

      <!-- Metadata -->
      <div class="text-xs text-gray-500 pt-4 border-t">
        <p>Generated at: {{ new Date(discoveryStore.scopeDocument.created_at as string | number | Date).toLocaleString() }}</p>
        <p>Request ID: {{ discoveryStore.scopeDocument.request_id }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useDiscoveryStore } from '@/stores/discovery'
import ComplexitySkeleton from '@/components/skeletons/ComplexitySkeleton.vue'
import RisksSkeleton from '@/components/skeletons/RisksSkeleton.vue'
import DeliverablesSkeleton from '@/components/skeletons/DeliverablesSkeleton.vue'
import TimelineSkeleton from '@/components/skeletons/TimelineSkeleton.vue'
import TechStackSkeleton from '@/components/skeletons/TechStackSkeleton.vue'

const discoveryStore = useDiscoveryStore()

const hasEstimates = computed(() => {
  return (
    discoveryStore.scopeDocument &&
    (discoveryStore.scopeDocument.estimated_cost_min ||
     discoveryStore.scopeDocument.estimated_cost_max ||
     discoveryStore.scopeDocument.estimated_weeks_min ||
     discoveryStore.scopeDocument.estimated_weeks_max)
  )
})

// Check if a phase is currently being processed
const isPhaseInProgress = (phase: string) => {
  return discoveryStore.currentPhase === phase && discoveryStore.isStreaming
}

// Check if a phase has completed
const isPhaseCompleted = (phase: string) => {
  return discoveryStore.completedPhases.has(phase) || 
         (discoveryStore.scopeDocument && !discoveryStore.isStreaming)
}

function formatPhase(phase: string) {
  switch (phase) {
    case 'classify':
      return 'Classifying project complexity...'
    case 'analyze_risks':
      return 'Analyzing potential risks...'
    case 'generate_scope':
      return 'Generating scope document...'
    default:
      return phase
  }
}
</script>

<style scoped>
.scope-viewer {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
}

.scope-card {
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: var(--space-6);
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow:
    0 8px 32px rgba(0, 0, 0, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);
}

.error-card {
  background: rgba(255, 107, 107, 0.1);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: var(--space-6);
  border: 1px solid rgba(255, 107, 107, 0.2);
}

/* Override all the tailwind text colors for dark theme */
:deep(h3), :deep(.text-xl), :deep(.text-2xl) {
  color: #ffffff !important;
}

:deep(p), :deep(span), :deep(li) {
  color: rgba(255, 255, 255, 0.8) !important;
}

:deep(.text-gray-500), :deep(.text-gray-600), :deep(.text-gray-700), :deep(.text-gray-800) {
  color: rgba(255, 255, 255, 0.6) !important;
}

:deep(.text-blue-700), :deep(.text-blue-900) {
  color: rgba(255, 255, 255, 0.9) !important;
}

:deep(.text-green-700), :deep(.text-green-800), :deep(.text-green-900) {
  color: rgba(255, 255, 255, 0.9) !important;
}

:deep(.text-red-900) {
  color: rgba(255, 200, 200, 0.9) !important;
}

:deep(.bg-blue-50), :deep(.bg-green-50), :deep(.bg-red-50), :deep(.bg-gray-50), :deep(.bg-gray-100) {
  background: rgba(0, 0, 0, 0.2) !important;
  border-radius: 12px;
}

:deep(.border), :deep(.border-gray-200) {
  border-color: rgba(255, 255, 255, 0.1) !important;
}

:deep(.bg-white) {
  background: transparent !important;
}

:deep(.shadow-lg) {
  box-shadow: none !important;
}
</style>
