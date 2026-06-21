import { createContext, useContext, useEffect, useState, useCallback } from 'react'
import { getMe, login as apiLogin, logout as apiLogout } from '@/api/auth'

export const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  const loadUser = useCallback(async () => {
    try {
      const me = await getMe()
      setUser(me)
    } catch {
      setUser(null)
      apiLogout()
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    if (localStorage.getItem('access_token')) {
      loadUser()
    } else {
      setIsLoading(false)
    }

    const handleLogout = () => {
      apiLogout()
      setUser(null)
    }
    window.addEventListener('auth:logout', handleLogout)
    return () => window.removeEventListener('auth:logout', handleLogout)
  }, [loadUser])

  const login = async (username, password) => {
    await apiLogin(username, password)
    await loadUser()
  }

  const logout = () => {
    apiLogout()
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
