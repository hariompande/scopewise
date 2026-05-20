<template>
  <div class="discovery-form">
    <PageHeader :title="t('discovery.title')" />

    <!-- Progress Bar -->
    <div class="progress-container">
      <div class="progress-bar">
        <div
          class="progress-fill"
          :style="{ width: `${((currentStep + 1) / steps.length) * 100}%` }"
        />
      </div>
      <div class="progress-steps">
        <button
          v-for="(step, index) in steps"
          :key="step.id"
          type="button"
          class="step-indicator"
          :class="{
            'step-indicator--active': currentStep === index,
            'step-indicator--completed': currentStep > index,
            'step-indicator--clickable': currentStep > index
          }"
          :disabled="currentStep <= index && !canNavigateToStep(index)"
          @click="goToStep(index)"
        >
          <span class="step-number">{{ index + 1 }}</span>
          <span class="step-label">{{ step.label }}</span>
        </button>
      </div>
    </div>

    <form class="discovery-form__form" @submit.prevent="handleSubmit">
      <!-- Step 1: Project Overview -->
      <div v-if="currentStep === 0" class="step-content">
        <div class="step-header">
          <h3 class="step-title">{{ steps[0]?.label }}</h3>
          <p class="step-description">Define the foundation of your project</p>
        </div>

        <FormSection :label="t('discovery.projectType.label')" required>
          <SelectDropdown
            id="discovery-project-type"
            v-model="discoveryStore.form.projectType"
            :options="projectTypeOptions"
            :placeholder="t('discovery.projectType.placeholder')"
          />
        </FormSection>

        <FormSection :label="t('discovery.budget.label')" required>
          <BudgetRangeSelector
            id="discovery-budget"
            v-model="form.budget"
            :options="budgetOptions"
          />
        </FormSection>

        <FormSection :label="t('discovery.timeline.label')" required>
          <SelectDropdown
            id="discovery-timeline"
            v-model="form.timeline"
            :options="timelineOptions"
            :placeholder="t('discovery.timeline.placeholder')"
          />
        </FormSection>
      </div>

      <!-- Step 2: Features -->
      <div v-if="currentStep === 1" class="step-content">
        <div class="step-header">
          <h3 class="step-title">{{ steps[1]?.label }}</h3>
          <p class="step-description">What functionality does your project need?</p>
        </div>

        <FormSection :label="t('discovery.features.label')" required>
          <div class="discovery-form__feature-input">
            <TextInput
              id="discovery-feature"
              v-model="newFeature"
              :placeholder="t('discovery.features.placeholder')"
              autocomplete="off"
              @keydown.enter.prevent="handleAddFeature"
            />
            <button
              :disabled="!newFeature.trim()"
              type="button"
              class="discovery-form__feature-button"
              @click="handleAddFeature"
            >
              {{ t('discovery.features.addButton') }}
            </button>
          </div>
          <MultiSelectChip
            id="discovery-feature-list"
            v-model="form.features"
            :options="featureOptions"
            :error="featuresError"
          />
        </FormSection>
      </div>

      <!-- Step 3: Audience & Goals -->
      <div v-if="currentStep === 2" class="step-content">
        <div class="step-header">
          <h3 class="step-title">{{ steps[2]?.label }}</h3>
          <p class="step-description">Who are you building for and why?</p>
        </div>

        <FormSection :label="t('discovery.targetAudience.label')">
          <FormTextarea
            id="discovery-target-audience"
            v-model="form.targetAudience"
            :placeholder="t('discovery.targetAudience.placeholder')"
            :rows="4"
          />
        </FormSection>

        <FormSection :label="t('discovery.businessGoals.label')">
          <FormTextarea
            id="discovery-business-goals"
            v-model="form.businessGoals"
            :placeholder="t('discovery.businessGoals.placeholder')"
            :rows="4"
          />
        </FormSection>
      </div>

      <!-- Step 4: Technical Requirements -->
      <div v-if="currentStep === 3" class="step-content">
        <div class="step-header">
          <h3 class="step-title">{{ steps[3]?.label }}</h3>
          <p class="step-description">Technical specifications and limitations</p>
        </div>

        <FormSection :label="t('discovery.technicalRequirements.label')">
          <FormTextarea
            id="discovery-technical-requirements"
            v-model="form.technicalRequirements"
            :placeholder="t('discovery.technicalRequirements.placeholder')"
            :rows="4"
          />
        </FormSection>

        <FormSection :label="t('discovery.constraints.label')">
          <FormTextarea
            id="discovery-constraints"
            v-model="form.constraints"
            :placeholder="t('discovery.constraints.placeholder')"
            :rows="4"
          />
        </FormSection>
      </div>

      <!-- Step 5: Additional Notes -->
      <div v-if="currentStep === 4" class="step-content">
        <div class="step-header">
          <h3 class="step-title">{{ steps[4]?.label }}</h3>
          <p class="step-description">Anything else we should know?</p>
        </div>

        <FormSection :label="t('discovery.additionalNotes.label')">
          <FormTextarea
            id="discovery-additional-notes"
            v-model="form.additionalNotes"
            :placeholder="t('discovery.additionalNotes.placeholder')"
            :rows="6"
          />
        </FormSection>
      </div>

      <!-- Step 6: Review -->
      <div v-if="currentStep === 5" class="step-content">
        <div class="step-header">
          <h3 class="step-title">{{ steps[5]?.label }}</h3>
          <p class="step-description">Review your project details before submitting</p>
        </div>

        <div class="review-section">
          <div class="review-group">
            <h4 class="review-group-title">Project Overview</h4>
            <div class="review-item">
              <span class="review-label">Type:</span>
              <span class="review-value">{{ getProjectTypeLabel(form.projectType) || '—' }}</span>
            </div>
            <div class="review-item">
              <span class="review-label">Budget:</span>
              <span class="review-value">{{ form.budget || '—' }}</span>
            </div>
            <div class="review-item">
              <span class="review-label">Timeline:</span>
              <span class="review-value">{{ form.timeline || '—' }}</span>
            </div>
          </div>

          <div class="review-group">
            <h4 class="review-group-title">Features</h4>
            <div class="review-tags">
              <span
                v-for="feature in form.features"
                :key="feature"
                class="review-tag"
              >{{ feature }}</span>
              <span v-if="form.features.length === 0" class="review-empty">No features added</span>
            </div>
          </div>

          <div class="review-group">
            <h4 class="review-group-title">Audience & Goals</h4>
            <div class="review-item">
              <span class="review-label">Target Audience:</span>
              <span class="review-value">{{ form.targetAudience || '—' }}</span>
            </div>
            <div class="review-item">
              <span class="review-label">Business Goals:</span>
              <span class="review-value">{{ form.businessGoals || '—' }}</span>
            </div>
          </div>

          <div class="review-group">
            <h4 class="review-group-title">Technical</h4>
            <div class="review-item">
              <span class="review-label">Requirements:</span>
              <span class="review-value">{{ form.technicalRequirements || '—' }}</span>
            </div>
            <div class="review-item">
              <span class="review-label">Constraints:</span>
              <span class="review-value">{{ form.constraints || '—' }}</span>
            </div>
          </div>

          <div v-if="form.additionalNotes" class="review-group">
            <h4 class="review-group-title">Additional Notes</h4>
            <p class="review-text">{{ form.additionalNotes }}</p>
          </div>
        </div>
      </div>

      <!-- Navigation -->
      <div class="discovery-form__actions">
        <button
          v-if="currentStep > 0"
          type="button"
          class="discovery-form__button discovery-form__button--secondary"
          :disabled="isSubmitting || isStreaming"
          @click="prevStep"
        >
          <svg class="button-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 12H5M12 19l-7-7 7-7" />
          </svg>
          Back
        </button>

        <button
          v-if="currentStep < steps.length - 1"
          type="button"
          class="discovery-form__button discovery-form__button--primary"
          :disabled="!isStepValid || isSubmitting || isStreaming"
          @click="nextStep"
        >
          Next
          <svg class="button-icon button-icon--end" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M5 12h14M12 5l7 7-7 7" />
          </svg>
        </button>

        <button
          v-else
          :disabled="!isFormValid || isSubmitting || isStreaming"
          type="submit"
          class="discovery-form__button discovery-form__button--primary discovery-form__button--submit flex"
        >
          <span v-if="isSubmitting">{{ t('discovery.actions.submitting') }}</span>
          <span v-else-if="isStreaming">{{ t('discovery.actions.processing') }}</span>
          <span class="flex gap-3" v-else>
            {{ t('discovery.actions.submit') }}
            <svg class="button-icon button-icon--end" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M5 12h14M12 5l7 7-7 7" />
            </svg>
          </span>
        </button>

        <button
          v-if="currentStep === 0"
          :disabled="isSubmitting || isStreaming"
          type="button"
          class="discovery-form__button discovery-form__button--ghost"
          @click="handleResetForm"
        >
          Reset
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { storeToRefs } from 'pinia'
import BudgetRangeSelector from '@/components/shared/BudgetRangeSelector.vue'
import FormSection from '@/components/shared/FormSection.vue'
import FormTextarea from '@/components/shared/FormTextarea.vue'
import MultiSelectChip from '@/components/shared/MultiSelectChip.vue'
import SelectDropdown from '@/components/shared/SelectDropdown.vue'
import TextInput from '@/components/shared/TextInput.vue'
import PageHeader from '@/components/shared/PageHeader.vue'
import { useDiscoveryStore } from '@/stores/discovery'
import { useAgentStream } from '@/composables/useAgentStream'

