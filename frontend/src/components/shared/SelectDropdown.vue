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
  color: #ffffff;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  transition: all 0.3s ease;
  outline: none;
  appearance: none;
  cursor: pointer;
  backdrop-filter: blur(10px);
}

.select-dropdown__field--placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.select-dropdown__field:hover:not(:disabled) {
  border-color: rgba(255, 255, 255, 0.25);
  background: rgba(0, 0, 0, 0.4);
}

.select-dropdown__field:focus {
  border-color: rgba(255, 255, 255, 0.4);
  box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.1);
}

.select-dropdown__field--error {
  border-color: rgba(255, 107, 107, 0.5);
}

.select-dropdown__field--error:focus {
  border-color: #ff6b6b;
  box-shadow: 0 0 0 2px rgba(255, 107, 107, 0.2);
}

.select-dropdown__field:disabled {
  background: rgba(0, 0, 0, 0.2);
  color: rgba(255, 255, 255, 0.3);
  cursor: not-allowed;
}

/* Style the dropdown options */
.select-dropdown__field option {
  background: #1a1a1a;
  color: #ffffff;
}

.select-dropdown__field option:hover,
.select-dropdown__field option:focus {
  background: #2a2a2a;
}

.select-dropdown__icon {
  position: absolute;
  right: var(--space-4);
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
  color: rgba(255, 255, 255, 0.5);
}

.select-dropdown__error {
  font-family: var(--font-body);
  font-size: var(--font-size-body-xs);
  color: #ff6b6b;
  margin: var(--space-2) 0 0 0;
  line-height: var(--line-height-normal);
}
</style>
