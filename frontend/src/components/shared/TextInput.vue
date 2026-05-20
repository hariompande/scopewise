<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  modelValue: string
  type?: 'text' | 'email' | 'tel' | 'url' | 'password'
  placeholder?: string
  disabled?: boolean
  readonly?: boolean
  error?: string
  id?: string
  name?: string
  autocomplete?: string
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  placeholder: '',
  disabled: false,
  readonly: false,
  error: '',
  id: '',
  name: '',
  autocomplete: 'off',
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
  focus: [event: FocusEvent]
  blur: [event: FocusEvent]
}>()

const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement
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
  <div class="text-input">
    <input
      :id="inputId"
      :name="name"
      :type="type"
      :value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      :readonly="readonly"
      :autocomplete="autocomplete"
      :aria-invalid="!!error"
      :aria-describedby="error ? `${inputId}-error` : undefined"
      class="text-input__field"
      :class="{
        'text-input__field--error': !!error,
      }"
      @input="handleInput"
      @focus="handleFocus"
      @blur="handleBlur"
    />
    <p
      v-if="error"
      :id="`${inputId}-error`"
      class="text-input__error"
      role="alert"
    >
      {{ error }}
    </p>
  </div>
</template>

<style scoped>
.text-input {
  position: relative;
}

.text-input__field {
  width: 100%;
  padding: var(--space-3) var(--space-4);
  font-family: var(--font-body);
  font-size: var(--font-size-body-md);
  line-height: var(--line-height-normal);
  color: var(--text-primary);
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
  outline: none;
}

.text-input__field::placeholder {
  color: var(--text-tertiary);
}

.text-input__field:hover:not(:disabled) {
  border-color: var(--border-secondary);
}

.text-input__field:focus {
  border-color: var(--color-primary-500);
  box-shadow: var(--shadow-focus);
}

.text-input__field--error {
  border-color: var(--color-error-500);
}

.text-input__field--error:focus {
  border-color: var(--color-error-500);
  box-shadow: 0 0 0 2px var(--bg-primary), 0 0 0 4px var(--color-error-500);
}

.text-input__field:disabled {
  background: var(--bg-secondary);
  color: var(--text-tertiary);
  cursor: not-allowed;
}

.text-input__field:readonly {
  background: var(--bg-secondary);
  cursor: default;
}

.text-input__error {
  font-family: var(--font-body);
  font-size: var(--font-size-body-xs);
  color: var(--color-error-500);
  margin: var(--space-2) 0 0 0;
  line-height: var(--line-height-normal);
}

@media (prefers-color-scheme: dark) {
  .text-input__field {
    border-color: var(--border-primary);
  }

  .text-input__field--error {
    border-color: var(--color-error-400);
  }

  .text-input__field--error:focus {
    border-color: var(--color-error-400);
    box-shadow: 0 0 0 2px var(--bg-primary), 0 0 0 4px var(--color-error-400);
  }

  .text-input__error {
    color: var(--color-error-400);
  }
}
</style>
