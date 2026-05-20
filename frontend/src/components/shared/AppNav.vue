<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
</script>

<template>
  <nav class="text-center mb-8 ">
    <h1 class="text-4xl font-bold text-gray-800 mb-2 uppercase tracking-wide">{{ t('app.title') }}</h1>
  </nav>
</template>
