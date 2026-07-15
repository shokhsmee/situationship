import axios from 'axios'

/**
 * Single axios instance. The JWT is injected from localStorage on every
 * request; a 401 clears it so the router guard can bounce to Home.
 */
const http = axios.create({
  baseURL: '/api/v1',
  // Bypass the ngrok-free interstitial on API calls (ignored off ngrok).
  headers: { 'ngrok-skip-browser-warning': 'true' },
})

export const TOKEN_KEY = 'situationship_token'

http.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY)
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

http.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) localStorage.removeItem(TOKEN_KEY)
    return Promise.reject(err)
  },
)

export default http
