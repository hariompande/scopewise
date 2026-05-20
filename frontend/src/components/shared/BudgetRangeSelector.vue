<script setup lang="ts">
import { computed } from 'vue'

interface RangeOption {
  value: string
  label: string
  sublabel?: string
}

interface Props {
  modelValue: string
  options: RangeOption[]
  disabled?: boolean
  error?: string
  id?: string
  name?: string
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false,
  error: '',
  id: '',
  name: '',
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const handleSelect = (value: string) => {
  if (props.disabled) return
  emit('update:modelValue', value)
}

const isSelected = (value: string) => {
  return props.modelValue === value
}

const inputId = computed(() => props.id || props.name)
</script>

<template>
  <div class="budget-range-selector">
    <div class="budget-range-selector__list">
      <button
        v-for="option in options"
        :key="option.value"
        type="button"
        :disabled="disabled"
        :aria-pressed="isSelected(option.value)"
        class="budget-range-selector__option"
        :class="{
          'budget-range-selector__option--selected': isSelected(option.value),
          'budget-range-selector__option--disabled': disabled,
        }"
        @click="handleSelect(option.value)"
      >
        <div class="budget-range-selector__content">
          <span class="budget-range-selector__label">{{ option.label }}</span>
          <span
            v-if="option.sublabel"
            class="budget-range-selector__sublabel"
          >
            {{ option.sublabel }}
          </span>
        </div>
        <div
          v-if="isSelected(option.value)"
          class="budget-range-selector__indicator"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="M20 6 9 17l-5-5" />
          </svg>
        </div>
      </button>
    </div>
    <p
      v-if="error"
      :id="`${inputId}-error`"
      class="budget-range-selector__error"
      role="alert"
    >
      {{ error }}
    </p>
  </div>
</template>

<style scoped>
.budget-range-selector {
  position: relative;
}

.budget-range-selector__list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--space-3);
}

.budget-range-selector__option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4);
  font-family: var(--font-body);
  font-size: var(--font-size-body-sm);
  line-height: var(--line-height-normal);
  color: var(--text-primary);
  background: var(--bg-primary);
  border: 2px solid var(--border-primary);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: border-color var(--transition-fast), background var(--transition-fast);
  outline: none;
  text-align: left;
}

.budget-range-selector__option:hover:not(:disabled) {
  border-color: var(--border-secondary);
  background: var(--bg-secondary);
}

.budget-range-selector__option:focus-visible {
  box-shadow: var(--focus-ring);
}

.budget-range-selector__option--selected {
  border-color: var(--color-primary-500);
  background: var(--color-primary-50);
}

.budget-range-selector__option--selected:hover:not(:disabled) {
  background: var(--color-primary-100);
}

.budget-range-selector__option--disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.budget-range-selector__content {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.budget-range-selector__label {
  font-weight: var(--font-weight-medium);
}

.budget-range-selector__sublabel {
  font-size: var(--font-size-body-xs);
  color: var(--text-tertiary);
}

.budget-range-selector__indicator {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-primary-600);
  background: var(--color-primary-500);
  border-radius: var(--radius-full);
}

.budget-range-selector__error {
  font-family: var(--font-body);
  font-size: var(--font-size-body-xs);
  color: var(--color-error-500);
  margin: var(--space-2) 0 0 0;
  line-height: var(--line-height-normal);
}

@media (prefers-color-scheme: dark) {
  .budget-range-selector__option--selected {
    border-color: var(--color-primary-400);
    background: rgba(72, 101, 129, 0.2);
  }

  .budget-range-selector__option--selected:hover:not(:disabled) {
    background: rgba(72, 101, 129, 0.3);
  }

  .budget-range-selector__indicator {
    color: var(--bg-primary);
    background: var(--color-primary-400);
  }

  .budget-range-selector__error {
    color: var(--color-error-400);
  }
}
</style>
