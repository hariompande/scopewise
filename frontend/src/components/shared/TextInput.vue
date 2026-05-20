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
  color: #ffffff;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  transition: all 0.3s ease;
  outline: none;
  backdrop-filter: blur(10px);
}

.text-input__field::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.text-input__field:hover:not(:disabled) {
  border-color: rgba(255, 255, 255, 0.25);
  background: rgba(0, 0, 0, 0.4);
}

.text-input__field:focus {
  border-color: rgba(255, 255, 255, 0.4);
  box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.1);
}

.text-input__field--error {
  border-color: rgba(255, 107, 107, 0.5);
}

.text-input__field--error:focus {
  border-color: #ff6b6b;
  box-shadow: 0 0 0 2px rgba(255, 107, 107, 0.2);
}

.text-input__field:disabled {
  background: rgba(0, 0, 0, 0.2);
  color: rgba(255, 255, 255, 0.3);
  cursor: not-allowed;
}

.text-input__field:readonly {
  background: rgba(0, 0, 0, 0.2);
  cursor: default;
}

.text-input__error {
  font-family: var(--font-body);
  font-size: var(--font-size-body-xs);
  color: #ff6b6b;
  margin: var(--space-2) 0 0 0;
  line-height: var(--line-height-normal);
}
</style>
