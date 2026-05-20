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
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
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
  color: rgba(255, 255, 255, 0.8);
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  outline: none;
  text-align: left;
  backdrop-filter: blur(10px);
}

.budget-range-selector__option:hover:not(:disabled) {
  border-color: rgba(255, 255, 255, 0.25);
  background: rgba(255, 255, 255, 0.08);
  transform: translateY(-1px);
}

.budget-range-selector__option:focus-visible {
  box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.2);
}

.budget-range-selector__option--selected {
  border-color: rgba(255, 255, 255, 0.5);
  background: rgba(255, 255, 255, 0.9);
  color: #000000;
}

.budget-range-selector__option--selected:hover:not(:disabled) {
  background: #ffffff;
  border-color: #ffffff;
  box-shadow: 0 4px 20px rgba(255, 255, 255, 0.2);
}

.budget-range-selector__option--disabled {
  opacity: 0.3;
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
  color: rgba(255, 255, 255, 0.5);
}

.budget-range-selector__option--selected .budget-range-selector__sublabel {
  color: rgba(0, 0, 0, 0.6);
}

.budget-range-selector__indicator {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #000000;
  background: rgba(0, 0, 0, 0.2);
  border-radius: var(--radius-full);
}

.budget-range-selector__error {
  font-family: var(--font-body);
  font-size: var(--font-size-body-xs);
  color: #ff6b6b;
  margin: var(--space-2) 0 0 0;
  line-height: var(--line-height-normal);
}
</style>
