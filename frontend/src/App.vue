<script setup lang="ts">
import AppNav from './components/shared/AppNav.vue'
import DiscoveryForm from './components/DiscoveryForm.vue'
import ScopeDocumentViewer from './components/ScopeDocumentViewer.vue'
</script>

<template>
  <div class="min-h-screen bg-gray-100 py-8 px-4">
    <div class="max-w-90w mx-auto">
      <AppNav />
      
      <div class="flex gap-4">
        <DiscoveryForm class="w-1/2"/>
        <ScopeDocumentViewer class="w-1/2"/>
      </div>
    </div>
  </div>
</template>
