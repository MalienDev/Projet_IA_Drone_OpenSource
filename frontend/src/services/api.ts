import axios from 'axios'
import type { Drone, Zone, Event, Operator, LoginRequest, TokenResponse } from '../types'

// Use relative path to leverage nginx proxy in Docker
const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || ''

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Intercepteur pour ajouter le token JWT
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Intercepteur pour gérer les erreurs d'authentification
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const authApi = {
  login: async (data: LoginRequest): Promise<TokenResponse> => {
    const response = await api.post<TokenResponse>('/api/auth/login', data)
    localStorage.setItem('access_token', response.data.access_token)
    return response.data
  },
  
  logout: () => {
    localStorage.removeItem('access_token')
  },
  
  getCurrentUser: async (): Promise<Operator> => {
    const response = await api.get<Operator>('/api/auth/me')
    return response.data
  },
}

export const dronesApi = {
  list: async (): Promise<Drone[]> => {
    const response = await api.get<Drone[]>('/api/drones')
    return response.data
  },
  
  get: async (id: string): Promise<Drone> => {
    const response = await api.get<Drone>(`/api/drones/${id}`)
    return response.data
  },
  
  create: async (data: Drone): Promise<Drone> => {
    const response = await api.post<Drone>('/api/drones', data)
    return response.data
  },
  
  update: async (id: string, data: Partial<Drone>): Promise<Drone> => {
    const response = await api.put<Drone>(`/api/drones/${id}`, data)
    return response.data
  },
  
  delete: async (id: string): Promise<void> => {
    await api.delete(`/api/drones/${id}`)
  },
}

export const zonesApi = {
  list: async (): Promise<Zone[]> => {
    const response = await api.get<Zone[]>('/api/zones')
    return response.data
  },
  
  get: async (id: string): Promise<Zone> => {
    const response = await api.get<Zone>(`/api/zones/${id}`)
    return response.data
  },
  
  create: async (data: Zone): Promise<Zone> => {
    const response = await api.post<Zone>('/api/zones', data)
    return response.data
  },
  
  update: async (id: string, data: Partial<Zone>): Promise<Zone> => {
    const response = await api.put<Zone>(`/api/zones/${id}`, data)
    return response.data
  },
  
  delete: async (id: string): Promise<void> => {
    await api.delete(`/api/zones/${id}`)
  },
}

export const eventsApi = {
  list: async (params?: {
    skip?: number
    limit?: number
    drone_id?: string
    event_type?: string
    severity?: string
    acknowledged?: boolean
    start_time?: string
    end_time?: string
  }): Promise<Event[]> => {
    const response = await api.get<Event[]>('/api/events', { params })
    return response.data
  },
  
  get: async (alertId: string): Promise<Event> => {
    const response = await api.get<Event>(`/api/events/${alertId}`)
    return response.data
  },
  
  acknowledge: async (alertId: string): Promise<Event> => {
    const response = await api.put<Event>(`/api/events/${alertId}`, {
      acknowledged_by: localStorage.getItem('username'),
      acknowledged_at: new Date().toISOString(),
    })
    return response.data
  },
}

export default api
