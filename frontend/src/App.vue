<script setup lang="ts">
import { storeToRefs } from 'pinia'
import AppNav from './components/shared/AppNav.vue'
import DiscoveryForm from './components/DiscoveryForm.vue'
import ScopeDocumentViewer from './components/ScopeDocumentViewer.vue'
import { useDiscoveryStore } from './stores/discovery'

const discoveryStore = useDiscoveryStore()
const { scopeDocument, isStreaming } = storeToRefs(discoveryStore)

const hasScopeDocument = computed(() => !!scopeDocument.value || isStreaming.value)
</script>

<template>
  <div class="app-wrapper">
    <div class="app-container">
      <AppNav />

      <div class="main-layout" :class="{ 'main-layout--split': hasScopeDocument }">
        <DiscoveryForm class="discovery-form-container" :class="{ 'discovery-form-container--centered': !hasScopeDocument }" />
        <Transition name="slide-from-right">
          <ScopeDocumentViewer v-if="hasScopeDocument" class="scope-viewer-container" />
        </Transition>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { computed } from 'vue'
</script>

<style>
/* Global dark theme base with grid background */
.app-wrapper {
  min-height: 100vh;
  background:
    linear-gradient(135deg, rgba(10, 10, 10, 0.97) 0%, rgba(26, 26, 26, 0.97) 50%, rgba(15, 15, 15, 0.97) 100%),
    linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
  background-size: 100% 100%, 40px 40px, 40px 40px;
  background-position: 0 0, 0 0, 0 0;
  padding: var(--space-8);
  position: relative;
}

/* Animated grid glow effect */
.app-wrapper::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background:
    radial-gradient(circle at 20% 80%, rgba(255, 255, 255, 0.03) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.03) 0%, transparent 50%);
  pointer-events: none;
  z-index: 0;
}

.app-container {
  max-width: 1400px;
  margin: 0 auto;
  position: relative;
  z-index: 1;
}

.main-layout {
  display: flex;
  gap: var(--space-6);
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.discovery-form-container {
  flex: 1;
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.discovery-form-container--centered {
  max-width: 800px;
  margin: 0 auto;
}

.scope-viewer-container {
  flex: 1;
  min-width: 0;
}

/* Slide from right animation */
.slide-from-right-enter-active,
.slide-from-right-leave-active {
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-from-right-enter-from {
  opacity: 0;
  transform: translateX(50px);
}

.slide-from-right-enter-to {
  opacity: 1;
  transform: translateX(0);
}

.slide-from-right-leave-from {
  opacity: 1;
  transform: translateX(0);
}

.slide-from-right-leave-to {
  opacity: 0;
  transform: translateX(50px);
}

/* Responsive adjustments */
@media (max-width: 1024px) {
  .main-layout--split {
    flex-direction: column;
  }

  .scope-viewer-container {
    order: -1;
  }

  .slide-from-right-enter-from,
  .slide-from-right-leave-to {
    transform: translateY(-30px);
  }
}

@media (max-width: 640px) {
  .app-wrapper {
    padding: var(--space-4);
  }
}
</style>
