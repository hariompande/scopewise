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
  color: #ffffff;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  transition: all 0.3s ease;
  outline: none;
  backdrop-filter: blur(10px);
}

.textarea__field::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.textarea__field:hover:not(:disabled) {
  border-color: rgba(255, 255, 255, 0.25);
  background: rgba(0, 0, 0, 0.4);
}

.textarea__field:focus {
  border-color: rgba(255, 255, 255, 0.4);
  box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.1);
}

.textarea__field--error {
  border-color: rgba(255, 107, 107, 0.5);
}

.textarea__field--error:focus {
  border-color: #ff6b6b;
  box-shadow: 0 0 0 2px rgba(255, 107, 107, 0.2);
}

.textarea__field:disabled {
  background: rgba(0, 0, 0, 0.2);
  color: rgba(255, 255, 255, 0.3);
  cursor: not-allowed;
  resize: none;
}

.textarea__field:readonly {
  background: rgba(0, 0, 0, 0.2);
  cursor: default;
}

.textarea__error {
  font-family: var(--font-body);
  font-size: var(--font-size-body-xs);
  color: #ff6b6b;
  margin: var(--space-2) 0 0 0;
  line-height: var(--line-height-normal);
}
</style>
