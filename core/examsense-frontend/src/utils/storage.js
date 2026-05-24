const ACCESS_TOKEN_KEY = 'access_token'
const REFRESH_TOKEN_KEY = 'refresh_token'

// centralizam aici operatiile de baza pentru tokenurile salvate local
export const storage = {
  getAccessToken() {
    return localStorage.getItem(ACCESS_TOKEN_KEY)
  },

  setAccessToken(token) {
    localStorage.setItem(ACCESS_TOKEN_KEY, token)
  },

  removeAccessToken() {
    localStorage.removeItem(ACCESS_TOKEN_KEY)
  },

  getRefreshToken() {
    return localStorage.getItem(REFRESH_TOKEN_KEY)
  },

  setRefreshToken(token) {
    localStorage.setItem(REFRESH_TOKEN_KEY, token)
  },

  removeRefreshToken() {
    localStorage.removeItem(REFRESH_TOKEN_KEY)
  },

  // salvam ambele tokenuri deodata daca sunt disponibile
  setTokens({ access, refresh }) {
    if (access) {
      localStorage.setItem(ACCESS_TOKEN_KEY, access)
    }

    if (refresh) {
      localStorage.setItem(REFRESH_TOKEN_KEY, refresh)
    }
  },

  // stergem complet datele de autentificare salvate local
  clearAuth() {
    localStorage.removeItem(ACCESS_TOKEN_KEY)
    localStorage.removeItem(REFRESH_TOKEN_KEY)
  },
}