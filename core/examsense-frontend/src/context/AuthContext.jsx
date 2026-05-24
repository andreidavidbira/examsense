import { createContext, useEffect, useMemo, useState } from 'react'
import api, { ensureCsrfCookie } from '../api/axios'

export const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  // cerem backendului datele utilizatorului autentificat
  async function fetchMe() {
    try {
      const response = await api.get('/auth/me/')
      setUser(response.data)
    } catch {
      setUser(null)
    } finally {
      setIsLoading(false)
    }
  }

  // facem login si salvam utilizatorul in context
  async function login(username, password) {
    await ensureCsrfCookie()

    const response = await api.post('/auth/login/', {
      username,
      password,
    })

    setUser(response.data.user)
    return response.data
  }

  // cream un cont nou
  async function register(payload) {
    await ensureCsrfCookie()
    const response = await api.post('/auth/register/', payload)
    return response.data
  }

  // facem logout si golim utilizatorul din context chiar daca cererea esueaza
  async function logout() {
    try {
      await ensureCsrfCookie()
      await api.post('/auth/logout/')
    } catch {
    } finally {
      setUser(null)
    }
  }

  // reincarcam profilul curent dupa modificari
  async function refreshProfile() {
    await fetchMe()
  }

  useEffect(() => {
    async function initAuth() {
      try {
        await ensureCsrfCookie()
        await fetchMe()
      } catch {
        setUser(null)
        setIsLoading(false)
      }
    }

    // ascultam evenimentul global trimis cand sesiunea expira
    function handleForcedLogout() {
      setUser(null)
      setIsLoading(false)
    }

    window.addEventListener('auth:logout', handleForcedLogout)
    initAuth()

    return () => {
      window.removeEventListener('auth:logout', handleForcedLogout)
    }
  }, [])

  // expunem starea si actiunile de autentificare pentru toata aplicatia
  const value = useMemo(
    () => ({
      user,
      isAuthenticated: !!user,
      isLoading,
      login,
      register,
      logout,
      refreshProfile,
      setUser,
    }),
    [user, isLoading]
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}