import axios from 'axios'
import { API_BASE_URL } from '../utils/constants'

const client = axios.create({
  baseURL: API_BASE_URL,
})

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        try {
          const res = await axios.post(`${API_BASE_URL}/auth/refresh/`, {
            refresh: refreshToken,
          })
          localStorage.setItem('access_token', res.data.access)
          if (res.data.refresh) {
            localStorage.setItem('refresh_token', res.data.refresh)
          }
          originalRequest.headers.Authorization = `Bearer ${res.data.access}`
          return client(originalRequest)
        } catch {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          window.location.href = '/login'
        }
      }
    }
    return Promise.reject(error)
  }
)

export default client
