import { useEffect, useMemo, useRef, useState } from 'react'
import type { AlertWebSocketMessage } from '../types'
import {
  formatConfidence,
  formatDateTime,
  formatFullDateTime,
  getAlertTypeLabel,
  getSeverityClasses,
  getSeverityLabel,
  isOpenAlert,
} from '../utils/alerts'
import type { AlertStatusFilter } from '../utils/alerts'
import { BellIcon, CheckIcon, ClockIcon, FilterIcon, PlayIcon, WifiIcon, WifiOffIcon } from './Icons'
import VideoReplay from './VideoReplay'

interface AlertPanelProps {
  alerts: AlertWebSocketMessage[]
  connected: boolean
  loading?: boolean
  error?: string | null
  lastRealtimeAlertId?: string | null
  acknowledgeAlert: (alertId: string) => Promise<void>
}

const severityFilters = ['all', 'critical', 'high', 'medium', 'low'] as const

function playAlertTone(severity: string) {
  const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext
  if (!AudioContextClass) return

  const context = new AudioContextClass()
  const gain = context.createGain()
  const oscillator = context.createOscillator()
  const frequencies: Record<string, number> = {
    critical: 920,
    high: 760,
    medium: 620,
    low: 480,
  }

  oscillator.type = severity === 'critical' ? 'square' : 'sine'
  oscillator.frequency.value = frequencies[severity] ?? 540
  gain.gain.setValueAtTime(0.0001, context.currentTime)
  gain.gain.exponentialRampToValueAtTime(0.18, context.currentTime + 0.02)
  gain.gain.exponentialRampToValueAtTime(0.0001, context.currentTime + 0.22)
  oscillator.connect(gain)
  gain.connect(context.destination)
  oscillator.start()
  oscillator.stop(context.currentTime + 0.24)
  oscillator.onended = () => context.close()
}

