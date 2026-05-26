/**
 * WebSocket client for the TV pairing wait screen.
 * Connects with the temporary pairing_token; server pushes `paired` when bind completes.
 */
import { isDockerServiceHostname } from '@/utils/apiBaseUrl'

function pairingWebSocketUrl(pairingToken) {
  if (!pairingToken || typeof window === 'undefined') return null

  const raw = import.meta.env.VITE_WS_URL
  if (raw && String(raw).trim()) {
    try {
      const s = String(raw).trim()
      const u = new URL(s.includes('://') ? s : `http://${s}`)
      if (!isDockerServiceHostname(u.hostname)) {
        const proto = u.protocol === 'https:' || u.protocol === 'wss:' ? 'wss:' : 'ws:'
        return `${proto}//${u.host}/ws/pairing/?pairing_token=${encodeURIComponent(pairingToken)}`
      }
    } catch {
      /* fall through */
    }
  }

  const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  return `${proto}//${window.location.host}/ws/pairing/?pairing_token=${encodeURIComponent(pairingToken)}`
}

/**
 * @param {object} options
 * @param {() => string|null} options.getToken
 * @param {(payload: { screenId: string }) => void} options.onPaired
 * @param {(code: number) => void} [options.onClose]
 */
export function usePairingWebSocket({ getToken, onPaired, onClose }) {
  let socket = null
  let reconnectTimer = null
  let intentionalClose = false
  let connectionId = 0

  function clearReconnect() {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
  }

  function closeSocket() {
    if (!socket) return
    const ws = socket
    socket = null
    if (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING) {
      try {
        ws.close(1000, 'pairing flow ended')
      } catch {
        /* ignore */
      }
    }
  }

  function scheduleReconnect() {
    if (intentionalClose) return
    clearReconnect()
    reconnectTimer = setTimeout(() => connect(), 3000)
  }

  function connect() {
    const token = getToken()
    const url = pairingWebSocketUrl(token)
    if (!url) return

    clearReconnect()
    closeSocket()

    const myConnectionId = ++connectionId
    intentionalClose = false

    try {
      const ws = new WebSocket(url)
      socket = ws

      ws.onmessage = (event) => {
        if (myConnectionId !== connectionId || socket !== ws) return
        try {
          const data = JSON.parse(event.data)
          if (data?.event === 'paired' && data.screen_id) {
            onPaired({ screenId: String(data.screen_id) })
          }
        } catch {
          /* ignore malformed payloads */
        }
      }

      ws.onclose = (event) => {
        if (myConnectionId !== connectionId) return
        if (socket === ws) socket = null
        onClose?.(event.code)
        if (!intentionalClose && event.code !== 1000) {
          scheduleReconnect()
        }
      }

      ws.onerror = () => {
        /* onclose handles reconnect */
      }
    } catch {
      scheduleReconnect()
    }
  }

  function disconnect() {
    intentionalClose = true
    connectionId += 1
    clearReconnect()
    closeSocket()
  }

  return { connect, disconnect }
}
