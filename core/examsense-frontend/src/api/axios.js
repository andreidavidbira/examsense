import axios from 'axios'

function getCookie(name) {
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)

  if (parts.length === 2) {
    return parts.pop().split(';').shift()
  }

  return null
}

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 15000,
  withCredentials: true,
})

let refreshPromise = null

export async function ensureCsrfCookie() {
  await api.get('/auth/csrf/')
}

api.interceptors.request.use(
  (config) => {
    const csrfToken = getCookie('csrftoken')

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

    if (isRefreshCall && status === 401) {
      window.dispatchEvent(new CustomEvent('auth:logout'))
      return Promise.reject(error)
    }

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