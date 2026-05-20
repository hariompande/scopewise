import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export interface DiscoveryForm {
  projectType: string
  budget: string
  timeline: string
  features: string[]
  targetAudience: string
  technicalRequirements: string
  businessGoals: string
  constraints: string
  additionalNotes: string
}

export const useDiscoveryStore = defineStore('discovery', () => {
  // Form state
  const form = ref<DiscoveryForm>({
    projectType: '',
    budget: '',
    timeline: '',
    features: [],
    targetAudience: '',
    technicalRequirements: '',
    businessGoals: '',
    constraints: '',
    additionalNotes: '',
  })

  // Loading state
  const isSubmitting = ref(false)
  const isStreaming = ref(false)

  // Pipeline state
  const currentPhase = ref<string>('')
  const currentToken = ref<string>('')
  const scopeDocument = ref<Record<string, unknown> | null>(null)
  const error = ref<string | null>(null)

  // Intermediate results for progressive display
  const classificationResult = ref<Record<string, unknown> | null>(null)
  const riskAnalysisResult = ref<Record<string, unknown> | null>(null)
  const scopeGenerationResult = ref<Record<string, unknown> | null>(null)
  const completedPhases = ref<Set<string>>(new Set())

  // Computed
  const isFormValid = computed(() => {
    return (
      form.value.projectType.trim() !== '' &&
      form.value.budget.trim() !== '' &&
      form.value.timeline.trim() !== '' &&
      form.value.features.length > 0
    )
  })

  const formattedUserInput = computed(() => {
    const parts = [
      `Project Type: ${form.value.projectType}`,
      `Budget: ${form.value.budget}`,
      `Timeline: ${form.value.timeline}`,
      `Features: ${form.value.features.join(', ')}`,
      `Target Audience: ${form.value.targetAudience}`,
      `Technical Requirements: ${form.value.technicalRequirements}`,
      `Business Goals: ${form.value.businessGoals}`,
      `Constraints: ${form.value.constraints}`,
      `Additional Notes: ${form.value.additionalNotes}`,
    ]
    return parts.filter(p => p.trim() !== '').join('\n')
  })

  return {
    // State
    form,
    isSubmitting,
    isStreaming,
    currentPhase,
    currentToken,
    scopeDocument,
    error,
    // Intermediate results
    classificationResult,
    riskAnalysisResult,
    scopeGenerationResult,
    completedPhases,
    // Computed
    isFormValid,
    formattedUserInput,
  }
})
