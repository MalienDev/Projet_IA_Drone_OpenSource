import { useState, useEffect } from 'react'
import { zonesApi } from '../services/api'
import type { Zone } from '../types'

export function useZones() {
  const [zones, setZones] = useState<Zone[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

  const fetchZones = async () => {
    try {
      setLoading(true)
      const data = await zonesApi.list()
      setZones(data)
      setError(null)
    } catch (err) {
      setError('Failed to fetch zones. Make sure the backend is running and database is seeded.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchZones()
  }, [])

  return { zones, loading, error, refetch: fetchZones }
}
