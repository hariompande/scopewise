<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  src?: string
  alt?: string
  name?: string
  size?: 'sm' | 'md' | 'lg' | 'xl'
}

const props = withDefaults(defineProps<Props>(), {
  alt: '',
  name: '',
  size: 'md',
})

const initials = computed(() => {
  if (!props.name) return ''
  return props.name
    .split(' ')
    .map(n => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
})

const hasImage = computed(() => !!props.src)
</script>

<template>
  <div
    class="avatar"
    :class="`avatar--${size}`"
  >
    <img
      v-if="hasImage"
      :src="src"
      :alt="alt || name"
      class="avatar__image"
    />
    <span
      v-else-if="initials"
      class="avatar__initials"
    >
      {{ initials }}
    </span>
    <svg
      v-else
      class="avatar__placeholder"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
    >
      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
      <circle cx="12" cy="7" r="4" />
    </svg>
  </div>
</template>

<style scoped>
.avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-full);
  background: var(--bg-secondary);
  border: 2px solid var(--border-primary);
  overflow: hidden;
  flex-shrink: 0;
}

.avatar--sm {
  width: 24px;
  height: 24px;
}

.avatar--md {
  width: 32px;
  height: 32px;
}

.avatar--lg {
  width: 40px;
  height: 40px;
}

.avatar--xl {
  width: 56px;
  height: 56px;
}

.avatar__image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar__initials {
  font-family: var(--font-body);
  font-size: var(--font-size-body-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
}

.avatar--sm .avatar__initials {
  font-size: var(--font-size-body-xs);
}

.avatar--xl .avatar__initials {
  font-size: var(--font-size-body-md);
}

.avatar__placeholder {
  width: 60%;
  height: 60%;
  color: var(--text-tertiary);
}
</style>
