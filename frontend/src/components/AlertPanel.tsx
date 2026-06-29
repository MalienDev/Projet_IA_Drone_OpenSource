import { useEffect, useRef, useState } from 'react'
import { useAlerts } from '../hooks/useAlerts'
import { eventsApi } from '../services/api'
import type { AlertWebSocketMessage } from '../types'
import { Howl } from 'howler'
import VideoReplay from './VideoReplay'

function AlertPanel() {
  const { alerts, connected } = useAlerts()
  const soundRef = useRef<Howl | null>(null)
  const [replayClip, setReplayClip] = useState<string | null>(null)

  useEffect(() => {
    // Initialize sound for alerts
    soundRef.current = new Howl({
      src: ['/sounds/alert.mp3'],
      volume: 0.5,
    })

    return () => {
      if (soundRef.current) {
        soundRef.current.unload()
      }
    }
  }, [])

  useEffect(() => {
    // Play sound when new alert arrives
    if (alerts.length > 0 && soundRef.current) {
      const latestAlert = alerts[0]
      if (latestAlert.requires_operator_ack && !latestAlert.acknowledged_by) {
        soundRef.current.play()
      }
    }
  }, [alerts])

  const handleAcknowledge = async (alertId: string) => {
    try {
      await eventsApi.acknowledge(alertId)
      // Refresh alerts list
      window.location.reload()
    } catch (error) {
      console.error('Failed to acknowledge alert:', error)
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-600'
      case 'high':
        return 'bg-orange-600'
      case 'medium':
        return 'bg-yellow-600'
      case 'low':
        return 'bg-blue-600'
      default:
        return 'bg-gray-600'
    }
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-white">Recent Alerts</h3>
        <div className="flex items-center space-x-2">
          <span className={`w-3 h-3 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'}`}></span>
          <span className="text-sm text-gray-400">
            {connected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </div>

      <div className="space-y-2 max-h-96 overflow-y-auto">
        {alerts.length === 0 ? (
          <p className="text-gray-400 text-center py-8">No alerts</p>
        ) : (
          alerts.map((alert) => (
            <div
              key={alert.alert_id}
              className={`p-4 rounded-lg ${
                alert.acknowledged_by ? 'bg-gray-700 opacity-60' : 'bg-gray-700'
              }`}
            >
              <div className="flex justify-between items-start mb-2">
                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-1 rounded text-xs text-white ${getSeverityColor(alert.severity)}`}>
                    {alert.severity}
                  </span>
                  <span className="text-sm text-gray-300">{alert.type}</span>
                </div>
                <span className="text-xs text-gray-400">
                  {new Date(alert.timestamp).toLocaleString()}
                </span>
              </div>

              <div className="text-sm text-gray-300 mb-2">
                <p>Drone: {alert.drone_id}</p>
                <p>Confidence: {(alert.confidence * 100).toFixed(1)}%</p>
                {alert.zone_id && <p>Zone: {alert.zone_id}</p>}
                {alert.track_id && <p>Track ID: {alert.track_id}</p>}
              </div>

              {alert.requires_operator_ack && !alert.acknowledged_by && (
                <button
                  onClick={() => handleAcknowledge(alert.alert_id)}
                  className="mt-2 bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700"
                >
                  Acknowledge
                </button>
              )}

              {alert.acknowledged_by && (
                <p className="text-xs text-gray-400 mt-2">
                  Acknowledged by {alert.acknowledged_by} at{' '}
                  {alert.acknowledged_at ? new Date(alert.acknowledged_at).toLocaleString() : 'N/A'}
                </p>
              )}

              {alert.snapshot_path && (
                <div className="mt-2">
                  <img
                    src={alert.snapshot_path}
                    alt="Alert snapshot"
                    className="w-32 h-32 object-cover rounded"
                  />
                </div>
              )}

              {alert.clip_path && (
                <button
                  onClick={() => setReplayClip(alert.clip_path)}
                  className="mt-2 bg-purple-600 text-white px-3 py-1 rounded text-sm hover:bg-purple-700"
                >
                  Replay Clip
                </button>
              )}
            </div>
          ))
        )}
      </div>

      {replayClip && (
        <VideoReplay
          clipPath={replayClip}
          onClose={() => setReplayClip(null)}
        />
      )}
    </div>
  )
}

export default AlertPanel
