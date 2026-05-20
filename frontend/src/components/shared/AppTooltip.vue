<script setup lang="ts">
import { ref, onUnmounted } from 'vue'

interface Props {
  content: string
  position?: 'top' | 'bottom' | 'left' | 'right'
  delay?: number
}

const props = withDefaults(defineProps<Props>(), {
  position: 'top',
  delay: 200,
})

const isVisible = ref(false)
const timeoutId = ref<number | null>(null)

const showTooltip = () => {
  if (timeoutId.value) {
    clearTimeout(timeoutId.value)
  }
  timeoutId.value = window.setTimeout(() => {
    isVisible.value = true
  }, props.delay)
}

const hideTooltip = () => {
  if (timeoutId.value) {
    clearTimeout(timeoutId.value)
  }
  isVisible.value = false
}

onUnmounted(() => {
  if (timeoutId.value) {
    clearTimeout(timeoutId.value)
  }
})
</script>

<template>
  <div
    class="tooltip-wrapper"
    @mouseenter="showTooltip"
    @mouseleave="hideTooltip"
    @focus="showTooltip"
    @blur="hideTooltip"
  >
    <slot />
    <Transition name="tooltip">
      <div
        v-if="isVisible"
        class="tooltip"
        :class="`tooltip--${position}`"
        role="tooltip"
      >
        {{ content }}
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.tooltip-wrapper {
  position: relative;
  display: inline-block;
}

.tooltip {
  position: absolute;
  z-index: var(--z-tooltip);
  padding: var(--space-2) var(--space-3);
  background: var(--color-gray-900);
  color: white;
  font-family: var(--font-body);
  font-size: var(--font-size-body-sm);
  font-weight: var(--font-weight-regular);
  line-height: var(--line-height-normal);
  border-radius: var(--radius-md);
  white-space: nowrap;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  box-shadow: var(--shadow-md);
}

.tooltip--top {
  bottom: calc(100% + var(--space-2));
  left: 50%;
  transform: translateX(-50%);
}

.tooltip--bottom {
  top: calc(100% + var(--space-2));
  left: 50%;
  transform: translateX(-50%);
}

.tooltip--left {
  right: calc(100% + var(--space-2));
  top: 50%;
  transform: translateY(-50%);
}

.tooltip--right {
  left: calc(100% + var(--space-2));
  top: 50%;
  transform: translateY(-50%);
}

.tooltip-enter-active,
.tooltip-leave-active {
  transition: opacity var(--transition-fast), transform var(--transition-fast);
}

.tooltip-enter-from,
.tooltip-leave-to {
  opacity: 0;
}

.tooltip--top.tooltip-enter-from,
.tooltip--top.tooltip-leave-to {
  transform: translateX(-50%) translateY(4px);
}

.tooltip--bottom.tooltip-enter-from,
.tooltip--bottom.tooltip-leave-to {
  transform: translateX(-50%) translateY(-4px);
}

.tooltip--left.tooltip-enter-from,
.tooltip--left.tooltip-leave-to {
  transform: translateY(-50%) translateX(4px);
}

.tooltip--right.tooltip-enter-from,
.tooltip--right.tooltip-leave-to {
  transform: translateY(-50%) translateX(-4px);
}

@media (prefers-color-scheme: dark) {
  .tooltip {
    background: var(--color-gray-100);
    color: var(--color-gray-900);
  }
}
</style>
