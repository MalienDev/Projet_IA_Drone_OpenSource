import type { AlertWebSocketMessage, Event } from '../types'

export type Severity = 'low' | 'medium' | 'high' | 'critical'
export type AlertStatusFilter = 'all' | 'open' | 'acknowledged'

export const severityOrder: Record<string, number> = {
  critical: 4,
  high: 3,
  medium: 2,
  low: 1,
}

export function normalizeEvent(event: Event): AlertWebSocketMessage {
  return {
    alert_id: event.alert_id,
    timestamp: event.timestamp,
    drone_id: event.drone_id,
    type: event.event_type,
    severity: event.severity,
    confidence: event.confidence,
    bbox: event.bbox,
    track_id: event.track_id,
    zone_id: event.zone_id,
    geo: event.geo,
    snapshot_path: event.snapshot_path,
    clip_path: event.clip_path,
    requires_operator_ack: event.requires_operator_ack,
    acknowledged_by: event.acknowledged_by ?? null,
    acknowledged_at: event.acknowledged_at ?? null,
  }
}

export function sortAlerts(alerts: AlertWebSocketMessage[]) {
  return [...alerts].sort((a, b) => {
    const timeDiff = new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
    if (timeDiff !== 0) return timeDiff
    return (severityOrder[b.severity] ?? 0) - (severityOrder[a.severity] ?? 0)
  })
}

export function upsertAlert(
  alerts: AlertWebSocketMessage[],
  alert: AlertWebSocketMessage,
) {
  const index = alerts.findIndex((item) => item.alert_id === alert.alert_id)
  if (index === -1) {
    return sortAlerts([alert, ...alerts]).slice(0, 250)
  }

  const next = [...alerts]
  next[index] = { ...next[index], ...alert }
  return sortAlerts(next)
}

export function isOpenAlert(alert: AlertWebSocketMessage) {
  return alert.requires_operator_ack && !alert.acknowledged_by
}

export function getAlertTypeLabel(type: string) {
  switch (type) {
    case 'weapon_suspected':
      return 'Arme probable - à confirmer'
    case 'intrusion':
      return 'Intrusion zone'
    case 'crowd':
      return 'Regroupement'
    case 'person':
      return 'Personne'
    case 'vehicle':
      return 'Véhicule'
    case 'movement_motorbike':
      return 'Déplacement moto'
    case 'movement_foot':
      return 'Déplacement à pied'
    default:
      return type.replace(/_/g, ' ')
  }
}

export function getSeverityLabel(severity: string) {
  switch (severity) {
    case 'critical':
      return 'Critique'
    case 'high':
      return 'Élevée'
    case 'medium':
      return 'Moyenne'
    case 'low':
      return 'Basse'
    default:
      return severity
  }
}

export function getSeverityClasses(severity: string) {
  switch (severity) {
    case 'critical':
      return 'border-red-500/70 bg-red-500/12 text-red-100'
    case 'high':
      return 'border-orange-500/70 bg-orange-500/12 text-orange-100'
    case 'medium':
      return 'border-amber-500/70 bg-amber-500/12 text-amber-100'
    case 'low':
      return 'border-sky-500/70 bg-sky-500/12 text-sky-100'
    default:
      return 'border-neutral-500/70 bg-neutral-500/12 text-neutral-100'
  }
}

export function getZoneTypeLabel(zoneType: string) {
  switch (zoneType) {
    case 'INTRUSION':
      return 'Intrusion'
    case 'CROWD':
      return 'Regroupement'
    case 'SAFE':
      return 'Sûre'
    default:
      return zoneType
  }
}

export function formatConfidence(confidence: number) {
  return `${Math.round(confidence * 100)}%`
}

export function formatDateTime(timestamp: string) {
  return new Intl.DateTimeFormat('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  }).format(new Date(timestamp))
}

export function formatFullDateTime(timestamp: string) {
  return new Intl.DateTimeFormat('fr-FR', {
    dateStyle: 'medium',
    timeStyle: 'medium',
  }).format(new Date(timestamp))
}
