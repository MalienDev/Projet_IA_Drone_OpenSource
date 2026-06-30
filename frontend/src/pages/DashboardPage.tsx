import { useMemo } from 'react'
import type { ReactNode } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { useAlerts } from '../hooks/useAlerts'
import { useDrones } from '../hooks/useDrones'
import { useZones } from '../hooks/useZones'
import MapView from '../components/MapView'
import VideoPlayer from '../components/VideoPlayer'
import AlertPanel from '../components/AlertPanel'
import { ActivityIcon, AlertTriangleIcon, DroneIcon, LogOutIcon, MapIcon, ShieldIcon, VideoIcon } from '../components/Icons'
import { formatConfidence, isOpenAlert } from '../utils/alerts'

interface MetricTileProps {
  label: string
  value: string | number
  detail: string
  tone?: 'neutral' | 'green' | 'amber' | 'red'
  icon: ReactNode
}

function MetricTile({ label, value, detail, tone = 'neutral', icon }: MetricTileProps) {
  return (
    <div className={`metric-tile metric-tile--${tone}`}>
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="truncate text-xs font-medium text-neutral-500">{label}</p>
          <p className="mt-1 text-2xl font-semibold text-neutral-100">{value}</p>
        </div>
        <span className="metric-tile__icon">{icon}</span>
      </div>
      <p className="mt-3 truncate text-xs text-neutral-500">{detail}</p>
    </div>
  )
}

interface PanelShellProps {
  title: string
  subtitle: string
  icon: ReactNode
  children: ReactNode
  className?: string
}

function PanelShell({ title, subtitle, icon, children, className = '' }: PanelShellProps) {
  return (
    <section className={`ops-panel ${className}`}>
      <div className="flex items-center justify-between gap-3 border-b border-neutral-800 px-4 py-3">
        <div className="flex min-w-0 items-center gap-3">
          <span className="flex h-9 w-9 items-center justify-center rounded-md border border-neutral-700 bg-neutral-900 text-neutral-300">
            {icon}
          </span>
          <div className="min-w-0">
            <h2 className="truncate text-sm font-semibold text-neutral-100">{title}</h2>
            <p className="truncate text-xs text-neutral-500">{subtitle}</p>
          </div>
        </div>
      </div>
      <div className="min-h-0 flex-1">{children}</div>
    </section>
  )
}

function DashboardPage() {
  const { user, logout } = useAuth()
  const alertsState = useAlerts()
  const { drones, loading: dronesLoading, error: dronesError } = useDrones()
  const { zones, loading: zonesLoading, error: zonesError } = useZones()

  const stats = useMemo(() => {
    const openAlerts = alertsState.alerts.filter(isOpenAlert)
    const criticalOpen = openAlerts.filter((alert) => alert.severity === 'critical').length
    const activeDrones = drones.filter((drone) => {
      const status = drone.status.toLowerCase()
      return status.includes('online') || status.includes('active')
    }).length
    const averageConfidence = alertsState.alerts.length
      ? alertsState.alerts.reduce((sum, alert) => sum + alert.confidence, 0) / alertsState.alerts.length
      : 0

    return {
      openAlerts: openAlerts.length,
      criticalOpen,
      activeDrones,
      averageConfidence,
    }
  }, [alertsState.alerts, drones])

  const mapError = dronesError || zonesError
  const selectedDrone = drones[0]
  const videoStreamName = selectedDrone?.stream_url?.split('/').filter(Boolean).pop() || 'drone-01-los'

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-100">
      <header className="sticky top-0 z-30 border-b border-neutral-800 bg-neutral-950/95 backdrop-blur">
        <div className="mx-auto flex max-w-[1800px] flex-wrap items-center justify-between gap-3 px-4 py-3">
          <div className="flex min-w-0 items-center gap-3">
            <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-md border border-emerald-500/35 bg-emerald-500/10 text-emerald-200">
              <ShieldIcon className="h-5 w-5" />
            </span>
            <div className="min-w-0">
              <h1 className="truncate text-base font-semibold text-neutral-50">GCS Surveillance IA</h1>
              <p className="truncate text-xs text-neutral-500">
                Détection et alerte locales, décision opérateur obligatoire
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="hidden rounded-md border border-neutral-800 bg-neutral-900 px-3 py-2 text-xs text-neutral-400 sm:inline-flex">
              {user?.username || 'opérateur'} · {user?.role || 'operator'}
            </span>
            <button
              type="button"
              onClick={logout}
              className="icon-text-button"
            >
              <LogOutIcon className="h-4 w-4" />
              Déconnexion
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto flex max-w-[1800px] flex-col gap-4 p-4">
        <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <MetricTile
            label="Drones actifs"
            value={`${stats.activeDrones}/${drones.length || 0}`}
            detail="Architecture prête pour 10 drones"
            tone={stats.activeDrones > 0 ? 'green' : 'neutral'}
            icon={<DroneIcon className="h-4 w-4" />}
          />
          <MetricTile
            label="Alertes ouvertes"
            value={stats.openAlerts}
            detail={`${stats.criticalOpen} critique(s) à confirmer`}
            tone={stats.criticalOpen > 0 ? 'red' : stats.openAlerts > 0 ? 'amber' : 'green'}
            icon={<AlertTriangleIcon className="h-4 w-4" />}
          />
          <MetricTile
            label="Confiance moyenne"
            value={formatConfidence(stats.averageConfidence)}
            detail="Calculée sur l’historique chargé"
            tone="neutral"
            icon={<ActivityIcon className="h-4 w-4" />}
          />
          <MetricTile
            label="Zones configurées"
            value={zones.length}
            detail="Intrusion, regroupement, sûreté"
            tone={zones.length > 0 ? 'amber' : 'neutral'}
            icon={<MapIcon className="h-4 w-4" />}
          />
        </section>

        <section className="grid min-h-[calc(100vh-220px)] gap-4 xl:grid-cols-[minmax(0,1.45fr)_minmax(360px,0.75fr)]">
          <div className="grid min-h-0 gap-4 lg:grid-rows-[auto_minmax(360px,1fr)]">
            <PanelShell
              title="Flux vidéo live"
              subtitle={selectedDrone ? `${selectedDrone.name} · ${selectedDrone.link_type}` : 'drone-01-los'}
              icon={<VideoIcon className="h-4 w-4" />}
            >
              <VideoPlayer
                streamName={videoStreamName}
                title={selectedDrone?.name || 'Caméra principale'}
                linkType={selectedDrone?.link_type || 'LOS'}
              />
            </PanelShell>

            <PanelShell
              title="Carte tactique"
              subtitle="Tuiles locales, drones et zones de détection"
              icon={<MapIcon className="h-4 w-4" />}
            >
              <MapView
                drones={drones}
                zones={zones}
                loading={dronesLoading || zonesLoading}
                error={mapError}
              />
            </PanelShell>
          </div>

          <section className="ops-panel min-h-[540px] overflow-hidden">
            <AlertPanel
              alerts={alertsState.alerts}
              connected={alertsState.connected}
              loading={alertsState.loading}
              error={alertsState.error}
              lastRealtimeAlertId={alertsState.lastRealtimeAlertId}
              acknowledgeAlert={alertsState.acknowledgeAlert}
            />
          </section>
        </section>
      </main>
    </div>
  )
}

export default DashboardPage
