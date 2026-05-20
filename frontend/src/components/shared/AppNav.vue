<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
</script>

<template>
  <nav class="app-nav">
    <h1 class="app-title">{{ t('app.title') }}</h1>
  </nav>
</template>

<style scoped>
.app-nav {
  text-align: center;
  margin-bottom: var(--space-8);
  padding: var(--space-4) 0;
}

.app-title {
  font-family: var(--font-heading);
  font-size: var(--font-size-heading-xl);
  font-weight: var(--font-weight-bold);
  color: #ffffff;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin: 0;
  text-shadow: 0 0 40px rgba(255, 255, 255, 0.3);
}
</style>
