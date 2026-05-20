<script setup lang="ts">
import { computed } from 'vue'

interface Option {
  value: string
  label: string
  disabled?: boolean
}

interface Props {
  modelValue: string
  options: Option[]
  placeholder?: string
  disabled?: boolean
  error?: string
  id?: string
  name?: string
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: 'Select an option',
  disabled: false,
  error: '',
  id: '',
  name: '',
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
  focus: [event: FocusEvent]
  blur: [event: FocusEvent]
}>()

const handleChange = (event: Event) => {
  const target = event.target as HTMLSelectElement
  emit('update:modelValue', target.value)
}

const handleFocus = (event: FocusEvent) => {
  emit('focus', event)
}

const handleBlur = (event: FocusEvent) => {
  emit('blur', event)
}

const inputId = computed(() => props.id || props.name)
</script>

<template>
  <div class="select-dropdown">
    <select
      :id="inputId"
      :name="name"
      :value="modelValue"
      :disabled="disabled"
      :aria-invalid="!!error"
      :aria-describedby="error ? `${inputId}-error` : undefined"
      class="select-dropdown__field"
      :class="{
        'select-dropdown__field--error': !!error,
        'select-dropdown__field--placeholder': !modelValue,
      }"
      @change="handleChange"
      @focus="handleFocus"
      @blur="handleBlur"
    >
      <option
        value=""
        disabled
      >
        {{ placeholder }}
      </option>
      <option
        v-for="option in options"
        :key="option.value"
        :value="option.value"
        :disabled="option.disabled"
      >
        {{ option.label }}
      </option>
    </select>
    <div class="select-dropdown__icon">
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
        <path d="m6 9 6 6 6-6" />
      </svg>
    </div>
    <p
      v-if="error"
      :id="`${inputId}-error`"
      class="select-dropdown__error"
      role="alert"
    >
      {{ error }}
    </p>
  </div>
</template>

<style scoped>
.select-dropdown {
  position: relative;
}

.select-dropdown__field {
  width: 100%;
  padding: var(--space-3) var(--space-4);
  padding-right: var(--space-10);
  font-family: var(--font-body);
  font-size: var(--font-size-body-md);
  line-height: var(--line-height-normal);
  color: var(--text-primary);
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
  outline: none;
  appearance: none;
  cursor: pointer;
}

.select-dropdown__field--placeholder {
  color: var(--text-tertiary);
}

.select-dropdown__field:hover:not(:disabled) {
  border-color: var(--border-secondary);
}

.select-dropdown__field:focus {
  border-color: var(--color-primary-500);
  box-shadow: var(--shadow-focus);
}

.select-dropdown__field--error {
  border-color: var(--color-error-500);
}

.select-dropdown__field--error:focus {
  border-color: var(--color-error-500);
  box-shadow: 0 0 0 2px var(--bg-primary), 0 0 0 4px var(--color-error-500);
}

.select-dropdown__field:disabled {
  background: var(--bg-secondary);
  color: var(--text-tertiary);
  cursor: not-allowed;
}

.select-dropdown__icon {
  position: absolute;
  right: var(--space-4);
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
  color: var(--text-tertiary);
}

.select-dropdown__error {
  font-family: var(--font-body);
  font-size: var(--font-size-body-xs);
  color: var(--color-error-500);
  margin: var(--space-2) 0 0 0;
  line-height: var(--line-height-normal);
}

@media (prefers-color-scheme: dark) {
  .select-dropdown__field--error {
    border-color: var(--color-error-400);
  }

  .select-dropdown__field--error:focus {
    border-color: var(--color-error-400);
    box-shadow: 0 0 0 2px var(--bg-primary), 0 0 0 4px var(--color-error-400);
  }

  .select-dropdown__error {
    color: var(--color-error-400);
  }
}
</style>
