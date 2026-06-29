import { useState, useEffect, useRef } from 'react'
import type { AlertWebSocketMessage } from '../types'

export function useAlerts() {
  const [alerts, setAlerts] = useState<AlertWebSocketMessage[]>([])
  const [connected, setConnected] = useState<boolean>(false)
  const wsRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (!token) return

    const wsUrl = `ws://localhost:8000/ws/alerts?token=${token}`
    wsRef.current = new WebSocket(wsUrl)

    wsRef.current.onopen = () => {
      console.log('WebSocket connected')
      setConnected(true)
    }

    wsRef.current.onmessage = (event) => {
      try {
        const alert: AlertWebSocketMessage = JSON.parse(event.data)
        setAlerts((prev) => [alert, ...prev])
      } catch (error) {
        console.error('Error parsing alert:', error)
      }
    }

    wsRef.current.onerror = (error) => {
      console.error('WebSocket error:', error)
      setConnected(false)
    }

    wsRef.current.onclose = () => {
      console.log('WebSocket disconnected')
      setConnected(false)
    }

    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [])

  return { alerts, connected }
}
