<template>
  <div class="scope-viewer">
    <!-- Streaming Document UI with Phased Skeleton Loading -->
    <div v-if="discoveryStore.isStreaming || (!discoveryStore.isStreaming && !discoveryStore.scopeDocument)" class="document-mock">
      <!-- Document Header -->
      <div class="document-header">
        <div class="document-title">
          <div class="doc-icon-ring"></div>
          <span class="doc-title-text">Generating Scope Document</span>
        </div>
        <div class="progress-indicator">
          <span class="progress-text">Step {{ currentStepNumber }} of {{ totalPhases }}</span>
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: `${(currentStepNumber / totalPhases) * 100}%` }"></div>
          </div>
        </div>
      </div>

      <!-- Document Sections with Phased Skeleton Loading -->
      <div class="document-sections">
        <!-- Section 1: Firm History Research -->
        <div class="doc-section" :class="{ active: isPhaseInProgress('search_firm_history'), completed: !discoveryStore.isStreaming && isPhaseCompleted('search_firm_history') }">
          <div class="section-header">
            <div class="section-icon research">
              <div class="icon-history"></div>
            </div>
            <div class="section-info">
              <span class="section-title">Firm History Research</span>
              <span class="section-status">
                <span v-if="isPhaseInProgress('search_firm_history')" class="status-badge processing">
                  <span class="status-dot"></span>
                  Searching past projects...
                </span>
                <span v-else-if="isPhaseCompleted('search_firm_history')" class="status-badge completed">
                  <span v-if="((discoveryStore.firmHistoryResult as any)?.total_matches || 0) > 0">
                    ✓ {{ (discoveryStore.firmHistoryResult as any)?.total_matches }} similar projects found
                  </span>
                  <span v-else>✓ No direct matches found</span>
                </span>
                <span v-else class="status-badge pending">Waiting...</span>
              </span>
            </div>
          </div>
          <div v-if="isPhaseCompleted('search_firm_history') && discoveryStore.firmHistoryResult" class="section-content completed-content research-content">
            <p class="research-summary">{{ (discoveryStore.firmHistoryResult as any).relevant_experience_summary }}</p>
            <p v-if="(discoveryStore.firmHistoryResult as any).recommended_approach" class="research-recommendation">
              <strong>Recommendation:</strong> {{ (discoveryStore.firmHistoryResult as any).recommended_approach }}
            </p>
            <div v-if="(discoveryStore.firmHistoryResult as any).similar_projects?.length" class="similar-projects">
              <span class="projects-label">Similar Projects:</span>
              <div v-for="(proj, i) in (discoveryStore.firmHistoryResult as any).similar_projects.slice(0, 3)" :key="i" class="project-chip">
                {{ proj.project_name }} ({{ Math.round(proj.relevance_score * 100) }}% match)
              </div>
            </div>
          </div>
        </div>

        <!-- Section 2: Resource Availability -->
        <div class="doc-section" :class="{ active: isPhaseInProgress('check_resources'), completed: !discoveryStore.isStreaming && isPhaseCompleted('check_resources') }">
          <div class="section-header">
            <div class="section-icon resources">
              <div class="icon-team"></div>
            </div>
            <div class="section-info">
              <span class="section-title">Resource Availability</span>
              <span class="section-status">
                <span v-if="isPhaseInProgress('check_resources')" class="status-badge processing">
                  <span class="status-dot"></span>
                  Checking team capacity...
                </span>
                <span v-else-if="isPhaseCompleted('check_resources')" class="status-badge completed">
                  <span v-if="discoveryStore.resourcesResult">
                    ✓ {{ (discoveryStore.resourcesResult as any).experts_available_count || 0 }} experts, {{ (discoveryStore.resourcesResult as any).reallocatable_count || 0 }} reallocatable
                  </span>
                  <span v-else>✓ Checked</span>
                </span>
                <span v-else class="status-badge pending">Waiting...</span>
              </span>
            </div>
          </div>
          <div v-if="isPhaseCompleted('check_resources') && discoveryStore.resourcesResult" class="section-content completed-content research-content">
            <p class="research-summary">{{ (discoveryStore.resourcesResult as any).resource_recommendation }}</p>
            <p v-if="(discoveryStore.resourcesResult as any).potential_team_composition" class="team-composition">
              <strong>Team Suggestion:</strong> {{ (discoveryStore.resourcesResult as any).potential_team_composition }}
            </p>
            <div v-if="(discoveryStore.resourcesResult as any).skill_coverage_analysis" class="skill-coverage">
              <span class="coverage-label">Skill Coverage:</span>
              <div v-for="(count, skill) in (discoveryStore.resourcesResult as any).skill_coverage_analysis" :key="skill" class="skill-chip">
                {{ skill }}: {{ count }}
              </div>
            </div>
          </div>
        </div>

        <!-- Section 3: Market Research -->
        <div class="doc-section" :class="{ active: isPhaseInProgress('market_research'), completed: !discoveryStore.isStreaming && isPhaseCompleted('market_research') }">
          <div class="section-header">
            <div class="section-icon market">
              <div class="icon-globe"></div>
            </div>
            <div class="section-info">
              <span class="section-title">Market Research</span>
              <span class="section-status">
                <span v-if="isPhaseInProgress('market_research')" class="status-badge processing">
                  <span class="status-dot"></span>
                  Analyzing market data...
                </span>
                <span v-else-if="isPhaseCompleted('market_research')" class="status-badge completed">
                  <span v-if="(discoveryStore.marketResearchResult as any)?.typical_budget_range">✓ Market data gathered</span>
                  <span v-else>✓ Checked</span>
                </span>
                <span v-else class="status-badge pending">Waiting...</span>
              </span>
            </div>
          </div>
          <div v-if="isPhaseCompleted('market_research') && discoveryStore.marketResearchResult" class="section-content completed-content research-content">
            <p class="research-summary">{{ (discoveryStore.marketResearchResult as any).market_trends }}</p>
            <div class="market-stats">
              <div v-if="(discoveryStore.marketResearchResult as any).typical_budget_range" class="market-stat">
                <span class="stat-label">Typical Budget:</span>
                <span class="stat-value">{{ (discoveryStore.marketResearchResult as any).typical_budget_range }}</span>
              </div>
              <div v-if="(discoveryStore.marketResearchResult as any).typical_timeline" class="market-stat">
                <span class="stat-label">Typical Timeline:</span>
                <span class="stat-value">{{ (discoveryStore.marketResearchResult as any).typical_timeline }}</span>
              </div>
            </div>
            <div v-if="(discoveryStore.marketResearchResult as any).technology_recommendations?.length" class="tech-recommendations">
              <span class="tech-label">Market Tech Trends:</span>
              <div v-for="(tech, i) in (discoveryStore.marketResearchResult as any).technology_recommendations.slice(0, 4)" :key="i" class="tech-chip">
                {{ tech }}
              </div>
            </div>
          </div>
        </div>

        <!-- Section 4: Complexity Analysis -->
        <div class="doc-section" :class="{ active: isPhaseInProgress('classify'), completed: !discoveryStore.isStreaming && isPhaseCompleted('classify') }">
          <div class="section-header">
            <div class="section-icon complexity">
              <div class="icon-bar"></div>
              <div class="icon-bar short"></div>
            </div>
            <div class="section-info">
              <span class="section-title">Complexity Analysis</span>
              <span class="section-status">
                <span v-if="isPhaseInProgress('classify')" class="status-badge processing">
                  <span class="status-dot"></span>
                  Processing...
                </span>
                <span v-else-if="discoveryStore.isStreaming" class="status-badge pending">Waiting...</span>
                <span v-else-if="isPhaseCompleted('classify')" class="status-badge completed">✓ Completed</span>
                <span v-else class="status-badge pending">Waiting...</span>
              </span>
            </div>
          </div>
          <div v-if="isPhaseInProgress('classify')" class="section-content">
            <ComplexitySkeleton />
          </div>
          <div v-else-if="isPhaseCompleted('classify') && discoveryStore.classificationResult" class="section-content completed-content">
            <div class="result-grid">
              <div class="result-item">
                <span class="result-label">Complexity:</span>
                <span class="result-value capitalize">{{ discoveryStore.classificationResult.complexity }}</span>
              </div>
              <div class="result-item">
                <span class="result-label">Reasoning:</span>
                <span class="result-value">{{ discoveryStore.classificationResult.reasoning }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Section 5: Risk Analysis -->
        <div class="doc-section" :class="{ active: isPhaseInProgress('analyze_risks'), completed: !discoveryStore.isStreaming && isPhaseCompleted('analyze_risks') }">
          <div class="section-header">
            <div class="section-icon risks">
              <div class="icon-triangle"></div>
            </div>
            <div class="section-info">
              <span class="section-title">Risk Analysis</span>
              <span class="section-status">
                <span v-if="isPhaseInProgress('analyze_risks')" class="status-badge processing">
                  <span class="status-dot"></span>
                  Processing...
                </span>
                <span v-else-if="discoveryStore.isStreaming" class="status-badge pending">Waiting...</span>
                <span v-else-if="isPhaseCompleted('analyze_risks')" class="status-badge completed">✓ Completed</span>
                <span v-else class="status-badge pending">Waiting...</span>
              </span>
            </div>
          </div>
          <div v-if="isPhaseInProgress('analyze_risks')" class="section-content">
            <RisksSkeleton />
          </div>
          <div v-else-if="isPhaseCompleted('analyze_risks') && discoveryStore.riskAnalysisResult?.risks" class="section-content completed-content risks-content">
            <div v-if="Array.isArray(discoveryStore.riskAnalysisResult.risks) && discoveryStore.riskAnalysisResult.risks.length > 0" class="risks-list">
              <div v-for="(risk, i) in discoveryStore.riskAnalysisResult.risks.slice(0, 3)" :key="i" class="risk-item">
                <span class="risk-marker small">!</span>
                <span class="risk-text">{{ risk }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Section 6: Scope Generation -->
        <div class="doc-section" :class="{ active: isPhaseInProgress('generate_scope'), completed: !discoveryStore.isStreaming && isPhaseCompleted('generate_scope') }">
          <div class="section-header">
            <div class="section-icon scope">
              <div class="icon-lines"></div>
              <div class="icon-lines short"></div>
              <div class="icon-lines"></div>
            </div>
            <div class="section-info">
              <span class="section-title">Scope Generation</span>
              <span class="section-status">
                <span v-if="isPhaseInProgress('generate_scope')" class="status-badge processing">
                  <span class="status-dot"></span>
                  Processing...
                </span>
                <span v-else-if="discoveryStore.isStreaming" class="status-badge pending">Waiting...</span>
                <span v-else-if="isPhaseCompleted('generate_scope')" class="status-badge completed">✓ Completed</span>
                <span v-else class="status-badge pending">Waiting...</span>
              </span>
            </div>
          </div>
          <div v-if="isPhaseInProgress('generate_scope') || discoveryStore.isStreaming" class="section-content scope-skeletons">
            <DeliverablesSkeleton />
            <TechStackSkeleton />
            <TimelineSkeleton />
          </div>
        </div>
      </div>

      <!-- Current Phase Indicator -->
      <div v-if="discoveryStore.currentPhase" class="phase-indicator">
        <div class="phase-ring"></div>
        <span class="phase-text">{{ formatPhase(discoveryStore.currentPhase) }}</span>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="discoveryStore.error" class="error-card">
      <h3 class="text-lg font-bold text-red-800 mb-2">Error</h3>
      <p class="text-red-700">{{ discoveryStore.error }}</p>
    </div>

    <!-- Final Scope Document -->
    <div v-if="discoveryStore.scopeDocument && !discoveryStore.isStreaming" class="document-mock">
      <!-- Document Header -->
      <div class="document-header">
        <div class="document-title">
          <div class="doc-icon-ring"></div>
          <span class="doc-title-text">Project Scope Document</span>
        </div>
        <div class="progress-indicator">
          <span class="progress-text complete">All sections complete</span>
          <div class="progress-bar">
            <div class="progress-fill" style="width: 100%"></div>
          </div>
        </div>
      </div>

      <!-- Document Sections -->
      <div class="document-sections">
        <!-- Section 1: Complexity -->
        <div class="doc-section completed">
          <div class="section-header">
            <div class="section-icon complexity">
              <div class="icon-bar"></div>
              <div class="icon-bar short"></div>
            </div>
            <div class="section-info">
              <span class="section-title">Complexity Assessment</span>
              <span class="section-status">
                <span class="status-badge completed">✓ Completed</span>
              </span>
            </div>
          </div>
          <div class="section-content completed-content">
            <div class="result-grid">
              <div class="result-item">
                <span class="result-label">Complexity Level:</span>
                <span class="result-value capitalize">{{ discoveryStore.scopeDocument.complexity }}</span>
              </div>
              <div class="result-item full-width">
                <span class="result-label">Reasoning:</span>
                <span class="result-value">{{ discoveryStore.scopeDocument.complexity_reason }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Section 2: Estimates -->
        <div v-if="hasEstimates" class="doc-section completed">
          <div class="section-header">
            <div class="section-icon estimates">
              <div class="icon-pie"></div>
            </div>
            <div class="section-info">
              <span class="section-title">Estimates</span>
              <span class="section-status">
                <span class="status-badge completed">✓ Completed</span>
              </span>
            </div>
          </div>
          <div class="section-content completed-content">
            <div class="result-grid">
              <div class="result-item">
                <span class="result-label">Cost Range:</span>
                <span class="result-value">
                  ${{ discoveryStore.scopeDocument.estimated_cost_min?.toLocaleString() }} - ${{ discoveryStore.scopeDocument.estimated_cost_max?.toLocaleString() }}
                </span>
              </div>
              <div class="result-item">
                <span class="result-label">Timeline:</span>
                <span class="result-value">
                  {{ discoveryStore.scopeDocument.estimated_weeks_min }} - {{ discoveryStore.scopeDocument.estimated_weeks_max }} weeks
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Section 3: Deliverables -->
        <div class="doc-section completed">
          <div class="section-header">
            <div class="section-icon deliverables">
              <div class="icon-check"></div>
            </div>
            <div class="section-info">
              <span class="section-title">Deliverables</span>
              <span class="section-status">
                <span class="status-badge completed">✓ Completed</span>
              </span>
            </div>
          </div>
          <div class="section-content completed-content">
            <ul class="deliverables-list">
              <li v-for="(deliverable, index) in discoveryStore.scopeDocument.deliverables" :key="index" class="deliverable-item">
                <span class="bullet"></span>
                <span class="deliverable-text">{{ deliverable }}</span>
              </li>
            </ul>
          </div>
        </div>

        <!-- Section 4: Tech Stack -->
        <div class="doc-section completed">
          <div class="section-header">
            <div class="section-icon tech">
              <div class="icon-grid"></div>
            </div>
            <div class="section-info">
              <span class="section-title">Recommended Tech Stack</span>
              <span class="section-status">
                <span class="status-badge completed">✓ Completed</span>
              </span>
            </div>
          </div>
          <div class="section-content completed-content">
            <div class="tech-grid">
              <div v-for="(tech, category) in discoveryStore.scopeDocument.tech_stack" :key="category" class="tech-cell">
                <span class="tech-category">{{ category }}</span>
                <span class="tech-value">{{ tech }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Section 5: Timeline -->
        <div class="doc-section completed">
          <div class="section-header">
            <div class="section-icon timeline">
              <div class="icon-clock"></div>
            </div>
            <div class="section-info">
              <span class="section-title">Timeline Breakdown</span>
              <span class="section-status">
                <span class="status-badge completed">✓ Completed</span>
              </span>
            </div>
          </div>
          <div class="section-content completed-content">
            <div class="timeline-list">
              <div v-for="(item, index) in discoveryStore.scopeDocument.timeline_breakdown" :key="index" class="timeline-item">
                <div class="timeline-marker"></div>
                <div class="timeline-content">
                  <div class="timeline-header">
                    <span class="timeline-phase">{{ (item as Record<string, unknown>).phase || (item as Record<string, unknown>).milestone || 'Phase ' + (index + 1) }}</span>
                    <span class="timeline-duration">{{ (item as Record<string, unknown>).duration || (item as Record<string, unknown>).weeks || '' }}</span>
                  </div>
                  <p v-if="(item as Record<string, unknown>).description || (item as Record<string, unknown>).tasks" class="timeline-desc">
                    {{ (item as Record<string, unknown>).description || (Array.isArray((item as Record<string, unknown>).tasks) ? ((item as Record<string, unknown>).tasks as string[]).join(', ') : String((item as Record<string, unknown>).tasks)) }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Section 6: Risks -->
        <div class="doc-section completed">
          <div class="section-header">
            <div class="section-icon risks">
              <div class="icon-triangle"></div>
            </div>
            <div class="section-info">
              <span class="section-title">Potential Risks</span>
              <span class="section-status">
                <span class="status-badge completed">✓ Completed</span>
              </span>
            </div>
          </div>
          <div class="section-content completed-content">
            <div class="risks-list">
              <div v-for="(risk, index) in discoveryStore.scopeDocument.risks" :key="index" class="risk-item">
                <span class="risk-marker">!</span>
                <span class="risk-text">{{ risk }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Section 7: Risk Mitigations -->
        <div v-if="discoveryStore.scopeDocument.mitigations && Object.keys(discoveryStore.scopeDocument.mitigations).length > 0" class="doc-section completed">
          <div class="section-header">
            <div class="section-icon mitigations">
              <div class="icon-shield"></div>
            </div>
            <div class="section-info">
              <span class="section-title">Risk Mitigations</span>
              <span class="section-status">
                <span class="status-badge completed">✓ Completed</span>
              </span>
            </div>
          </div>
          <div class="section-content completed-content">
            <div class="mitigation-list">
              <div v-for="(mitigation, risk, index) in discoveryStore.scopeDocument.mitigations" :key="index" class="mitigation-item">
                <span class="mitigation-risk">{{ risk }}</span>
                <span class="mitigation-text">{{ mitigation }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Section 8: Out of Scope -->
        <div class="doc-section completed">
          <div class="section-header">
            <div class="section-icon outofscope">
              <div class="icon-cross"></div>
            </div>
            <div class="section-info">
              <span class="section-title">Out of Scope</span>
              <span class="section-status">
                <span class="status-badge completed">✓ Completed</span>
              </span>
            </div>
          </div>
          <div class="section-content completed-content">
            <div class="outofscope-list">
              <div v-for="(item, index) in discoveryStore.scopeDocument.out_of_scope" :key="index" class="outofscope-item">
                <span class="outofscope-marker">×</span>
                <span class="outofscope-text">{{ item }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Section 9: Firm History Research -->
        <div v-if="discoveryStore.firmHistoryResult" class="doc-section completed">
          <div class="section-header">
            <div class="section-icon research">
              <div class="icon-history"></div>
            </div>
            <div class="section-info">
              <span class="section-title">Firm History Research</span>
              <span class="section-status">
                <span class="status-badge completed">
                  <span v-if="((discoveryStore.firmHistoryResult as any)?.total_matches || 0) > 0">
                    ✓ {{ (discoveryStore.firmHistoryResult as any)?.total_matches }} similar projects found
                  </span>
                  <span v-else>✓ No direct matches found</span>
                </span>
              </span>
            </div>
          </div>
          <div class="section-content completed-content research-content">
            <p class="research-summary">{{ (discoveryStore.firmHistoryResult as any).relevant_experience_summary }}</p>
            <p v-if="(discoveryStore.firmHistoryResult as any).recommended_approach" class="research-recommendation">
              <strong>Recommendation:</strong> {{ (discoveryStore.firmHistoryResult as any).recommended_approach }}
            </p>
            <div v-if="(discoveryStore.firmHistoryResult as any).similar_projects?.length" class="similar-projects">
              <span class="projects-label">Similar Projects:</span>
              <div v-for="(proj, i) in (discoveryStore.firmHistoryResult as any).similar_projects.slice(0, 3)" :key="i" class="project-chip">
                {{ proj.project_name }} ({{ Math.round(proj.relevance_score * 100) }}% match)
              </div>
            </div>
          </div>
        </div>

        <!-- Section 10: Resource Availability -->
        <div v-if="discoveryStore.resourcesResult" class="doc-section completed">
          <div class="section-header">
            <div class="section-icon resources">
              <div class="icon-team"></div>
            </div>
            <div class="section-info">
              <span class="section-title">Resource Availability</span>
              <span class="section-status">
                <span class="status-badge completed">
                  ✓ {{ (discoveryStore.resourcesResult as any).experts_available_count || 0 }} experts, {{ (discoveryStore.resourcesResult as any).reallocatable_count || 0 }} reallocatable
                </span>
              </span>
            </div>
          </div>
          <div class="section-content completed-content research-content">
            <p class="research-summary">{{ (discoveryStore.resourcesResult as any).resource_recommendation }}</p>
            <p v-if="(discoveryStore.resourcesResult as any).potential_team_composition" class="team-composition">
              <strong>Team Suggestion:</strong> {{ (discoveryStore.resourcesResult as any).potential_team_composition }}
            </p>
            <div v-if="(discoveryStore.resourcesResult as any).skill_coverage_analysis" class="skill-coverage">
              <span class="coverage-label">Skill Coverage:</span>
              <div v-for="(count, skill) in (discoveryStore.resourcesResult as any).skill_coverage_analysis" :key="skill" class="skill-chip">
                {{ skill }}: {{ count }}
              </div>
            </div>
          </div>
        </div>

        <!-- Section 11: Market Research -->
        <div v-if="discoveryStore.marketResearchResult" class="doc-section completed">
          <div class="section-header">
            <div class="section-icon market">
              <div class="icon-globe"></div>
            </div>
            <div class="section-info">
              <span class="section-title">Market Research</span>
              <span class="section-status">
                <span class="status-badge completed">✓ Market data gathered</span>
              </span>
            </div>
          </div>
          <div class="section-content completed-content research-content">
            <p class="research-summary">{{ (discoveryStore.marketResearchResult as any).market_trends }}</p>
            <div class="market-stats">
              <div v-if="(discoveryStore.marketResearchResult as any).typical_budget_range" class="market-stat">
                <span class="stat-label">Typical Budget:</span>
                <span class="stat-value">{{ (discoveryStore.marketResearchResult as any).typical_budget_range }}</span>
              </div>
              <div v-if="(discoveryStore.marketResearchResult as any).typical_timeline" class="market-stat">
                <span class="stat-label">Typical Timeline:</span>
                <span class="stat-value">{{ (discoveryStore.marketResearchResult as any).typical_timeline }}</span>
              </div>
            </div>
            <div v-if="(discoveryStore.marketResearchResult as any).technology_recommendations?.length" class="tech-recommendations">
              <span class="tech-label">Market Tech Trends:</span>
              <div v-for="(tech, i) in (discoveryStore.marketResearchResult as any).technology_recommendations.slice(0, 4)" :key="i" class="tech-chip">
                {{ tech }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Metadata Footer -->
      <div class="document-footer">
        <p class="meta-text">Generated at: {{ new Date(discoveryStore.scopeDocument.created_at as string | number | Date).toLocaleString() }}</p>
        <p class="meta-text">Request ID: {{ discoveryStore.scopeDocument.request_id }}</p>
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

const totalPhases = 6

const currentStepNumber = computed(() => {
  // Step numbers match backend execution order
  if (discoveryStore.isStreaming) {
    if (discoveryStore.currentPhase === 'search_firm_history') return 1
    if (discoveryStore.currentPhase === 'check_resources') return 2
    if (discoveryStore.currentPhase === 'market_research') return 3
    if (discoveryStore.currentPhase === 'classify') return 4
    if (discoveryStore.currentPhase === 'analyze_risks') return 5
    if (discoveryStore.currentPhase === 'generate_scope') return 6
    return 1
  }
  return 6
})

// Check if a phase is currently being processed
const isPhaseInProgress = (phase: string) => {
  return discoveryStore.currentPhase === phase && discoveryStore.isStreaming
}

// Check if a phase has completed
const isPhaseCompleted = (phase: string) => {
  // During streaming, only show as completed if explicitly in completedPhases
  // and NOT currently being processed
  if (discoveryStore.isStreaming) {
    return discoveryStore.completedPhases.has(phase) && 
           discoveryStore.currentPhase !== phase
  }
  // When not streaming, check completedPhases or if we have final document
  return discoveryStore.completedPhases.has(phase) || 
         (discoveryStore.scopeDocument && !discoveryStore.isStreaming)
}

function formatPhase(phase: string) {
  switch (phase) {
    case 'search_firm_history':
      return 'Searching firm history...'
    case 'check_resources':
      return 'Checking resource availability...'
    case 'market_research':
      return 'Researching market data...'
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

/* Document Mock UI - Grid with Scanning Lens */
.document-mock {
  position: relative;
  width: 100%;
  min-height: 600px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.02) 0%, rgba(255, 255, 255, 0.01) 100%),
    linear-gradient(rgba(255, 255, 255, 0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.04) 1px, transparent 1px);
  background-size: 100% 100%, 24px 24px, 24px 24px;
  border-radius: 24px;
  padding: var(--space-8);
  border: 1px solid rgba(255, 255, 255, 0.1);
  overflow: hidden;
}

/* Document Header */
.document-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-8);
  padding-bottom: var(--space-5);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.document-title {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.doc-icon-ring {
  width: 32px;
  height: 32px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  position: relative;
}

.doc-icon-ring::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 12px;
  height: 12px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 50%;
}

.progress-text.complete {
  color: rgba(100, 255, 100, 0.8);
}

.doc-title-text {
  font-size: 20px;
  font-weight: 700;
  color: #ffffff;
  letter-spacing: -0.02em;
}

.progress-indicator {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: var(--space-2);
}

.progress-text {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  font-weight: 500;
}

.progress-bar {
  width: 120px;
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, rgba(255, 255, 255, 0.6), rgba(255, 255, 255, 0.9));
  border-radius: 2px;
  transition: width 0.5s ease;
}

/* Document Sections */
.document-sections {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.doc-section {
  background: rgba(255, 255, 255, 0.02);
  border-radius: 16px;
  padding: var(--space-5);
  border: 1px solid rgba(255, 255, 255, 0.05);
  transition: all 0.3s ease;
}

.doc-section.active {
  background: rgba(255, 255, 255, 0.04);
  border-color: rgba(255, 255, 255, 0.12);
  box-shadow: 0 0 20px rgba(255, 255, 255, 0.05);
}

.doc-section.completed {
  background: rgba(255, 255, 255, 0.03);
  border-color: rgba(100, 255, 100, 0.15);
}

.section-header {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  margin-bottom: var(--space-4);
}

.section-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.section-icon.complexity {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.15);
  flex-direction: column;
  gap: 4px;
}

.icon-bar {
  width: 20px;
  height: 3px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 2px;
}

.icon-bar.short {
  width: 12px;
}

.section-icon.risks {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.15);
}

.icon-triangle {
  width: 0;
  height: 0;
  border-left: 8px solid transparent;
  border-right: 8px solid transparent;
  border-bottom: 14px solid rgba(255, 255, 255, 0.9);
}

.section-icon.scope {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.15);
  flex-direction: column;
  gap: 3px;
  align-items: flex-start;
  padding-left: 10px;
}

.icon-lines {
  width: 18px;
  height: 2px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 1px;
}

.icon-lines.short {
  width: 12px;
}

/* Additional section icons for final document */
.section-icon.estimates {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.15);
}

.icon-pie {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.9);
  border-radius: 50%;
  border-right-color: transparent;
  transform: rotate(-45deg);
}

.section-icon.deliverables {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.15);
}

.icon-check {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.9);
  border-radius: 3px;
  position: relative;
}

.icon-check::after {
  content: '';
  position: absolute;
  top: 2px;
  left: 5px;
  width: 4px;
  height: 8px;
  border: solid rgba(255, 255, 255, 0.9);
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.section-icon.tech {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.15);
}

.icon-grid {
  width: 16px;
  height: 16px;
  background:
    linear-gradient(rgba(255, 255, 255, 0.9) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.9) 1px, transparent 1px);
  background-size: 7px 7px;
}

