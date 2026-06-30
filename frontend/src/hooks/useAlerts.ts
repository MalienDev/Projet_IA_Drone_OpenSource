import { useState, useEffect, useRef, useCallback } from 'react'
import { eventsApi } from '../services/api'
import type { AlertWebSocketMessage } from '../types'
import { normalizeEvent, sortAlerts, upsertAlert } from '../utils/alerts'

export function useAlerts() {
  const [alerts, setAlerts] = useState<AlertWebSocketMessage[]>([])
  const [connected, setConnected] = useState<boolean>(false)
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)
  const [lastRealtimeAlertId, setLastRealtimeAlertId] = useState<string | null>(null)
  const wsRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      setLoading(false)
      return
    }

    let cancelled = false
    let reconnectTimer: number | null = null

    const loadHistory = async () => {
      try {
        setLoading(true)
        const events = await eventsApi.list({ limit: 100 })
        if (!cancelled) {
          setAlerts(sortAlerts(events.map(normalizeEvent)))
          setError(null)
        }
      } catch (err) {
        if (!cancelled) {
          setError("Historique d'alertes indisponible.")
        }
        console.error(err)
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    const connect = () => {
      const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
      const wsUrl = `${protocol}://${window.location.host}/ws/alerts?token=${encodeURIComponent(token)}`

      try {
        wsRef.current = new WebSocket(wsUrl)

        wsRef.current.onopen = () => {
          setConnected(true)
          setError(null)
        }

        wsRef.current.onmessage = (event) => {
          try {
            const alert: AlertWebSocketMessage = JSON.parse(event.data)
            setAlerts((prev) => upsertAlert(prev, alert))
            setLastRealtimeAlertId(alert.alert_id)
          } catch (parseError) {
            console.error('Error parsing alert:', parseError)
          }
        }

        wsRef.current.onerror = (wsError) => {
          console.error('WebSocket error:', wsError)
          setConnected(false)
        }

        wsRef.current.onclose = () => {
          setConnected(false)
          if (!cancelled) {
            reconnectTimer = window.setTimeout(connect, 3000)
          }
        }
      } catch (connectionError) {
        console.error('Failed to create WebSocket connection:', connectionError)
        setConnected(false)
        if (!cancelled) {
          reconnectTimer = window.setTimeout(connect, 3000)
        }
      }
    }

    loadHistory()
    connect()

    return () => {
      cancelled = true
      if (reconnectTimer !== null) {
        window.clearTimeout(reconnectTimer)
      }
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [])

  const acknowledgeAlert = useCallback(async (alertId: string) => {
    const updated = await eventsApi.acknowledge(alertId)
    setAlerts((prev) => upsertAlert(prev, normalizeEvent(updated)))
  }, [])

  return {
    alerts,
    connected,
    loading,
    error,
    lastRealtimeAlertId,
    acknowledgeAlert,
  }
}
