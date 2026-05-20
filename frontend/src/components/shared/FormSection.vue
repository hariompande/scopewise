<script setup lang="ts">
interface Props {
  label?: string
  helper?: string
  required?: boolean
}

withDefaults(defineProps<Props>(), {
  label: '',
  helper: '',
  required: false,
})
</script>

<template>
  <div class="form-section">
    <div
      v-if="label"
      class="form-section__header"
    >
      <label class="form-section__label">
        {{ label }}
        <span
          v-if="required"
          class="form-section__required"
        >
          *
        </span>
      </label>
      <p
        v-if="helper"
        class="form-section__helper"
      >
        {{ helper }}
      </p>
    </div>
    <div class="form-section__content">
      <slot />
    </div>
  </div>
</template>

<style scoped>
.form-section {
  margin-bottom: var(--space-6);
}

.form-section__header {
  margin-bottom: var(--space-3);
}

.form-section__label {
  font-family: var(--font-body);
  font-size: var(--font-size-body-sm);
  font-weight: var(--font-weight-medium);
  color: rgba(255, 255, 255, 0.9);
  display: block;
  margin-bottom: var(--space-1);
}

.form-section__required {
  color: #ff6b6b;
  margin-left: 2px;
}

.form-section__helper {
  font-family: var(--font-body);
  font-size: var(--font-size-body-xs);
  color: rgba(255, 255, 255, 0.5);
  margin: 0;
  line-height: var(--line-height-normal);
}

.form-section__content {
  position: relative;
}
</style>