/* Research section icons */
.section-icon.research {
  background: rgba(99, 102, 241, 0.08);
  border-color: rgba(99, 102, 241, 0.2);
}

.icon-history {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.9);
  border-radius: 50%;
  border-bottom-color: transparent;
  position: relative;
}

.icon-history::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 6px;
  height: 6px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 50%;
  transform: translate(-50%, -50%);
}

.section-icon.resources {
  background: rgba(16, 185, 129, 0.08);
  border-color: rgba(16, 185, 129, 0.2);
}

.icon-team {
  width: 18px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.9);
  border-radius: 8px 8px 0 0;
  position: relative;
}

.icon-team::after {
  content: '';
  position: absolute;
  top: -5px;
  left: 50%;
  transform: translateX(-50%);
  width: 6px;
  height: 6px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 50%;
}

.section-icon.market {
  background: rgba(245, 158, 11, 0.08);
  border-color: rgba(245, 158, 11, 0.2);
}

.icon-globe {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.9);
  border-radius: 50%;
  position: relative;
}

.icon-globe::before,
.icon-globe::after {
  content: '';
  position: absolute;
  background: rgba(255, 255, 255, 0.9);
}

.icon-globe::before {
  width: 100%;
  height: 2px;
  top: 50%;
  left: 0;
  transform: translateY(-50%);
}

