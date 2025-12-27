import { defineStore } from 'pinia'
import { usersAPI } from '../services/api'

export const useSidebarStore = defineStore('sidebar', {
  state: () => ({
    items: [],
    loading: false,
    error: null,
    lastFetched: null,
  }),
  actions: {
    async fetchSidebarItems() {
      this.loading = true
      this.error = null
      try {
        const response = await usersAPI.sidebarItems()
        this.items = response.data.items || []
        this.lastFetched = new Date()
        return this.items
      } catch (error) {
        this.error = error.response?.data?.detail || error.message || 'Failed to load sidebar items'
        console.error('Failed to fetch sidebar items:', error)
        // Return empty array on error to prevent breaking the UI
        this.items = []
        return []
      } finally {
        this.loading = false
      }
    },
    clearSidebarItems() {
      this.items = []
      this.lastFetched = null
    },
  },
  getters: {
    hasItems: (state) => state.items.length > 0,
    // Get items that should be visible (no children or has accessible children)
    visibleItems: (state) => {
      return state.items.filter(item => {
        // If item has children, only show if at least one child is accessible
        if (item.children && item.children.length > 0) {
          return true // Children filtering is done in the component
        }
        // If no children, show the item
        return true
      })
    },
  },
})