interface OptionKey {
  value: string
  labelKey: string
  sublabelKey?: string
}

interface Step {
  id: string
  label: string
}

const { t } = useI18n()

const discoveryStore = useDiscoveryStore()
const { form, isSubmitting, isStreaming, isFormValid, formattedUserInput } = storeToRefs(discoveryStore)
const { connect } = useAgentStream()

const currentStep = ref(0)

const steps: Step[] = [
  { id: 'overview', label: 'Overview' },
  { id: 'features', label: 'Features' },
  { id: 'audience', label: 'Audience & Goals' },
  { id: 'technical', label: 'Technical' },
  { id: 'notes', label: 'Notes' },
  { id: 'review', label: 'Review' },
]

const isStepValid = computed(() => {
  switch (currentStep.value) {
    case 0: // Overview
      return !!form.value.projectType && !!form.value.budget && !!form.value.timeline
    case 1: // Features
      return form.value.features.length > 0
    default:
      return true
  }
})

const nextStep = () => {
  if (currentStep.value < steps.length - 1) {
    currentStep.value++
  }
}

const prevStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

const goToStep = (index: number) => {
  if (index < currentStep.value || canNavigateToStep(index)) {
    currentStep.value = index
  }
}

const canNavigateToStep = (index: number): boolean => {
  // Can navigate to any step if all previous required steps are valid
  if (index === 0) return true
  if (index === 1) return !!form.value.projectType && !!form.value.budget && !!form.value.timeline
  if (index <= 2) return form.value.features.length > 0 && !!form.value.projectType && !!form.value.budget && !!form.value.timeline
  return isFormValid.value
}

