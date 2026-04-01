/**
 * WebSocket plugin for Vue app.
 * 
 * Provides global WebSocket connection management.
 */
import { useWebSocket } from '../composables/useWebSocket'

export default {
  install(app) {
    // Create global WebSocket instance
    const ws = useWebSocket()
    
    // Make it available globally
    app.config.globalProperties.$ws = ws
    app.provide('websocket', ws)
    
    // Auto-connect if token is available
    const token = localStorage.getItem('access_token')
    if (token) {
      ws.connect(token)
    }
  }
}