.icon-globe::after {
  width: 2px;
  height: 100%;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
}

.section-icon.timeline {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.15);
}

.icon-clock {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.9);
  border-radius: 50%;
  position: relative;
}

.icon-clock::after {
  content: '';
  position: absolute;
  top: 2px;
  left: 50%;
  width: 1px;
  height: 5px;
  background: rgba(255, 255, 255, 0.9);
}

.section-icon.mitigations {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.15);
}

.icon-shield {
  width: 14px;
  height: 16px;
  background: rgba(255, 255, 255, 0.9);
  clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
}

.section-icon.outofscope {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.15);
}

.icon-cross {
  width: 14px;
  height: 14px;
  position: relative;
}

.icon-cross::before,
.icon-cross::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  width: 100%;
  height: 2px;
  background: rgba(255, 255, 255, 0.9);
}

.icon-cross::before {
  transform: rotate(45deg);
}

.icon-cross::after {
  transform: rotate(-45deg);
}

.section-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.section-status {
  display: flex;
  align-items: center;
}

.status-badge {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: 12px;
  font-weight: 500;
  padding: 4px 10px;
  border-radius: 20px;
}

.status-badge.processing {
  color: rgba(255, 255, 255, 0.8);
  background: rgba(255, 255, 255, 0.08);
}

