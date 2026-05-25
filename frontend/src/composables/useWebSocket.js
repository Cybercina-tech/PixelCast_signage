/**
 * Singleton WebSocket client for dashboard real-time updates.
 */
import { ref } from 'vue'
import { isDockerServiceHostname } from '@/utils/apiBaseUrl'

const RECONNECT_DELAY_MS = 1000
const MAX_RECONNECT_DELAY_MS = 30000
const MAX_RECONNECT_ATTEMPTS = 18
const PING_INTERVAL_MS = 30000
/** Refresh access token when exp within this many seconds */
const TOKEN_REFRESH_LEEWAY_SEC = 120

/** Server/custom close codes (dashboard_consumer) */
const WS_CLOSE_NORMAL = 1000
const WS_CLOSE_AUTH = 4001
const WS_CLOSE_SERVER = 4002

const socket = ref(null)
const isConnected = ref(false)
const reconnectAttempts = ref(0)
const reconnectExhausted = ref(false)
const lastCloseCode = ref(null)
const lastCloseReason = ref('')
let reconnectTimer = null
let pingTimer = null
let intentionalDisconnect = false
let consecutiveReconnectFailures = 0
let activeConnectionId = 0
let reconnectWithTokenTimer = null
let pendingTokenForReconnect = null
const eventHandlers = new Map()

function devLog(...args) {
  if (import.meta.env.DEV) {
    console.log(...args)
  }
}

function devWarn(...args) {
  if (import.meta.env.DEV) {
    console.warn(...args)
  }
}

function getWebSocketOrigin() {
  const raw = import.meta.env.VITE_WS_URL
  if (raw && String(raw).trim()) {
    try {
      const s = String(raw).trim()
      const u = new URL(s.includes('://') ? s : `http://${s}`)
      if (!isDockerServiceHostname(u.hostname)) {
        const proto =
          u.protocol === 'https:' || u.protocol === 'wss:' ? 'wss:' : 'ws:'
        return `${proto}//${u.host}`
      }
    } catch {
      /* fall through */
    }
  }
  if (typeof window !== 'undefined' && window.location?.host) {
    return `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}`
  }
  return 'ws://127.0.0.1:8000'
}

function parseJwtExp(token) {
  if (!token || typeof token !== 'string') return null
  try {
    const parts = token.split('.')
    if (parts.length < 2) return null
    const payload = JSON.parse(atob(parts[1].replace(/-/g, '+').replace(/_/g, '/')))
    return typeof payload.exp === 'number' ? payload.exp : null
  } catch {
    return null
  }
}

function tokenNeedsRefresh(token) {
  const exp = parseJwtExp(token)
  // If JWT payload cannot be parsed, force refresh instead of reusing a potentially stale token.
  if (!exp) return true
  const nowSec = Math.floor(Date.now() / 1000)
  return exp - nowSec < TOKEN_REFRESH_LEEWAY_SEC
}

function readStoredAccessToken() {
  if (typeof localStorage === 'undefined') return null
  return localStorage.getItem('auth_token')
}

async function resolveAccessToken({ forceRefresh = false } = {}) {
  let token = readStoredAccessToken()
  if (!token) return null

  if (!forceRefresh && !tokenNeedsRefresh(token)) {
    return token
  }

  try {
    const { useAuthStore } = await import('@/stores/auth')
    const authStore = useAuthStore()
    if (authStore.refreshToken) {
      token = await authStore.refreshAccessToken()
      return token
    }
  } catch (e) {
    devWarn('WebSocket: token refresh failed', e)
  }

  return readStoredAccessToken()
}

function isNonRecoverableClose(code) {
  return code === WS_CLOSE_AUTH || code === WS_CLOSE_SERVER
}

function closeMessageForCode(code) {
  if (code === WS_CLOSE_AUTH) {
    return 'Live updates unavailable — session expired or invalid. Please sign in again.'
  }
  if (code === WS_CLOSE_SERVER) {
    return 'Live updates unavailable — server error. Try reconnecting.'
  }
  if (code === 1006) {
    return 'Live updates disconnected unexpectedly.'
  }
  return 'Live updates disconnected.'
}

function emit(eventType, data) {
  const handlers = eventHandlers.get(eventType)
  if (!handlers) return
  handlers.forEach((handler) => {
    try {
      handler(data)
    } catch (error) {
      console.error(`Error in WebSocket handler for ${eventType}:`, error)
    }
  })
}

function stopPingInterval() {
  if (pingTimer) {
    clearInterval(pingTimer)
    pingTimer = null
  }
}

function startPingInterval() {
  stopPingInterval()
  pingTimer = setInterval(() => {
    if (socket.value?.readyState === WebSocket.OPEN) {
      send({ type: 'ping' })
    }
  }, PING_INTERVAL_MS)
}

function send(data) {
  if (socket.value?.readyState === WebSocket.OPEN) {
    socket.value.send(JSON.stringify(data))
  } else {
    devWarn('Cannot send: WebSocket not connected')
  }
}

