<script setup lang="ts">
interface Props {
  title: string
  subtitle?: string
  actions?: boolean
}

withDefaults(defineProps<Props>(), {
  subtitle: '',
  actions: false,
})
</script>

<template>
  <header class="page-header">
    <div class="page-header__content">
      <h1 class="page-header__title">
        {{ title }}
      </h1>
      <p
        v-if="subtitle"
        class="page-header__subtitle"
      >
        {{ subtitle }}
      </p>
    </div>
    <div
      v-if="actions"
      class="page-header__actions"
    >
      <slot name="actions" />
    </div>
  </header>
</template>

<style scoped>
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-6);
  margin-bottom: var(--space-8);
}

.page-header__content {
  flex: 1;
}

.page-header__title {
  font-family: var(--font-heading);
  font-size: var(--font-size-heading-2xl);
  font-weight: var(--font-weight-semibold);
  color: #ffffff;
  line-height: var(--line-height-tight);
  margin: 0 0 var(--space-2) 0;
  letter-spacing: -0.02em;
}

.page-header__subtitle {
  font-family: var(--font-body);
  font-size: var(--font-size-body-lg);
  color: rgba(255, 255, 255, 0.6);
  margin: 0;
  line-height: var(--line-height-normal);
}

.page-header__actions {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  flex-shrink: 0;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: var(--space-4);
  }

  .page-header__actions {
    width: 100%;
    justify-content: flex-start;
  }
}
</style>