.status-badge.completed {
  color: rgba(100, 255, 100, 0.9);
  background: rgba(100, 255, 100, 0.1);
}

.status-badge.pending {
  color: rgba(255, 255, 255, 0.4);
  background: rgba(255, 255, 255, 0.03);
}

.status-dot {
  width: 6px;
  height: 6px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 50%;
  animation: pulse 1.5s ease-in-out infinite;
}

.section-content {
  padding-left: calc(40px + var(--space-4));
}

.section-content.completed-content {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 12px;
  padding: var(--space-4);
}

.section-content.scope-skeletons {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

/* Research content styling */
.research-content {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.research-summary {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.5;
  margin: 0;
}

.research-recommendation,
.team-composition {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.4;
  margin: 0;
  padding: var(--space-2) var(--space-3);
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  border-left: 3px solid rgba(99, 102, 241, 0.5);
}

.similar-projects,
.skill-coverage,
.tech-recommendations {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  align-items: center;
}

.projects-label,
.coverage-label,
.tech-label {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  font-weight: 500;
}

.project-chip,
.skill-chip,
.tech-chip {
  font-size: 11px;
  padding: 4px 10px;
  border-radius: 20px;
  background: rgba(99, 102, 241, 0.15);
  color: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(99, 102, 241, 0.3);
}

.skill-chip {
  background: rgba(16, 185, 129, 0.15);
  border-color: rgba(16, 185, 129, 0.3);
}

.tech-chip {
  background: rgba(245, 158, 11, 0.15);
  border-color: rgba(245, 158, 11, 0.3);
}

.market-stats {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-4);
}

.market-stat {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.stat-label {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  font-weight: 500;
}

.stat-value {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 600;
}

.result-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-4);
}

