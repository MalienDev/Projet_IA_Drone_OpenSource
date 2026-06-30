import { useState } from 'react'
import { MapContainer, TileLayer, Marker, Polygon, Popup } from 'react-leaflet'
import L from 'leaflet'
import { useDrones } from '../hooks/useDrones'
import { useZones } from '../hooks/useZones'

// Fix for default marker icons in react-leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
})

function MapView() {
  const { drones, loading: dronesLoading, error: dronesError } = useDrones()
  const { zones, loading: zonesLoading, error: zonesError } = useZones()
  const [mapCenter] = useState<[number, number]>([48.8566, 2.3522]) // Paris par défaut

  if (dronesLoading || zonesLoading) {
    return (
      <div className="h-96 w-full flex items-center justify-center bg-gray-700">
        <p className="text-gray-300">Loading map data...</p>
      </div>
    )
  }

  if (dronesError || zonesError) {
    return (
      <div className="h-96 w-full flex items-center justify-center bg-gray-700">
        <p className="text-red-400">{dronesError || zonesError}</p>
      </div>
    )
  }

  return (
    <div className="h-96 w-full">
      <MapContainer center={mapCenter} zoom={13} style={{ height: '100%', width: '100%' }}>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        {/* Drone markers */}
        {drones.map((drone) => (
          <Marker
            key={drone.id}
            position={[48.8566, 2.3522]} // Position par défaut, à remplacer par GPS réel
          >
            <Popup>
              <div>
                <h3 className="font-bold">{drone.name}</h3>
                <p>Status: {drone.status}</p>
                <p>Link: {drone.link_type}</p>
              </div>
            </Popup>
          </Marker>
        ))}

        {/* Zone polygons */}
        {zones.map((zone) => {
          const coordinates = zone.polygon_geojson?.coordinates?.[0] || []
          const latLngs = coordinates.map((coord: number[]) => [coord[1], coord[0]])
          
          return (
            <Polygon
              key={zone.id}
              positions={latLngs}
              pathOptions={{
                color: zone.zone_type === 'INTRUSION' ? 'red' : 
                       zone.zone_type === 'CROWD' ? 'orange' : 'green',
                fillColor: zone.zone_type === 'INTRUSION' ? 'red' : 
                          zone.zone_type === 'CROWD' ? 'orange' : 'green',
                fillOpacity: 0.2,
              }}
            >
              <Popup>
                <div>
                  <h3 className="font-bold">{zone.name}</h3>
                  <p>Type: {zone.zone_type}</p>
                </div>
              </Popup>
            </Polygon>
          )
        })}
      </MapContainer>
    </div>
  )
}

export default MapView
