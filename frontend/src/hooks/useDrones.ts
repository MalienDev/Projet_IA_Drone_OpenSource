import { useState, useEffect } from 'react'
import { dronesApi } from '../services/api'
import type { Drone } from '../types'

export function useDrones() {
  const [drones, setDrones] = useState<Drone[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

  const fetchDrones = async () => {
    try {
      setLoading(true)
      const data = await dronesApi.list()
      setDrones(data)
      setError(null)
    } catch (err) {
      setError('Failed to fetch drones. Make sure the backend is running and database is seeded.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDrones()
  }, [])

  return { drones, loading, error, refetch: fetchDrones }
}
