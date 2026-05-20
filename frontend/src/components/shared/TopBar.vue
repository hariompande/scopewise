<script setup lang="ts">
import { ref } from 'vue'
import { useThemeStore } from '@/stores/theme'

interface Props {
  logo?: string
  userName?: string
  userAvatar?: string
  notificationCount?: number
}

withDefaults(defineProps<Props>(), {
  logo: 'ScopeAI',
  userName: '',
  userAvatar: '',
  notificationCount: 0,
})

const emit = defineEmits<{
  notificationClick: []
  profileClick: []
  themeToggle: []
}>()

const themeStore = useThemeStore()
const showNotifications = ref(false)

const handleNotificationClick = () => {
  showNotifications.value = !showNotifications.value
  emit('notificationClick')
}

const handleProfileClick = () => {
  emit('profileClick')
}

const handleThemeToggle = () => {
  themeStore.toggleTheme()
  emit('themeToggle')
}

const getInitials = (name: string) => {
  return name
    .split(' ')
    .map(n => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}
</script>

<template>
  <header
    class="topbar"
    role="banner"
  >
    <div class="topbar__left">
      <div class="topbar__logo">
        {{ logo }}
      </div>
    </div>

    <div class="topbar__right">
      <!-- Theme Toggle -->
      <button
        class="topbar__icon-button"
        @click="handleThemeToggle"
        aria-label="Toggle theme"
        :aria-pressed="themeStore.isDark"
      >
        <svg
          v-if="!themeStore.isDark"
          xmlns="http://www.w3.org/2000/svg"
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z" />
        </svg>
        <svg
          v-else
          xmlns="http://www.w3.org/2000/svg"
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <circle cx="12" cy="12" r="4" />
          <path d="M12 2v2" />
          <path d="M12 20v2" />
          <path d="m4.93 4.93 1.41 1.41" />
          <path d="m17.66 17.66 1.41 1.41" />
          <path d="M2 12h2" />
          <path d="M20 12h2" />
          <path d="m6.34 17.66-1.41 1.41" />
          <path d="m19.07 4.93-1.41 1.41" />
        </svg>
      </button>

      <!-- Notifications -->
      <button
        class="topbar__icon-button topbar__icon-button--notification"
        @click="handleNotificationClick"
        aria-label="Notifications"
        :aria-expanded="showNotifications"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9" />
          <path d="M10.3 21a1.94 1.94 0 0 0 3.4 0" />
        </svg>
        <span
          v-if="notificationCount > 0"
          class="topbar__notification-badge"
        >
          {{ notificationCount > 9 ? '9+' : notificationCount }}
        </span>
      </button>

      <!-- User Avatar -->
      <button
        class="topbar__avatar-button"
        @click="handleProfileClick"
        aria-label="User profile"
      >
        <img
          v-if="userAvatar"
          :src="userAvatar"
          :alt="userName"
          class="topbar__avatar"
        />
        <span
          v-else-if="userName"
          class="topbar__avatar-initials"
        >
          {{ getInitials(userName) }}
        </span>
        <svg
          v-else
          xmlns="http://www.w3.org/2000/svg"
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="topbar__avatar-placeholder"
        >
          <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2" />
          <circle cx="12" cy="7" r="4" />
        </svg>
      </button>
    </div>
  </header>
</template>

<style scoped>
.topbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: var(--topbar-height);
  background: var(--bg-elevated);
  border-bottom: 1px solid var(--border-primary);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--space-6);
  z-index: var(--z-fixed);
}

.topbar__left {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.topbar__logo {
  font-family: var(--font-display);
  font-size: var(--font-size-heading-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-primary-600);
  letter-spacing: var(--letter-spacing-tight);
}

.topbar__right {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.topbar__icon-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: none;
  background: transparent;
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  cursor: pointer;
  transition: background var(--transition-fast), color var(--transition-fast);
  position: relative;
}

.topbar__icon-button:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.topbar__icon-button:focus-visible {
  outline: none;
  box-shadow: var(--focus-ring);
}

.topbar__icon-button--notification {
  margin-right: var(--space-2);
}

.topbar__notification-badge {
  position: absolute;
  top: 4px;
  right: 4px;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  background: var(--color-error-500);
  color: white;
  font-size: var(--font-size-body-xs);
  font-weight: var(--font-weight-semibold);
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
}

.topbar__avatar-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: 2px solid var(--border-primary);
  border-radius: var(--radius-full);
  background: var(--bg-secondary);
  cursor: pointer;
  overflow: hidden;
  transition: border-color var(--transition-fast);
}

.topbar__avatar-button:hover {
  border-color: var(--border-secondary);
}

.topbar__avatar-button:focus-visible {
  outline: none;
  box-shadow: var(--focus-ring);
}

.topbar__avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.topbar__avatar-initials {
  font-family: var(--font-body);
  font-size: var(--font-size-body-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
}

.topbar__avatar-placeholder {
  color: var(--text-tertiary);
}

@media (prefers-color-scheme: dark) {
  .topbar__logo {
    color: var(--color-primary-400);
  }
}
</style>