.result-item.full-width {
  grid-column: 1 / -1;
}

.result-item {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.result-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  font-weight: 500;
}

.result-value {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 600;
}

.result-value.capitalize {
  text-transform: capitalize;
}

.risks-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.risk-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3);
  background: rgba(239, 68, 68, 0.08);
  border-radius: 8px;
  border: 1px solid rgba(239, 68, 68, 0.15);
}

.risk-icon {
  color: rgba(239, 68, 68, 0.8);
}

.risk-text {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.8);
}

/* Additional styles for final document sections */
.deliverables-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.deliverable-item {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  padding: var(--space-3);
  background: rgba(34, 197, 94, 0.05);
  border-radius: 8px;
  border: 1px solid rgba(34, 197, 94, 0.1);
}

.bullet {
  width: 6px;
  height: 6px;
  background: rgba(34, 197, 94, 0.8);
  border-radius: 50%;
  margin-top: 6px;
  flex-shrink: 0;
}

.deliverable-text {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
}

.tech-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-3);
}

.tech-cell {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  padding: var(--space-3);
  background: rgba(6, 182, 212, 0.05);
  border-radius: 8px;
  border: 1px solid rgba(6, 182, 212, 0.1);
}

.tech-category {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.tech-value {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 600;
}

.timeline-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.timeline-item {
  display: flex;
  gap: var(--space-3);
  padding: var(--space-3);
  background: rgba(245, 158, 11, 0.05);
  border-radius: 8px;
  border: 1px solid rgba(245, 158, 11, 0.1);
}

.timeline-marker {
  width: 8px;
  height: 8px;
  background: rgba(245, 158, 11, 0.8);
  border-radius: 50%;
  margin-top: 4px;
  flex-shrink: 0;
}

.timeline-content {
  flex: 1;
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-1);
}

