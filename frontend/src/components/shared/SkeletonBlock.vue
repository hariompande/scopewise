<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  width?: string | number
  height?: string | number
  variant?: 'text' | 'rectangular' | 'circular'
  animation?: 'pulse' | 'wave' | 'none'
}

const props = withDefaults(defineProps<Props>(), {
  width: '100%',
  height: '1em',
  variant: 'text',
  animation: 'pulse',
})

const style = computed(() => ({
  width: typeof props.width === 'number' ? `${props.width}px` : props.width,
  height: typeof props.height === 'number' ? `${props.height}px` : props.height,
}))
</script>

<template>
  <div
    class="skeleton-block"
    :class="`skeleton-block--${variant} skeleton-block--${animation}`"
    :style="style"
    role="status"
    aria-label="Loading content"
  />
</template>

<style scoped>
.skeleton-block {
  background: var(--color-gray-200);
  display: inline-block;
}

.skeleton-block--text {
  border-radius: var(--radius-sm);
}

.skeleton-block--rectangular {
  border-radius: var(--radius-md);
}

.skeleton-block--circular {
  border-radius: var(--radius-full);
}

.skeleton-block--pulse {
  animation: pulse 1.5s ease-in-out 0.5s infinite;
}

.skeleton-block--wave {
  position: relative;
  overflow: hidden;
}

.skeleton-block--wave::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.4),
    transparent
  );
  transform: translateX(-100%);
  animation: wave 1.5s infinite;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

@keyframes wave {
  100% {
    transform: translateX(100%);
  }
}

@media (prefers-color-scheme: dark) {
  .skeleton-block {
    background: var(--color-gray-700);
  }

  .skeleton-block--wave::after {
    background: linear-gradient(
      90deg,
      transparent,
      rgba(255, 255, 255, 0.1),
      transparent
    );
  }
}
</style>
