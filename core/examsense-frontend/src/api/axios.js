/*
ExamSense+ - API Client Configuration
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- configureaza instanta globala axios folosita in frontend
- gestioneaza automat trimiterea tokenului CSRF
- incearca refacerea sesiunii prin refresh token atunci cand access token-ul expira
- centralizeaza comunicarea sigura dintre frontend si backend
*/

import axios from 'axios'

// luam valoarea unui cookie dupa nume
function getCookie(name) {
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)

  if (parts.length === 2) {
    return parts.pop().split(';').shift()
  }

  return null
}

// configuram instanta axios folosita in tot frontendul
const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 60000,
  withCredentials: true,
})

// pastram o singura cerere de refresh activa la un moment dat
let refreshPromise = null

// cerem backendului sa seteze cookie-ul csrf
export async function ensureCsrfCookie() {
  await api.get('/auth/csrf/')
}

api.interceptors.request.use(
  (config) => {
    const csrfToken = getCookie('csrftoken')

    // daca avem token csrf, il trimitem automat in header
    if (csrfToken) {
      config.headers['X-CSRFToken'] = csrfToken
    }

    return config
  },
  (error) => Promise.reject(error)
)

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    const status = error?.response?.status
    const url = originalRequest?.url || ''

    const isRefreshCall = url.includes('/auth/refresh/')
    const isLoginCall = url.includes('/auth/login/')
    const isRegisterCall = url.includes('/auth/register/')
    const isMeCall = url.includes('/auth/me/')
    const isCsrfCall = url.includes('/auth/csrf/')

    // daca refresh-ul insusi a esuat, fortam logout in frontend
    if (isRefreshCall && status === 401) {
      window.dispatchEvent(new CustomEvent('auth:logout'))
      return Promise.reject(error)
    }

    // daca primim 401 pe o cerere normala, incercam o singura data sa refacem sesiunea
    if (
      status === 401 &&
      !originalRequest._retry &&
      !isRefreshCall &&
      !isLoginCall &&
      !isRegisterCall &&
      !isMeCall &&
      !isCsrfCall
    ) {
      originalRequest._retry = true

      try {
        await ensureCsrfCookie()

        // evitam trimiterea mai multor refresh-uri simultan
        if (!refreshPromise) {
          refreshPromise = api.post('/auth/refresh/')
        }

        await refreshPromise
        return api(originalRequest)
      } catch (refreshError) {
        window.dispatchEvent(new CustomEvent('auth:logout'))
        return Promise.reject(refreshError)
      } finally {
        refreshPromise = null
      }
    }

    return Promise.reject(error)
  }
)

export default api