.timeline-phase {
  font-size: 14px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.timeline-duration {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  background: rgba(245, 158, 11, 0.1);
  padding: 2px 8px;
  border-radius: 4px;
}

.timeline-desc {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0;
}

.risk-marker {
  width: 16px;
  height: 16px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.8);
  flex-shrink: 0;
}

.risk-marker.small {
  width: 14px;
  height: 14px;
  font-size: 10px;
}

.mitigation-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.mitigation-item {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  padding: var(--space-3);
  background: rgba(16, 185, 129, 0.05);
  border-radius: 8px;
  border: 1px solid rgba(16, 185, 129, 0.1);
}

.mitigation-risk {
  font-size: 12px;
  font-weight: 600;
  color: rgba(239, 68, 68, 0.8);
}

.mitigation-text {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.8);
}

.outofscope-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.outofscope-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3);
  background: rgba(107, 114, 128, 0.05);
  border-radius: 8px;
  border: 1px solid rgba(107, 114, 128, 0.1);
}

.outofscope-marker {
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
  color: rgba(107, 114, 128, 0.8);
  flex-shrink: 0;
}

.outofscope-text {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
}

.document-footer {
  margin-top: var(--space-6);
  padding-top: var(--space-4);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.meta-text {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
  margin: 0;
}

/* Phase Indicator */
.phase-indicator {
  position: fixed;
  bottom: var(--space-6);
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: var(--space-3);
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(12px);
  padding: var(--space-3) var(--space-5);
  border-radius: 50px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  z-index: 100;
}

.phase-ring {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.5);
  border-radius: 50%;
  position: relative;
  animation: phasePulse 1.5s ease-in-out infinite;
}

.phase-ring::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 8px;
  height: 8px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 50%;
  animation: phaseDotPulse 1.5s ease-in-out infinite;
}

@keyframes phasePulse {
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.2);
    opacity: 0.7;
  }
}

@keyframes phaseDotPulse {
  0%, 100% {
    transform: translate(-50%, -50%) scale(1);
    opacity: 1;
  }
  50% {
    transform: translate(-50%, -50%) scale(0.6);
    opacity: 0.5;
  }
}

.phase-text {
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
}

@keyframes shimmer {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 0.3;
  }
  50% {
    opacity: 0.8;
  }
}
</style>
