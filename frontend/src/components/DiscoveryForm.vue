<template>
  <div class="discovery-form">
    <PageHeader
      :title="t('discovery.title')"
    />

    <form
      class="discovery-form__form"
      @submit.prevent="handleSubmit"
    >
      <FormSection
        :label="t('discovery.projectType.label')"
        required
      >
        <SelectDropdown
          id="discovery-project-type"
          v-model="discoveryStore.form.projectType"
          :options="projectTypeOptions"
          :placeholder="t('discovery.projectType.placeholder')"
        />
      </FormSection>

      <FormSection
        :label="t('discovery.budget.label')"
        required
      >
        <BudgetRangeSelector
          id="discovery-budget"
          v-model="form.budget"
          :options="budgetOptions"
        />
      </FormSection>

      <FormSection
        :label="t('discovery.timeline.label')"
        required
      >
        <SelectDropdown
          id="discovery-timeline"
          v-model="form.timeline"
          :options="timelineOptions"
          :placeholder="t('discovery.timeline.placeholder')"
        />
      </FormSection>

      <FormSection
        :label="t('discovery.features.label')"
        required
      >
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

      <FormSection
        :label="t('discovery.targetAudience.label')"
      >
        <FormTextarea
          id="discovery-target-audience"
          v-model="form.targetAudience"
          :placeholder="t('discovery.targetAudience.placeholder')"
          :rows="3"
        />
      </FormSection>

      <FormSection
        :label="t('discovery.technicalRequirements.label')"
      >
        <FormTextarea
          id="discovery-technical-requirements"
          v-model="form.technicalRequirements"
          :placeholder="t('discovery.technicalRequirements.placeholder')"
          :rows="3"
        />
      </FormSection>

      <FormSection
        :label="t('discovery.businessGoals.label')"
      >
        <FormTextarea
          id="discovery-business-goals"
          v-model="form.businessGoals"
          :placeholder="t('discovery.businessGoals.placeholder')"
          :rows="3"
        />
      </FormSection>

      <FormSection
        :label="t('discovery.constraints.label')"
      >
        <FormTextarea
          id="discovery-constraints"
          v-model="form.constraints"
          :placeholder="t('discovery.constraints.placeholder')"
          :rows="3"
        />
      </FormSection>

      <FormSection
        :label="t('discovery.additionalNotes.label')"
      >
        <FormTextarea
          id="discovery-additional-notes"
          v-model="form.additionalNotes"
          :placeholder="t('discovery.additionalNotes.placeholder')"
          :rows="3"
        />
      </FormSection>

      <div class="discovery-form__actions">
        <button
          :disabled="!isFormValid || isSubmitting || isStreaming"
          type="submit"
          class="discovery-form__button discovery-form__button--primary"
        >
          <span v-if="isSubmitting">{{ t('discovery.actions.submitting') }}</span>
          <span v-else-if="isStreaming">{{ t('discovery.actions.processing') }}</span>
          <span v-else>{{ t('discovery.actions.submit') }}</span>
        </button>
        <button
          :disabled="isSubmitting || isStreaming"
          type="button"
          class="discovery-form__button discovery-form__button--secondary"
          @click="handleResetForm"
        >
          {{ t('discovery.actions.reset') }}
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

const { t } = useI18n()

const discoveryStore = useDiscoveryStore()
const { form, isSubmitting, isStreaming, isFormValid, formattedUserInput } = storeToRefs(discoveryStore)
const { connect } = useAgentStream()

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
.discovery-form {
  background: var(--bg-primary);
  border-radius: var(--radius-lg);
  padding: var(--space-8);
  box-shadow: var(--shadow-md);
  border: 1px solid var(--border-primary);
}

.discovery-form__form {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
}

.discovery-form__feature-input {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  margin-bottom: var(--space-3);
}

.discovery-form__feature-button {
  align-self: flex-start;
  padding: var(--space-3) var(--space-5);
  font-family: var(--font-body);
  font-size: var(--font-size-body-sm);
  font-weight: var(--font-weight-medium);
  color: white;
  background: var(--color-primary-600);
  border: 1px solid var(--color-primary-600);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background var(--transition-fast), border-color var(--transition-fast), opacity var(--transition-fast);
}

.discovery-form__feature-button:hover:not(:disabled) {
  background: var(--color-primary-700);
  border-color: var(--color-primary-700);
}

.discovery-form__feature-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.discovery-form__actions {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  margin-top: var(--space-4);
}

.discovery-form__button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-3) var(--space-6);
  font-family: var(--font-body);
  font-size: var(--font-size-body-sm);
  font-weight: var(--font-weight-medium);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background var(--transition-fast), border-color var(--transition-fast), opacity var(--transition-fast);
}

.discovery-form__button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.discovery-form__button--primary {
  color: white;
  background: var(--color-primary-600);
  border: 1px solid var(--color-primary-600);
}

.discovery-form__button--primary:hover:not(:disabled) {
  background: var(--color-primary-700);
  border-color: var(--color-primary-700);
}

.discovery-form__button--secondary {
  color: var(--text-primary);
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
}

.discovery-form__button--secondary:hover:not(:disabled) {
  background: var(--bg-tertiary);
  border-color: var(--border-secondary);
}

@media (min-width: 48rem) {
  .discovery-form__feature-input {
    flex-direction: row;
    align-items: flex-start;
  }

  .discovery-form__actions {
    flex-direction: row;
  }

  .discovery-form__button--primary {
    flex: 1;
  }
}

@media (prefers-color-scheme: dark) {
  .discovery-form__feature-button {
    background: var(--color-primary-500);
    border-color: var(--color-primary-500);
  }

  .discovery-form__feature-button:hover:not(:disabled) {
    background: var(--color-primary-400);
    border-color: var(--color-primary-400);
  }

  .discovery-form__button--primary {
    background: var(--color-primary-500);
    border-color: var(--color-primary-500);
  }

  .discovery-form__button--primary:hover:not(:disabled) {
    background: var(--color-primary-400);
    border-color: var(--color-primary-400);
  }
}
</style>
