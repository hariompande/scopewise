<script setup lang="ts">
interface Props {
  size?: 'sm' | 'md' | 'lg'
  color?: 'primary' | 'secondary'
}

withDefaults(defineProps<Props>(), {
  size: 'md',
  color: 'primary',
})
</script>

<template>
  <div
    class="loading-spinner"
    :class="`loading-spinner--${size} loading-spinner--${color}`"
    role="status"
    aria-label="Loading"
  >
    <svg
      class="loading-spinner__svg"
      viewBox="0 0 50 50"
    >
      <circle
        class="loading-spinner__circle"
        cx="25"
        cy="25"
        r="20"
        fill="none"
        stroke-width="4"
      />
    </svg>
  </div>
</template>

<style scoped>
.loading-spinner {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.loading-spinner--sm {
  width: 16px;
  height: 16px;
}

.loading-spinner--md {
  width: 24px;
  height: 24px;
}

.loading-spinner--lg {
  width: 32px;
  height: 32px;
}

.loading-spinner__svg {
  width: 100%;
  height: 100%;
  animation: rotate 1.5s linear infinite;
}

.loading-spinner__circle {
  stroke: var(--color-primary-500);
  stroke-dasharray: 90, 150;
  stroke-dashoffset: 0;
  stroke-linecap: round;
  animation: dash 1.5s ease-in-out infinite;
}

.loading-spinner--secondary .loading-spinner__circle {
  stroke: var(--text-tertiary);
}

@keyframes rotate {
  100% {
    transform: rotate(360deg);
  }
}

@keyframes dash {
  0% {
    stroke-dasharray: 1, 200;
    stroke-dashoffset: 0;
  }
  50% {
    stroke-dasharray: 90, 150;
    stroke-dashoffset: -35;
  }
  100% {
    stroke-dasharray: 90, 150;
    stroke-dashoffset: -124;
  }
}

@media (prefers-color-scheme: dark) {
  .loading-spinner__circle {
    stroke: var(--color-primary-400);
  }
}
</style>
