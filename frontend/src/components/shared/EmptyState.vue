<script setup lang="ts">
interface Props {
  icon?: string
  title: string
  message: string
  actionLabel?: string
}

defineProps<Props>()

const emit = defineEmits<{
  action: []
}>()

const handleAction = () => {
  emit('action')
}
</script>

<template>
  <div class="empty-state">
    <div
      v-if="icon"
      class="empty-state__icon"
    >
      <component :is="icon" />
    </div>
    <div
      v-else
      class="empty-state__icon-placeholder"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="48"
        height="48"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="1.5"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <circle cx="12" cy="12" r="10" />
        <path d="M12 8v4" />
        <path d="M12 16h.01" />
      </svg>
    </div>
    <h3 class="empty-state__title">
      {{ title }}
    </h3>
    <p class="empty-state__message">
      {{ message }}
    </p>
    <button
      v-if="actionLabel"
      class="empty-state__action"
      @click="handleAction"
    >
      {{ actionLabel }}
    </button>
  </div>
</template>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-12) var(--space-6);
  text-align: center;
}

.empty-state__icon,
.empty-state__icon-placeholder {
  width: 48px;
  height: 48px;
  margin-bottom: var(--space-6);
  color: var(--text-tertiary);
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-state__title {
  font-family: var(--font-heading);
  font-size: var(--font-size-heading-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
  margin: 0 0 var(--space-2) 0;
}

.empty-state__message {
  font-family: var(--font-body);
  font-size: var(--font-size-body-md);
  color: var(--text-secondary);
  margin: 0 0 var(--space-6) 0;
  max-width: 400px;
}

.empty-state__action {
  font-family: var(--font-body);
  font-size: var(--font-size-body-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-primary-600);
  background: var(--color-primary-50);
  border: 1px solid var(--color-primary-200);
  padding: var(--space-3) var(--space-6);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background var(--transition-fast), border-color var(--transition-fast);
}

.empty-state__action:hover {
  background: var(--color-primary-100);
  border-color: var(--color-primary-300);
}

.empty-state__action:focus-visible {
  outline: none;
  box-shadow: var(--focus-ring);
}

@media (prefers-color-scheme: dark) {
  .empty-state__action {
    color: var(--color-primary-300);
    background: rgba(72, 101, 129, 0.2);
    border-color: rgba(72, 101, 129, 0.3);
  }

  .empty-state__action:hover {
    background: rgba(72, 101, 129, 0.3);
    border-color: rgba(72, 101, 129, 0.4);
  }
}
</style>
