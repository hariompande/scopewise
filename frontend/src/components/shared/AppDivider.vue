<script setup lang="ts">
interface Props {
  label?: string
  orientation?: 'horizontal' | 'vertical'
}

withDefaults(defineProps<Props>(), {
  label: '',
  orientation: 'horizontal',
})
</script>

<template>
  <div
    class="app-divider"
    :class="`app-divider--${orientation}`"
    role="separator"
    :aria-orientation="orientation"
  >
    <span
      v-if="label"
      class="app-divider__label"
    >
      {{ label }}
    </span>
  </div>
</template>

<style scoped>
.app-divider {
  border: none;
  position: relative;
}

.app-divider--horizontal {
  width: 100%;
  height: 1px;
  background: var(--border-primary);
  margin: var(--space-6) 0;
}

.app-divider--horizontal.app-divider--with-label {
  display: flex;
  align-items: center;
}

.app-divider__label {
  font-family: var(--font-body);
  font-size: var(--font-size-body-sm);
  font-weight: var(--font-weight-medium);
  color: var(--text-tertiary);
  background: var(--bg-primary);
  padding: 0 var(--space-3);
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  top: 50%;
  margin-top: -0.5em;
}

.app-divider--vertical {
  width: 1px;
  height: 100%;
  background: var(--border-primary);
  margin: 0 var(--space-6);
}
</style>