const getProjectTypeLabel = (value: string): string => {
  const option = projectTypeOptionKeys.find(opt => opt.value === value)
  return option ? t(option.labelKey) : value
}

const projectTypeOptionKeys: OptionKey[] = [
  { value: 'web-application', labelKey: 'discovery.projectType.options.webApplication' },
  { value: 'mobile-app', labelKey: 'discovery.projectType.options.mobileApp' },
  { value: 'e-commerce', labelKey: 'discovery.projectType.options.ecommerce' },
  { value: 'saas', labelKey: 'discovery.projectType.options.saas' },
  { value: 'api-integration', labelKey: 'discovery.projectType.options.apiIntegration' },
  { value: 'data-analytics', labelKey: 'discovery.projectType.options.dataAnalytics' },
  { value: 'custom-software', labelKey: 'discovery.projectType.options.customSoftware' },
  { value: 'other', labelKey: 'discovery.projectType.options.other' },
]

const budgetOptionKeys: OptionKey[] = [
  { value: '< $10k', labelKey: 'discovery.budget.options.under10k' },
  { value: '$10k - $25k', labelKey: 'discovery.budget.options.tenToTwentyFive' },
  { value: '$25k - $50k', labelKey: 'discovery.budget.options.twentyFiveToFifty' },
  { value: '$50k - $100k', labelKey: 'discovery.budget.options.fiftyToHundred' },
  { value: '$100k - $250k', labelKey: 'discovery.budget.options.hundredToTwoFifty' },
  { value: '$250k+', labelKey: 'discovery.budget.options.twoFiftyPlus' },
]

