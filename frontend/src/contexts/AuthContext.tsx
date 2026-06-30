import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { authApi } from '../services/api'
import type { Operator } from '../types'

interface AuthContextType {
  isAuthenticated: boolean
  user: Operator | null
  loading: boolean
  login: (username: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false)
  const [user, setUser] = useState<Operator | null>(null)
  const [loading, setLoading] = useState<boolean>(true)

  const checkAuth = async () => {
    const token = localStorage.getItem('access_token')
    if (token) {
      try {
        const userData = await authApi.getCurrentUser()
        setUser(userData)
        setIsAuthenticated(true)
      } catch {
        localStorage.removeItem('access_token')
        setIsAuthenticated(false)
      }
    }
    setLoading(false)
  }

  useEffect(() => {
    checkAuth()
  }, [])

  const login = async (username: string, password: string) => {
    const response = await authApi.login({ username, password })
    setUser({ username: response.username, role: response.role, created_at: '' })
    setIsAuthenticated(true)
    localStorage.setItem('username', response.username)
    setLoading(false)
  }

  const logout = () => {
    authApi.logout()
    setUser(null)
    setIsAuthenticated(false)
    localStorage.removeItem('username')
  }

  return (
    <AuthContext.Provider value={{ isAuthenticated, user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
