<script setup lang="ts">
import { computed } from 'vue'

interface Option {
  value: string
  label: string
}

interface Props {
  modelValue: string[]
  options: Option[]
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
  'update:modelValue': [value: string[]]
}>()

const toggleOption = (value: string) => {
  if (props.disabled) return
  
  const newValue = props.modelValue.includes(value)
    ? props.modelValue.filter(v => v !== value)
    : [...props.modelValue, value]
  
  emit('update:modelValue', newValue)
}

const isSelected = (value: string) => {
  return props.modelValue.includes(value)
}

const inputId = computed(() => props.id || props.name)
</script>

<template>
  <div class="multi-select-chip">
    <div class="multi-select-chip__list">
      <button
        v-for="option in options"
        :key="option.value"
        type="button"
        :disabled="disabled"
        :aria-pressed="isSelected(option.value)"
        class="multi-select-chip__chip"
        :class="{
          'multi-select-chip__chip--selected': isSelected(option.value),
          'multi-select-chip__chip--disabled': disabled,
        }"
        @click="toggleOption(option.value)"
      >
        <span class="multi-select-chip__label">{{ option.label }}</span>
        <span
          v-if="isSelected(option.value)"
          class="multi-select-chip__remove"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="M18 6 6 18" />
            <path d="m6 6 12 12" />
          </svg>
        </span>
      </button>
    </div>
    <p
      v-if="error"
      :id="`${inputId}-error`"
      class="multi-select-chip__error"
      role="alert"
    >
      {{ error }}
    </p>
  </div>
</template>

<style scoped>
.multi-select-chip {
  position: relative;
}

.multi-select-chip__list {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.multi-select-chip__chip {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  font-family: var(--font-body);
  font-size: var(--font-size-body-sm);
  line-height: var(--line-height-normal);
  color: var(--text-primary);
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-full);
  cursor: pointer;
  transition: background var(--transition-fast), border-color var(--transition-fast);
  outline: none;
}

.multi-select-chip__chip:hover:not(:disabled) {
  background: var(--bg-tertiary);
  border-color: var(--border-secondary);
}

.multi-select-chip__chip:focus-visible {
  box-shadow: var(--focus-ring);
}

.multi-select-chip__chip--selected {
  background: var(--color-primary-50);
  border-color: var(--color-primary-300);
  color: var(--color-primary-700);
}

.multi-select-chip__chip--selected:hover:not(:disabled) {
  background: var(--color-primary-100);
  border-color: var(--color-primary-400);
}

.multi-select-chip__chip--disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.multi-select-chip__remove {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  color: var(--color-primary-600);
}

.multi-select-chip__error {
  font-family: var(--font-body);
  font-size: var(--font-size-body-xs);
  color: var(--color-error-500);
  margin: var(--space-2) 0 0 0;
  line-height: var(--line-height-normal);
}

@media (prefers-color-scheme: dark) {
  .multi-select-chip__chip--selected {
    background: rgba(72, 101, 129, 0.2);
    border-color: rgba(72, 101, 129, 0.4);
    color: var(--color-primary-300);
  }

  .multi-select-chip__chip--selected:hover:not(:disabled) {
    background: rgba(72, 101, 129, 0.3);
    border-color: rgba(72, 101, 129, 0.5);
  }

  .multi-select-chip__remove {
    color: var(--color-primary-400);
  }

  .multi-select-chip__error {
    color: var(--color-error-400);
  }
}
</style>
