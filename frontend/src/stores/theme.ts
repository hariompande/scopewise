import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const isDark = ref(false)

  const toggleTheme = () => {
    isDark.value = !isDark.value
    if (isDark.value) {
      document.documentElement.setAttribute('data-theme', 'dark')
      document.documentElement.classList.add('dark')
      localStorage.setItem('scopeai-theme', 'dark')
    } else {
      document.documentElement.setAttribute('data-theme', 'light')
      document.documentElement.classList.remove('dark')
      localStorage.setItem('scopeai-theme', 'light')
    }
  }

  const setTheme = (dark: boolean) => {
    isDark.value = dark
    if (dark) {
      document.documentElement.setAttribute('data-theme', 'dark')
      document.documentElement.classList.add('dark')
      localStorage.setItem('scopeai-theme', 'dark')
    } else {
      document.documentElement.setAttribute('data-theme', 'light')
      document.documentElement.classList.remove('dark')
      localStorage.setItem('scopeai-theme', 'light')
    }
  }

  const initializeTheme = () => {
    const savedTheme = localStorage.getItem('scopeai-theme')
    if (savedTheme === 'dark') {
      isDark.value = true
      document.documentElement.setAttribute('data-theme', 'dark')
      document.documentElement.classList.add('dark')
    } else if (savedTheme === 'light') {
      isDark.value = false
      document.documentElement.setAttribute('data-theme', 'light')
      document.documentElement.classList.remove('dark')
    } else {
      // Check system preference
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      isDark.value = prefersDark
      document.documentElement.setAttribute('data-theme', prefersDark ? 'dark' : 'light')
      if (prefersDark) {
        document.documentElement.classList.add('dark')
      }
    }
  }

  return {
    isDark,
    toggleTheme,
    setTheme,
    initializeTheme,
  }
})
