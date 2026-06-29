// Types communs pour le frontend

export interface Drone {
  id: string
  name: string
  stream_url: string
  link_type: 'LOS' | 'BLOS'
  status: string
  created_at: string
  updated_at?: string
}

export interface Zone {
  id: string
  name: string
  polygon_geojson: any
  zone_type: 'INTRUSION' | 'CROWD' | 'SAFE'
  rules_json?: any
  created_at: string
  updated_at?: string
}

export interface Event {
  id: string
  alert_id: string
  timestamp: string
  drone_id: string
  event_type: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  confidence: number
  bbox: number[]
  track_id?: string
  zone_id?: string
  geo?: { lat: number | null; lon: number | null }
  snapshot_path?: string
  clip_path?: string
  requires_operator_ack: boolean
  acknowledged_by?: string
  acknowledged_at?: string
  created_at: string
}

export interface Operator {
  username: string
  role: string
  created_at: string
  updated_at?: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
  username: string
  role: string
}

export interface AlertWebSocketMessage {
  alert_id: string
  timestamp: string
  drone_id: string
  type: string
  severity: string
  confidence: number
  bbox: number[]
  track_id?: string
  zone_id?: string
  geo?: { lat: number | null; lon: number | null }
  snapshot_path?: string
  clip_path?: string
  requires_operator_ack: boolean
  acknowledged_by?: string | null
  acknowledged_at?: string | null
}
