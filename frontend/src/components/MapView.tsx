import 'leaflet/dist/leaflet.css'

import { useMemo, useState } from 'react'
import { MapContainer, Marker, Polygon, Popup, TileLayer } from 'react-leaflet'
import L from 'leaflet'
import type { Drone, Zone } from '../types'
import { getZoneTypeLabel } from '../utils/alerts'

interface MapViewProps {
  drones: Drone[]
  zones: Zone[]
  loading?: boolean
  error?: string | null
}

const tileUrl = ((import.meta as any).env?.VITE_TILE_URL as string | undefined)
  || '/tiles/styles/basic/{z}/{x}/{y}.png'

const defaultCenter: [number, number] = [12.6392, -8.0029]

function getDronePosition(index: number): [number, number] {
  const offset = index * 0.012
  return [defaultCenter[0] + offset, defaultCenter[1] + offset / 2]
}

function createDroneIcon(status: string, linkType: string) {
  const normalizedStatus = status.toLowerCase()
  const color = normalizedStatus.includes('online') || normalizedStatus.includes('active')
    ? '#22c55e'
    : normalizedStatus.includes('warning')
      ? '#f59e0b'
      : '#ef4444'

  return L.divIcon({
    className: 'drone-map-marker',
    html: `
      <span class="drone-map-marker__pulse" style="background:${color}"></span>
      <span class="drone-map-marker__body" style="border-color:${color}">
        <span>${linkType}</span>
      </span>
    `,
    iconSize: [42, 42],
    iconAnchor: [21, 21],
  })
}

function getZoneColor(zoneType: string) {
  switch (zoneType) {
    case 'INTRUSION':
      return '#ef4444'
    case 'CROWD':
      return '#f59e0b'
    case 'SAFE':
      return '#22c55e'
    default:
      return '#a3a3a3'
  }
}

function toLatLngs(zone: Zone): [number, number][] {
  const coordinates = zone.polygon_geojson?.coordinates?.[0] || []
  return coordinates
    .filter((coord: number[]) => coord.length >= 2)
    .map((coord: number[]) => [coord[1], coord[0]])
}

function MapView({ drones, zones, loading = false, error = null }: MapViewProps) {
  const [mapCenter] = useState<[number, number]>(defaultCenter)

  const zonePolygons = useMemo(
    () => zones.map((zone) => ({ zone, latLngs: toLatLngs(zone) })),
    [zones],
  )

  if (loading) {
    return (
      <div className="map-shell flex items-center justify-center">
        <p className="text-sm text-neutral-300">Chargement de la carte opérationnelle...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="map-shell flex items-center justify-center border border-red-500/30 bg-red-950/20">
        <p className="max-w-sm text-center text-sm text-red-200">{error}</p>
      </div>
    )
  }

  return (
    <div className="map-shell">
      <MapContainer
        center={mapCenter}
        zoom={12}
        scrollWheelZoom
        style={{ height: '100%', width: '100%' }}
      >
        <TileLayer attribution="Tuiles OSM locales" url={tileUrl} />

        {drones.map((drone, index) => (
          <Marker
            key={drone.id}
            position={getDronePosition(index)}
            icon={createDroneIcon(drone.status, drone.link_type)}
          >
            <Popup>
              <div className="space-y-1 text-sm">
                <h3 className="font-semibold">{drone.name}</h3>
                <p>Statut : {drone.status}</p>
                <p>Liaison : {drone.link_type}</p>
                <p className="max-w-56 truncate">Flux : {drone.stream_url}</p>
              </div>
            </Popup>
          </Marker>
        ))}

        {zonePolygons.map(({ zone, latLngs }) => {
          const color = getZoneColor(zone.zone_type)
          if (latLngs.length < 3) return null

          return (
            <Polygon
              key={zone.id}
              positions={latLngs}
              pathOptions={{
                color,
                fillColor: color,
                fillOpacity: 0.2,
                weight: 2,
              }}
            >
              <Popup>
                <div className="space-y-1 text-sm">
                  <h3 className="font-semibold">{zone.name}</h3>
                  <p>Type : {getZoneTypeLabel(zone.zone_type)}</p>
                  {zone.rules_json?.threshold && <p>Seuil : {zone.rules_json.threshold}</p>}
                </div>
              </Popup>
            </Polygon>
          )
        })}
      </MapContainer>

      <div className="pointer-events-none absolute left-3 top-3 rounded-md border border-neutral-700/80 bg-neutral-950/85 px-3 py-2 text-xs text-neutral-200 shadow-lg">
        <div className="font-medium text-neutral-100">Carte locale</div>
        <div className="mt-1 text-neutral-400">{drones.length} drone(s), {zones.length} zone(s)</div>
      </div>
    </div>
  )
}

export default MapView