const timelineOptionKeys: OptionKey[] = [
  { value: '1-2 months', labelKey: 'discovery.timeline.options.oneToTwo' },
  { value: '3-4 months', labelKey: 'discovery.timeline.options.threeToFour' },
  { value: '5-6 months', labelKey: 'discovery.timeline.options.fiveToSix' },
  { value: '6-12 months', labelKey: 'discovery.timeline.options.sixToTwelve' },
  { value: '12+ months', labelKey: 'discovery.timeline.options.twelvePlus' },
]

const newFeature = ref<string>('')

const projectTypeOptions = computed(() =>
  projectTypeOptionKeys.map(option => ({
    value: option.value,
    label: t(option.labelKey),
  })),
)

const budgetOptions = computed(() =>
  budgetOptionKeys.map(option => ({
    value: option.value,
    label: t(option.labelKey),
  })),
)

const timelineOptions = computed(() =>
  timelineOptionKeys.map(option => ({
    value: option.value,
    label: t(option.labelKey),
  })),
)

const featureOptions = computed(() =>
  form.value.features.map(feature => ({
    value: feature,
    label: feature,
  })),
)

const featuresError = computed(() =>
  form.value.features.length === 0 ? t('discovery.features.error') : '',
)

const handleAddFeature = () => {
  const trimmedFeature = newFeature.value.trim()
  if (!trimmedFeature) return

  if (trimmedFeature && !form.value.features.includes(trimmedFeature)) {
    form.value.features.push(trimmedFeature)
  }
  newFeature.value = ''
}

const handleResetForm = () => {
  form.value = {
    projectType: '',
    budget: '',
    timeline: '',
    features: [],
    targetAudience: '',
    technicalRequirements: '',
    businessGoals: '',
    constraints: '',
    additionalNotes: '',
  }
  newFeature.value = ''
}

const handleSubmit = () => {
  if (isFormValid.value) {
    connect(formattedUserInput.value)
  }
}
</script>

<style scoped>
/* Neoglassmorphism Black & White Theme */
.discovery-form {
  /* Glass effect with black/white palette */
  width: 100%;
  height: fit-content;
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: var(--space-8);
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow:
    0 8px 32px rgba(0, 0, 0, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);
}

/* Progress Bar Container */
.progress-container {
  margin-bottom: var(--space-8);
}

.progress-bar {
  height: 4px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: var(--space-6);
  box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.3);
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #ffffff 0%, #a0a0a0 100%);
  border-radius: 2px;
  transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
}

/* Step Indicators */
.progress-steps {
  display: flex;
  justify-content: space-between;
  gap: var(--space-2);
  flex-wrap: wrap;
}

.step-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  background: transparent;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
  opacity: 0.5;
}

.step-indicator--active {
  opacity: 1;
}

.step-indicator--completed {
  opacity: 0.8;
}

.step-indicator--clickable:hover:not(:disabled) {
  opacity: 1;
  transform: translateY(-2px);
}

.step-indicator:disabled {
  cursor: not-allowed;
  opacity: 0.3;
}

.step-number {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-family: var(--font-heading);
  font-size: var(--font-size-body-sm);
  font-weight: var(--font-weight-semibold);
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.6);
  transition: all 0.3s ease;
}

.step-indicator--active .step-number {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
  color: #ffffff;
  box-shadow: 0 0 20px rgba(255, 255, 255, 0.15);
}

.step-indicator--completed .step-number {
  background: rgba(255, 255, 255, 0.9);
  border-color: #ffffff;
  color: #000000;
}

.step-label {
  font-family: var(--font-body);
  font-size: var(--font-size-body-xs);
  color: rgba(255, 255, 255, 0.5);
  white-space: nowrap;
  transition: color 0.3s ease;
}

.step-indicator--active .step-label {
  color: #ffffff;
}

.step-indicator--completed .step-label {
  color: rgba(255, 255, 255, 0.8);
}