function handleMessage(data) {
  const { type } = data
  if (type === 'connection_confirmed') {
    devLog('WebSocket connection confirmed', data)
    emit('connection_confirmed', data)
    return
  }
  if (type === 'pong') return
  if (type === 'error') {
    console.error('WebSocket error:', data.message)
    emit('error', data)
    return
  }
  emit(type, data.data || data)
}

function clearReconnectTimer() {
  if (reconnectTimer) {
    clearTimeout(reconnectTimer)
    reconnectTimer = null
  }
}

function buildDashboardWsUrl(token) {
  return `${getWebSocketOrigin()}/ws/dashboard/?token=${encodeURIComponent(token)}`
}

/**
 * Replace an in-flight or open socket without calling close() while CONNECTING
 * (avoids "WebSocket is closed before the connection is established" noise).
 */
function supersedeSocket(ws, reason = 'Superseded') {
  if (!ws) return

  ws.onmessage = null
  ws.onerror = null

  const closeSuperseded = () => {
    try {
      if (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CLOSING) {
        ws.close(WS_CLOSE_NORMAL, reason)
      }
    } catch {
      /* ignore */
    }
  }

  if (ws.readyState === WebSocket.OPEN) {
    ws.onopen = null
    ws.onclose = null
    closeSuperseded()
    return
  }

  if (ws.readyState === WebSocket.CONNECTING) {
    ws.onopen = () => {
      ws.onclose = null
      closeSuperseded()
    }
    ws.onclose = null
    return
  }

  ws.onopen = null
  ws.onclose = null
}

function detachSocketHandlers(ws) {
  if (!ws) return
  ws.onopen = null
  ws.onmessage = null
  ws.onerror = null
  ws.onclose = null
}

async function scheduleReconnect(closeCode) {
  if (intentionalDisconnect || reconnectTimer) return

  if (isNonRecoverableClose(closeCode)) {
    reconnectExhausted.value = true
    emit('reconnect_exhausted', {
      code: closeCode,
      message: closeMessageForCode(closeCode),
    })
    return
  }

  if (reconnectAttempts.value >= MAX_RECONNECT_ATTEMPTS) {
    reconnectExhausted.value = true
    emit('reconnect_exhausted', {
      code: closeCode,
      message: 'Could not restore live updates. Use Reconnect or refresh the page.',
    })
    return
  }

  const delay = Math.min(
    RECONNECT_DELAY_MS * Math.pow(2, reconnectAttempts.value),
    MAX_RECONNECT_DELAY_MS
  )
  const jitter = Math.floor(Math.random() * 500)
  const totalDelay = delay + jitter
  reconnectAttempts.value += 1
  devLog(`WebSocket reconnect in ${totalDelay}ms (attempt ${reconnectAttempts.value})`)

  reconnectTimer = setTimeout(async () => {
    reconnectTimer = null
    const forceRefresh =
      closeCode === WS_CLOSE_AUTH ||
      tokenNeedsRefresh(readStoredAccessToken()) ||
      consecutiveReconnectFailures >= 2
    const token = await resolveAccessToken({ forceRefresh })
    if (!token) {
      reconnectExhausted.value = true
      emit('reconnect_exhausted', {
        code: closeCode,
        message: 'Session ended. Please sign in again.',
      })
      return
    }
    connect(token)
  }, totalDelay)
}

async function connect(tokenOrUndefined) {
  intentionalDisconnect = false

  const token = tokenOrUndefined || (await resolveAccessToken())
  if (!token) {
    devWarn('WebSocket connect skipped: no access token')
    return
  }

  const wsUrl = buildDashboardWsUrl(token)
  const existing = socket.value

  if (existing?.readyState === WebSocket.OPEN && existing.url === wsUrl) {
    devLog('WebSocket already connected')
    return
  }

  if (existing?.readyState === WebSocket.CONNECTING && existing.url === wsUrl) {
    devLog('WebSocket connection already in progress')
    return
  }

  reconnectExhausted.value = false
  const connectionId = ++activeConnectionId

  if (existing) {
    supersedeSocket(existing, 'Replacing connection')
    if (socket.value === existing) {
      socket.value = null
    }
  }

  try {
    const ws = new WebSocket(wsUrl)
    socket.value = ws

    ws.onopen = () => {
      if (connectionId !== activeConnectionId || socket.value !== ws) {
        supersedeSocket(ws, 'Stale connection')
        return
      }
      devLog('WebSocket connected')
      isConnected.value = true
      consecutiveReconnectFailures = 0
      reconnectAttempts.value = 0
      lastCloseCode.value = null
      lastCloseReason.value = ''
      startPingInterval()
      emit('connected', { timestamp: new Date().toISOString() })
    }

    ws.onmessage = (event) => {
      if (connectionId !== activeConnectionId || socket.value !== ws) return
      try {
        handleMessage(JSON.parse(event.data))
      } catch (error) {
        console.error('Error parsing WebSocket message:', error)
      }
    }

    ws.onerror = () => {
      if (connectionId !== activeConnectionId || socket.value !== ws) return
      emit('error', { error: 'WebSocket connection error' })
    }

    ws.onclose = (event) => {
      if (connectionId !== activeConnectionId) {
        return
      }
      if (socket.value === ws) {
        socket.value = null
      }
      devLog('WebSocket disconnected', event.code, event.reason)
      isConnected.value = false
      stopPingInterval()
      lastCloseCode.value = event.code
      lastCloseReason.value = event.reason || closeMessageForCode(event.code)

      emit('disconnected', { code: event.code, reason: event.reason })

      if (intentionalDisconnect || event.code === WS_CLOSE_NORMAL) {
        return
      }

      consecutiveReconnectFailures += 1
      const forceAuthRefresh = event.code === WS_CLOSE_AUTH
      scheduleReconnect(forceAuthRefresh ? WS_CLOSE_AUTH : event.code)
    }
  } catch (error) {
    console.error('Error creating WebSocket:', error)
    consecutiveReconnectFailures += 1
    scheduleReconnect(null)
  }
}

