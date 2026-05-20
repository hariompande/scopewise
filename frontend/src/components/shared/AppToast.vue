<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

type ToastType = 'success' | 'error' | 'warning' | 'info'

interface Props {
  type?: ToastType
  title?: string
  message: string
  duration?: number
  closable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  type: 'info',
  title: '',
  duration: 5000,
  closable: true,
})

const emit = defineEmits<{
  close: []
}>()

const isVisible = ref(false)
let timeoutId: number | null = null

onMounted(() => {
  // Trigger animation
  requestAnimationFrame(() => {
    isVisible.value = true
  })

  // Auto-dismiss
  if (props.duration > 0) {
    timeoutId = window.setTimeout(() => {
      handleClose()
    }, props.duration)
  }
})

onUnmounted(() => {
  if (timeoutId) {
    clearTimeout(timeoutId)
  }
})

const handleClose = () => {
  isVisible.value = false
  setTimeout(() => {
    emit('close')
  }, 200)
}

const getIcon = () => {
  switch (props.type) {
    case 'success':
      return '✓'
    case 'error':
      return '✕'
    case 'warning':
      return '⚠'
    case 'info':
    default:
      return 'ℹ'
  }
}
</script>

<template>
  <Transition name="toast">
    <div
      v-if="isVisible"
      class="app-toast"
      :class="`app-toast--${type}`"
      role="alert"
      :aria-live="type === 'error' ? 'assertive' : 'polite'"
    >
      <div class="app-toast__icon">
        {{ getIcon() }}
      </div>
      <div class="app-toast__content">
        <h4
          v-if="title"
          class="app-toast__title"
        >
          {{ title }}
        </h4>
        <p class="app-toast__message">
          {{ message }}
        </p>
      </div>
      <button
        v-if="closable"
        class="app-toast__close"
        @click="handleClose"
        aria-label="Close notification"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path d="M18 6 6 18" />
          <path d="m6 6 12 12" />
        </svg>
      </button>
    </div>
  </Transition>
</template>

<style scoped>
.app-toast {
  position: fixed;
  top: var(--space-6);
  right: var(--space-6);
  max-width: 400px;
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  padding: var(--space-4);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  z-index: var(--z-toast);
  background: var(--bg-elevated);
  border: 1px solid var(--border-primary);
}

.app-toast--success {
  border-left: 3px solid var(--color-success-500);
}

.app-toast--error {
  border-left: 3px solid var(--color-error-500);
}

.app-toast--warning {
  border-left: 3px solid var(--color-warning-500);
}

.app-toast--info {
  border-left: 3px solid var(--color-info-500);
}

.app-toast__icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: var(--font-weight-bold);
  font-size: var(--font-size-body-sm);
}

.app-toast--success .app-toast__icon {
  color: var(--color-success-500);
  background: var(--color-success-50);
  border-radius: var(--radius-full);
}

.app-toast--error .app-toast__icon {
  color: var(--color-error-500);
  background: var(--color-error-50);
  border-radius: var(--radius-full);
}

.app-toast--warning .app-toast__icon {
  color: var(--color-warning-500);
  background: var(--color-warning-50);
  border-radius: var(--radius-full);
}

.app-toast--info .app-toast__icon {
  color: var(--color-info-500);
  background: var(--color-info-50);
  border-radius: var(--radius-full);
}

.app-toast__content {
  flex: 1;
  min-width: 0;
}

.app-toast__title {
  font-family: var(--font-body);
  font-size: var(--font-size-body-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
  margin: 0 0 var(--space-1) 0;
}

.app-toast__message {
  font-family: var(--font-body);
  font-size: var(--font-size-body-sm);
  color: var(--text-secondary);
  margin: 0;
  line-height: var(--line-height-normal);
}

.app-toast__close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border: none;
  background: transparent;
  color: var(--text-tertiary);
  cursor: pointer;
  border-radius: var(--radius-sm);
  flex-shrink: 0;
  transition: background var(--transition-fast), color var(--transition-fast);
}

.app-toast__close:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.app-toast__close:focus-visible {
  outline: none;
  box-shadow: var(--focus-ring);
}

.toast-enter-active,
.toast-leave-active {
  transition: transform var(--transition-normal), opacity var(--transition-normal);
}

.toast-enter-from,
.toast-leave-to {
  transform: translateX(100%);
  opacity: 0;
}

@media (prefers-color-scheme: dark) {
  .app-toast--success .app-toast__icon {
    color: var(--color-success-400);
    background: rgba(16, 185, 129, 0.2);
  }

  .app-toast--error .app-toast__icon {
    color: var(--color-error-400);
    background: rgba(239, 68, 68, 0.2);
  }

  .app-toast--warning .app-toast__icon {
    color: var(--color-warning-400);
    background: rgba(245, 158, 11, 0.2);
  }

  .app-toast--info .app-toast__icon {
    color: var(--color-info-400);
    background: rgba(59, 130, 246, 0.2);
  }
}
</style>