/* Step Content */
.step-content {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateX(10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.step-header {
  margin-bottom: var(--space-6);
  padding-bottom: var(--space-4);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.step-title {
  font-family: var(--font-heading);
  font-size: var(--font-size-h4);
  font-weight: var(--font-weight-semibold);
  color: #ffffff !important;
  margin: 0 0 var(--space-2) 0;
  letter-spacing: -0.02em;
}

.step-description {
  font-family: var(--font-body);
  font-size: var(--font-size-body);
  color: rgba(255, 255, 255, 0.6) !important;
  margin: 0;
}

.discovery-form__form {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
  color: #ffffff;
}

.discovery-form__feature-input {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  margin-bottom: var(--space-3);
}

/* Glassmorphism Feature Button */
.discovery-form__feature-button {
  align-self: flex-start;
  padding: var(--space-3) var(--space-5);
  font-family: var(--font-body);
  font-size: var(--font-size-body-sm);
  font-weight: var(--font-weight-medium);
  color: #ffffff;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.discovery-form__feature-button:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
  box-shadow: 0 4px 20px rgba(255, 255, 255, 0.1);
  transform: translateY(-1px);
}

.discovery-form__feature-button:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

/* Review Section */
.review-section {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
  max-height: 400px;
  overflow-y: auto;
  padding-right: var(--space-3);
}

.review-section::-webkit-scrollbar {
  width: 4px;
}

.review-section::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 2px;
}

.review-section::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.15);
  border-radius: 2px;
}

.review-group {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 16px;
  padding: var(--space-4);
  backdrop-filter: blur(10px);
}

.review-group-title {
  font-family: var(--font-heading);
  font-size: var(--font-size-body-sm);
  font-weight: var(--font-weight-semibold);
  color: #ffffff;
  margin: 0 0 var(--space-3) 0;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.review-item {
  display: flex;
  justify-content: space-between;
  gap: var(--space-3);
  padding: var(--space-2) 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}

.review-item:last-child {
  border-bottom: none;
}

.review-label {
  font-family: var(--font-body);
  font-size: var(--font-size-body-sm);
  color: rgba(255, 255, 255, 0.5);
}

.review-value {
  font-family: var(--font-body);
  font-size: var(--font-size-body-sm);
  color: rgba(255, 255, 255, 0.9);
  text-align: right;
}

.review-tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.review-tag {
  padding: var(--space-1) var(--space-3);
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 20px;
  font-family: var(--font-body);
  font-size: var(--font-size-body-xs);
  color: #ffffff;
}

.review-empty {
  font-family: var(--font-body);
  font-size: var(--font-size-body-sm);
  color: rgba(255, 255, 255, 0.3);
  font-style: italic;
}

.review-text {
  font-family: var(--font-body);
  font-size: var(--font-size-body-sm);
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.6;
  margin: 0;
}

/* Navigation Actions */
.discovery-form__actions {
  display: flex;
  flex-direction: row;
  gap: var(--space-3);
  margin-top: var(--space-8);
  padding-top: var(--space-6);
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

/* Glassmorphism Buttons */
.discovery-form__button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-6);
  font-family: var(--font-body);
  font-size: var(--font-size-body-sm);
  font-weight: var(--font-weight-medium);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.15);
}

.button-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.button-icon--end {
  margin-left: var(--space-1);
}

.discovery-form__button:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

/* Primary - White Glass */
.discovery-form__button--primary {
  color: #000000;
  background: rgba(255, 255, 255, 0.9);
  border-color: rgba(255, 255, 255, 0.5);
  flex: 1;
}

.discovery-form__button--primary:hover:not(:disabled) {
  background: #ffffff;
  border-color: #ffffff;
  box-shadow: 0 4px 24px rgba(255, 255, 255, 0.25);
  transform: translateY(-2px);
}

/* Submit variant */
.discovery-form__button--submit {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(200, 200, 200, 0.9) 100%);
}

/* Secondary - Dark Glass */
.discovery-form__button--secondary {
  color: rgba(255, 255, 255, 0.9);
  background: rgba(0, 0, 0, 0.3);
  border-color: rgba(255, 255, 255, 0.1);
}

.discovery-form__button--secondary:hover:not(:disabled) {
  background: rgba(0, 0, 0, 0.5);
  border-color: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
}

/* Ghost - Transparent */
.discovery-form__button--ghost {
  color: rgba(255, 255, 255, 0.6);
  background: transparent;
  border-color: rgba(255, 255, 255, 0.1);
}

.discovery-form__button--ghost:hover:not(:disabled) {
  color: rgba(255, 255, 255, 0.9);
  border-color: rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.03);
}

@media (min-width: 48rem) {
  .discovery-form__feature-input {
    flex-direction: row;
    align-items: flex-start;
  }

  .step-indicator {
    flex-direction: row;
    gap: var(--space-3);
  }
}

@media (max-width: 47.99rem) {
  .progress-steps {
    justify-content: center;
  }

  .step-label {
    display: none;
  }

  .step-indicator--active .step-label {
    display: block;
  }
}
</style>
