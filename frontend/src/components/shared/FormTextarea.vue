<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  modelValue: string
  placeholder?: string
  disabled?: boolean
  readonly?: boolean
  error?: string
  id?: string
  name?: string
  rows?: number
  resize?: 'none' | 'vertical' | 'horizontal' | 'both'
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: '',
  disabled: false,
  readonly: false,
  error: '',
  id: '',
  name: '',
  rows: 4,
  resize: 'vertical',
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
  focus: [event: FocusEvent]
  blur: [event: FocusEvent]
}>()

const handleInput = (event: Event) => {
  const target = event.target as HTMLTextAreaElement
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
  <div class="textarea">
    <textarea
      :id="inputId"
      :name="name"
      :value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      :readonly="readonly"
      :rows="rows"
      :aria-invalid="!!error"
      :aria-describedby="error ? `${inputId}-error` : undefined"
      class="textarea__field"
      :class="{
        'textarea__field--error': !!error,
      }"
      :style="{ resize }"
      @input="handleInput"
      @focus="handleFocus"
      @blur="handleBlur"
    />
    <p
      v-if="error"
      :id="`${inputId}-error`"
      class="textarea__error"
      role="alert"
    >
      {{ error }}
    </p>
  </div>
</template>

<style scoped>
.textarea {
  position: relative;
}

.textarea__field {
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

.textarea__field::placeholder {
  color: var(--text-tertiary);
}

.textarea__field:hover:not(:disabled) {
  border-color: var(--border-secondary);
}

.textarea__field:focus {
  border-color: var(--color-primary-500);
  box-shadow: var(--shadow-focus);
}

.textarea__field--error {
  border-color: var(--color-error-500);
}

.textarea__field--error:focus {
  border-color: var(--color-error-500);
  box-shadow: 0 0 0 2px var(--bg-primary), 0 0 0 4px var(--color-error-500);
}

.textarea__field:disabled {
  background: var(--bg-secondary);
  color: var(--text-tertiary);
  cursor: not-allowed;
  resize: none;
}

.textarea__field:readonly {
  background: var(--bg-secondary);
  cursor: default;
}

.textarea__error {
  font-family: var(--font-body);
  font-size: var(--font-size-body-xs);
  color: var(--color-error-500);
  margin: var(--space-2) 0 0 0;
  line-height: var(--line-height-normal);
}

@media (prefers-color-scheme: dark) {
  .textarea__field--error {
    border-color: var(--color-error-400);
  }

  .textarea__field--error:focus {
    border-color: var(--color-error-400);
    box-shadow: 0 0 0 2px var(--bg-primary), 0 0 0 4px var(--color-error-400);
  }

  .textarea__error {
    color: var(--color-error-400);
  }
}
</style>