function disconnect() {
  intentionalDisconnect = true
  activeConnectionId += 1
  clearReconnectTimer()
  if (reconnectWithTokenTimer) {
    clearTimeout(reconnectWithTokenTimer)
    reconnectWithTokenTimer = null
  }
  pendingTokenForReconnect = null
  stopPingInterval()
  consecutiveReconnectFailures = 0

  if (socket.value) {
    const ws = socket.value
    detachSocketHandlers(ws)
    if (ws.readyState === WebSocket.OPEN) {
      try {
        ws.close(WS_CLOSE_NORMAL, 'User logout')
      } catch {
        /* ignore */
      }
    } else if (ws.readyState === WebSocket.CONNECTING) {
      ws.onopen = () => {
        try {
          ws.close(WS_CLOSE_NORMAL, 'User logout')
        } catch {
          /* ignore */
        }
      }
    }
    socket.value = null
  }

  isConnected.value = false
  reconnectAttempts.value = 0
  reconnectExhausted.value = false
  lastCloseCode.value = null
  lastCloseReason.value = ''
}

/** Manual reconnect from UI (resets backoff). */
async function reconnect() {
  intentionalDisconnect = false
  clearReconnectTimer()
  if (reconnectWithTokenTimer) {
    clearTimeout(reconnectWithTokenTimer)
    reconnectWithTokenTimer = null
  }
  pendingTokenForReconnect = null
  reconnectAttempts.value = 0
  reconnectExhausted.value = false
  consecutiveReconnectFailures = 0

  if (socket.value) {
    supersedeSocket(socket.value, 'Reconnecting')
    socket.value = null
  }

  const token = await resolveAccessToken({ forceRefresh: true })
  if (token) {
    connect(token)
  }
}

/** Called after Axios refreshes the access token (debounced). */
function reconnectWithToken(accessToken) {
  if (!accessToken || intentionalDisconnect) return

  pendingTokenForReconnect = accessToken
  if (reconnectWithTokenTimer) {
    clearTimeout(reconnectWithTokenTimer)
  }

  reconnectWithTokenTimer = setTimeout(() => {
    reconnectWithTokenTimer = null
    const token = pendingTokenForReconnect
    pendingTokenForReconnect = null
    if (!token || intentionalDisconnect) return

    intentionalDisconnect = false
    clearReconnectTimer()
    reconnectAttempts.value = 0
    reconnectExhausted.value = false
    consecutiveReconnectFailures = 0

    const existing = socket.value
    const nextUrl = buildDashboardWsUrl(token)
    if (existing?.readyState === WebSocket.OPEN && existing.url === nextUrl) {
      return
    }

    if (existing) {
      supersedeSocket(existing, 'Token refreshed')
      socket.value = null
    }

    connect(token)
  }, 150)
}

function on(eventType, handler) {
  if (!eventHandlers.has(eventType)) {
    eventHandlers.set(eventType, [])
  }
  eventHandlers.get(eventType).push(handler)
}

function off(eventType, handler) {
  const handlers = eventHandlers.get(eventType)
  if (!handlers) return
  if (!handler) {
    eventHandlers.delete(eventType)
    return
  }
  const index = handlers.indexOf(handler)
  if (index > -1) handlers.splice(index, 1)
}

function subscribeScreen(screenId) {
  send({ type: 'subscribe_screen', screen_id: screenId })
}

function unsubscribeScreen(screenId) {
  send({ type: 'unsubscribe_screen', screen_id: screenId })
}

function subscribeCommand(commandId) {
  send({ type: 'subscribe_command', command_id: commandId })
}

/** Resume after browser comes online. */
function handleBrowserOnline() {
  if (intentionalDisconnect) return
  if (!isConnected.value && !reconnectTimer) {
    reconnectAttempts.value = 0
    reconnect()
  }
}

if (typeof window !== 'undefined') {
  window.addEventListener('online', handleBrowserOnline)
}

export function useWebSocket() {
  return {
    socket,
    isConnected,
    reconnectExhausted,
    lastCloseCode,
    lastCloseReason,
    connect,
    disconnect,
    reconnect,
    reconnectWithToken,
    send,
    on,
    off,
    subscribeScreen,
    unsubscribeScreen,
    subscribeCommand,
  }
}

/** Singleton API for api.js and plugins (same instance as useWebSocket()). */
export const dashboardWebSocket = useWebSocket()
