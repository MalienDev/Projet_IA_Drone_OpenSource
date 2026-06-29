import { useState, useEffect } from 'react'
import { authApi } from '../services/api'
import type { Operator } from '../types'

export function useAuth() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false)
  const [user, setUser] = useState<Operator | null>(null)
  const [loading, setLoading] = useState<boolean>(true)

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (token) {
      // Vérifier si le token est valide en récupérant l'utilisateur
      authApi.getCurrentUser()
        .then((userData) => {
          setUser(userData)
          setIsAuthenticated(true)
        })
        .catch(() => {
          localStorage.removeItem('access_token')
          setIsAuthenticated(false)
        })
        .finally(() => {
          setLoading(false)
        })
    } else {
      setLoading(false)
    }
  }, [])

  const login = async (username: string, password: string) => {
    const response = await authApi.login({ username, password })
    setUser({ username: response.username, role: response.role, created_at: '' })
    setIsAuthenticated(true)
    localStorage.setItem('username', response.username)
  }

  const logout = () => {
    authApi.logout()
    setUser(null)
    setIsAuthenticated(false)
    localStorage.removeItem('username')
  }

  return { isAuthenticated, user, loading, login, logout }
}
