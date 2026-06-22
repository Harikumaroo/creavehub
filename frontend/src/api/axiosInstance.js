import axios from 'axios'
import { API_BASE, TOKEN_KEYS, ENDPOINTS } from '../constants'

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
  timeout: 15000,
})

/* ── Request: attach access token ── */
api.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEYS.ACCESS)
  if (token) config.headers.Authorization = `Bearer ${token}`
  
  // Let the browser set the correct Content-Type (with boundary) for FormData
  if (config.data instanceof FormData) {
    delete config.headers['Content-Type']
  }
  
  return config
}, Promise.reject)

/* ── Response: handle 401 → refresh ── */
let refreshing = false
let queue = []

const drain = (err, token) => {
  queue.forEach((p) => (err ? p.reject(err) : p.resolve(token)))
  queue = []
}

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const orig = error.config
    if (error.response?.status !== 401 || orig._retry) return Promise.reject(error)

    if (refreshing) {
      return new Promise((resolve, reject) => queue.push({ resolve, reject }))
        .then((token) => { orig.headers.Authorization = `Bearer ${token}`; return api(orig) })
    }

    orig._retry = true
    refreshing  = true

    const refresh = localStorage.getItem(TOKEN_KEYS.REFRESH)
    if (!refresh) {
      refreshing = false
      localStorage.clear()
      window.location.replace('/auth/login')
      return Promise.reject(error)
    }

    try {
      const { data } = await axios.post(`${API_BASE}${ENDPOINTS.TOKEN_REFRESH}`, { refresh })
      /* SimpleJWT rotates token — new access is data.access */
      const newAccess = data.access || data.data?.access_token
      localStorage.setItem(TOKEN_KEYS.ACCESS, newAccess)
      api.defaults.headers.common.Authorization = `Bearer ${newAccess}`
      drain(null, newAccess)
      orig.headers.Authorization = `Bearer ${newAccess}`
      return api(orig)
    } catch (err) {
      drain(err, null)
      localStorage.clear()
      window.location.replace('/auth/login')
      return Promise.reject(err)
    } finally {
      refreshing = false
    }
  }
)

export default api