function AlertPanel({
  alerts,
  connected,
  loading = false,
  error = null,
  lastRealtimeAlertId = null,
  acknowledgeAlert,
}: AlertPanelProps) {
  const [statusFilter, setStatusFilter] = useState<AlertStatusFilter>('open')
  const [severityFilter, setSeverityFilter] = useState<(typeof severityFilters)[number]>('all')
  const [typeFilter, setTypeFilter] = useState('all')
  const [muted, setMuted] = useState(false)
  const [ackLoadingId, setAckLoadingId] = useState<string | null>(null)
  const [ackError, setAckError] = useState<string | null>(null)
  const [replayAlert, setReplayAlert] = useState<AlertWebSocketMessage | null>(null)
  const previousRealtimeAlertRef = useRef<string | null>(null)

  const alertTypes = useMemo(() => {
    return Array.from(new Set(alerts.map((alert) => alert.type))).sort()
  }, [alerts])

  const filteredAlerts = useMemo(() => {
    return alerts.filter((alert) => {
      const statusMatches =
        statusFilter === 'all'
          || (statusFilter === 'open' && isOpenAlert(alert))
          || (statusFilter === 'acknowledged' && !isOpenAlert(alert))
      const severityMatches = severityFilter === 'all' || alert.severity === severityFilter
      const typeMatches = typeFilter === 'all' || alert.type === typeFilter

      return statusMatches && severityMatches && typeMatches
    })
  }, [alerts, severityFilter, statusFilter, typeFilter])

  useEffect(() => {
    if (!lastRealtimeAlertId || previousRealtimeAlertRef.current === lastRealtimeAlertId) return

    previousRealtimeAlertRef.current = lastRealtimeAlertId
    const latestAlert = alerts.find((alert) => alert.alert_id === lastRealtimeAlertId)
    if (latestAlert && isOpenAlert(latestAlert) && !muted) {
      playAlertTone(latestAlert.severity)
    }
  }, [alerts, lastRealtimeAlertId, muted])

  const handleAcknowledge = async (alertId: string) => {
    setAckError(null)
    setAckLoadingId(alertId)

    try {
      await acknowledgeAlert(alertId)
    } catch (err) {
      setAckError("Accusé de réception impossible. Vérifier la connexion backend.")
      console.error(err)
    } finally {
      setAckLoadingId(null)
    }
  }

  const openAlerts = alerts.filter(isOpenAlert).length
  const criticalOpenAlerts = alerts.filter((alert) => isOpenAlert(alert) && alert.severity === 'critical').length

  return (
    <div className="flex h-full min-h-0 flex-col">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-neutral-800 px-4 py-3">
        <div className="flex min-w-0 items-center gap-3">
          <span className="flex h-9 w-9 items-center justify-center rounded-md border border-amber-500/35 bg-amber-500/10 text-amber-200">
            <BellIcon className="h-4 w-4" />
          </span>
          <div className="min-w-0">
            <h2 className="truncate text-sm font-semibold text-neutral-100">Alertes opérateur</h2>
            <p className="truncate text-xs text-neutral-500">
              {openAlerts} ouverte(s), {criticalOpenAlerts} critique(s) à confirmer
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className={`inline-flex items-center gap-2 rounded-md border px-2.5 py-1 text-xs ${
            connected
              ? 'border-emerald-500/35 bg-emerald-500/10 text-emerald-200'
              : 'border-red-500/35 bg-red-500/10 text-red-200'
          }`}>
            {connected ? <WifiIcon className="h-3.5 w-3.5" /> : <WifiOffIcon className="h-3.5 w-3.5" />}
            {connected ? 'Temps réel' : 'Hors ligne'}
          </span>
          <button
            type="button"
            onClick={() => setMuted((value) => !value)}
            className={`toolbar-button ${muted ? 'toolbar-button--active' : ''}`}
          >
            {muted ? 'Son coupé' : 'Son actif'}
          </button>
        </div>
      </div>

      <div className="border-b border-neutral-800 px-4 py-3">
        <div className="grid gap-2 sm:grid-cols-[1fr_1fr_1.1fr]">
          <div className="segmented-control" aria-label="Filtre statut">
            {(['open', 'all', 'acknowledged'] as AlertStatusFilter[]).map((status) => (
              <button
                key={status}
                type="button"
                onClick={() => setStatusFilter(status)}
                className={statusFilter === status ? 'is-active' : ''}
              >
                {status === 'open' ? 'Ouvertes' : status === 'acknowledged' ? 'Acquittées' : 'Toutes'}
              </button>
            ))}
          </div>

          <label className="select-control">
            <FilterIcon className="h-4 w-4 text-neutral-500" />
            <select
              value={severityFilter}
              onChange={(event) => setSeverityFilter(event.target.value as (typeof severityFilters)[number])}
            >
              {severityFilters.map((severity) => (
                <option key={severity} value={severity}>
                  {severity === 'all' ? 'Toutes sévérités' : getSeverityLabel(severity)}
                </option>
              ))}
            </select>
          </label>

          <label className="select-control">
            <BellIcon className="h-4 w-4 text-neutral-500" />
            <select value={typeFilter} onChange={(event) => setTypeFilter(event.target.value)}>
              <option value="all">Tous types</option>
              {alertTypes.map((type) => (
                <option key={type} value={type}>{getAlertTypeLabel(type)}</option>
              ))}
            </select>
          </label>
        </div>
      </div>

      {ackError && (
        <div className="border-b border-red-500/20 bg-red-950/30 px-4 py-2 text-xs text-red-200">
          {ackError}
        </div>
      )}

      <div className="min-h-0 flex-1 overflow-y-auto px-3 py-3">
        {loading ? (
          <div className="flex h-44 items-center justify-center text-sm text-neutral-400">
            Chargement des alertes...
          </div>
        ) : error ? (
          <div className="flex h-44 items-center justify-center px-4 text-center text-sm text-red-200">
            {error}
          </div>
        ) : filteredAlerts.length === 0 ? (
          <div className="flex h-44 flex-col items-center justify-center px-4 text-center text-sm text-neutral-500">
            <CheckIcon className="mb-3 h-8 w-8 text-emerald-300" />
            Aucune alerte ne correspond aux filtres.
          </div>
        ) : (
          <div className="space-y-3">
            {filteredAlerts.map((alert) => {
              const open = isOpenAlert(alert)
              const severityClasses = getSeverityClasses(alert.severity)

              return (
                <article
                  key={alert.alert_id}
                  className={`alert-item ${open ? 'alert-item--open' : 'opacity-70'}`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className={`rounded-md border px-2 py-1 text-[11px] font-semibold ${severityClasses}`}>
                          {getSeverityLabel(alert.severity)}
                        </span>
                        {open && (
                          <span className="rounded-md border border-amber-500/40 bg-amber-500/10 px-2 py-1 text-[11px] font-medium text-amber-100">
                            À confirmer
                          </span>
                        )}
                      </div>
                      <h3 className="mt-2 truncate text-sm font-semibold text-neutral-100">
                        {getAlertTypeLabel(alert.type)}
                      </h3>
                    </div>
                    <div className="flex shrink-0 items-center gap-1.5 text-xs text-neutral-500">
                      <ClockIcon className="h-3.5 w-3.5" />
                      {formatDateTime(alert.timestamp)}
                    </div>
                  </div>

                  <dl className="mt-3 grid grid-cols-2 gap-2 text-xs text-neutral-400">
                    <div>
                      <dt className="text-neutral-600">Drone</dt>
                      <dd className="truncate text-neutral-200">{alert.drone_id}</dd>
                    </div>
                    <div>
                      <dt className="text-neutral-600">Confiance</dt>
                      <dd className="text-neutral-200">{formatConfidence(alert.confidence)}</dd>
                    </div>
                    {alert.zone_id && (
                      <div>
                        <dt className="text-neutral-600">Zone</dt>
                        <dd className="truncate text-neutral-200">{alert.zone_id}</dd>
                      </div>
                    )}
                    {alert.track_id && (
                      <div>
                        <dt className="text-neutral-600">Track</dt>
                        <dd className="truncate text-neutral-200">{alert.track_id}</dd>
                      </div>
                    )}
                  </dl>

                  {alert.snapshot_path && (
                    <img
                      src={alert.snapshot_path}
                      alt="Capture associée à l’alerte"
                      className="mt-3 h-28 w-full rounded-md border border-neutral-800 object-cover"
                    />
                  )}

                  <div className="mt-3 flex flex-wrap items-center justify-between gap-2">
                    <p className="text-[11px] text-neutral-600" title={formatFullDateTime(alert.timestamp)}>
                      ID {alert.alert_id.slice(0, 8)}
                    </p>
                    <div className="flex items-center gap-2">
                      {alert.clip_path && (
                        <button
                          type="button"
                          onClick={() => setReplayAlert(alert)}
                          className="icon-text-button"
                        >
                          <PlayIcon className="h-3.5 w-3.5" />
                          Replay
                        </button>
                      )}
                      {open ? (
                        <button
                          type="button"
                          onClick={() => handleAcknowledge(alert.alert_id)}
                          disabled={ackLoadingId === alert.alert_id}
                          className="confirm-button"
                        >
                          <CheckIcon className="h-3.5 w-3.5" />
                          {ackLoadingId === alert.alert_id ? 'En cours' : 'Accuser'}
                        </button>
                      ) : (
                        <span className="rounded-md border border-neutral-700 bg-neutral-900 px-2.5 py-1 text-[11px] text-neutral-400">
                          Acquittée {alert.acknowledged_by ? `par ${alert.acknowledged_by}` : ''}
                        </span>
                      )}
                    </div>
                  </div>
                </article>
              )
            })}
          </div>
        )}
      </div>

      {replayAlert && (
        <VideoReplay
          clipPath={replayAlert.clip_path || undefined}
          alertLabel={getAlertTypeLabel(replayAlert.type)}
          onClose={() => setReplayAlert(null)}
        />
      )}
    </div>
  )
}

export default AlertPanel
