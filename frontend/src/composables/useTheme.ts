import { ref, watch, onMounted } from 'vue'

type Theme = 'light' | 'dark'

const THEME_KEY = 'scopeai-theme'
const theme = ref<Theme>('light')

export function useTheme() {
  const isDark = ref(false)

  const applyTheme = (newTheme: Theme) => {
    theme.value = newTheme
    isDark.value = newTheme === 'dark'
    
    if (typeof document !== 'undefined') {
      document.documentElement.setAttribute('data-theme', newTheme)
      if (newTheme === 'dark') {
        document.documentElement.classList.add('dark')
      } else {
        document.documentElement.classList.remove('dark')
      }
      localStorage.setItem(THEME_KEY, newTheme)
    }
  }

  const toggleTheme = () => {
    const newTheme = theme.value === 'light' ? 'dark' : 'light'
    applyTheme(newTheme)
  }

  const setTheme = (newTheme: Theme) => {
    applyTheme(newTheme)
  }

  onMounted(() => {
    // Check localStorage or system preference
    const savedTheme = localStorage.getItem(THEME_KEY) as Theme | null
    
    if (savedTheme) {
      applyTheme(savedTheme)
    } else {
      // Check system preference
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      applyTheme(prefersDark ? 'dark' : 'light')
    }
  })

  // Watch for system preference changes
  if (typeof window !== 'undefined') {
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      if (!localStorage.getItem(THEME_KEY)) {
        applyTheme(e.matches ? 'dark' : 'light')
      }
    })
  }

  return {
    theme,
    isDark,
    toggleTheme,
    setTheme,
  }
}
