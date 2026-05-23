import { defineStore } from 'pinia'

const THEME_STORAGE_KEY = 'pixelcast-signage_theme'
const VALID_PREFERENCES = ['system', 'light', 'dark']

export const useThemeStore = defineStore('theme', {
  state: () => ({
    // Resolved theme applied to the DOM: 'dark' | 'light'
    theme: 'dark',
    // User preference: 'system' | 'dark' | 'light'
    preference: 'system',
    _mediaQueryList: null,
    _mediaQueryListener: null,
  }),

  getters: {
    /**
     * Check if dark mode is active
     */
    isDarkMode() {
      return this.theme === 'dark'
    },
  },

  actions: {
    _getSystemTheme() {
      if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        return 'dark'
      }
      return 'light'
    },

    _normalizeStoredPreference(raw) {
      if (!raw) return null
      if (VALID_PREFERENCES.includes(raw)) return raw

      // Backward compatibility: if an object was stored in earlier experiments.
      try {
        const parsed = JSON.parse(raw)
        const pref = parsed?.preference
        if (VALID_PREFERENCES.includes(pref)) return pref
      } catch {
        // no-op: legacy string format is handled above
      }
      return null
    },

    _applyResolvedTheme(theme) {
      this.theme = theme
      document.documentElement.classList.toggle('dark', theme === 'dark')
    },

    _teardownSystemListener() {
      if (!this._mediaQueryList || !this._mediaQueryListener) return

      if (typeof this._mediaQueryList.removeEventListener === 'function') {
        this._mediaQueryList.removeEventListener('change', this._mediaQueryListener)
      } else if (typeof this._mediaQueryList.removeListener === 'function') {
        this._mediaQueryList.removeListener(this._mediaQueryListener)
      }

      this._mediaQueryList = null
      this._mediaQueryListener = null
    },

    _setupSystemListener() {
      this._teardownSystemListener()
      if (!window.matchMedia) return

      const mql = window.matchMedia('(prefers-color-scheme: dark)')
      const listener = () => {
        if (this.preference !== 'system') return
        this._applyResolvedTheme(mql.matches ? 'dark' : 'light')
      }

      if (typeof mql.addEventListener === 'function') {
        mql.addEventListener('change', listener)
      } else if (typeof mql.addListener === 'function') {
        mql.addListener(listener)
      }

      this._mediaQueryList = mql
      this._mediaQueryListener = listener
    },

    /**
     * Initialize theme on app startup
     * Reads from localStorage or detects system preference
     */
    initTheme() {
      const storedValue = localStorage.getItem(THEME_STORAGE_KEY)
      const preference = this._normalizeStoredPreference(storedValue) || 'system'
      this.setPreference(preference)
    },

    /**
     * Set theme preference and update DOM
     */
    setPreference(preference) {
      if (!VALID_PREFERENCES.includes(preference)) {
        console.warn(`Invalid theme preference: ${preference}. Using 'system' as fallback.`)
        preference = 'system'
      }

      this.preference = preference
      localStorage.setItem(THEME_STORAGE_KEY, preference)

      if (preference === 'system') {
        this._applyResolvedTheme(this._getSystemTheme())
        this._setupSystemListener()
      } else {
        this._teardownSystemListener()
        this._applyResolvedTheme(preference)
      }
    },

    /**
     * Backward compatible API: explicit light/dark assignment.
     */
    setTheme(theme) {
      if (theme !== 'dark' && theme !== 'light') {
        console.warn(`Invalid theme: ${theme}. Using 'dark' as fallback.`)
        this.setPreference('dark')
        return
      }
      this.setPreference(theme)
    },

    /**
     * Toggle between dark and light theme
     */
    toggleTheme() {
      this.setTheme(this.theme === 'dark' ? 'light' : 'dark')
    },
  },
})

