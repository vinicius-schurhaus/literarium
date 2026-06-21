import axios from 'axios'

// Em produção (Netlify) defina VITE_API_URL com a URL do backend, ex.:
//   https://seuusuario.pythonanywhere.com/api
// Em desenvolvimento o fallback '/api' usa o proxy do Vite.
const API_URL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: API_URL,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true
      const refresh = localStorage.getItem('refresh_token')
      if (!refresh) {
        window.dispatchEvent(new Event('auth:logout'))
        return Promise.reject(error)
      }
      try {
        const { data } = await axios.post(`${API_URL}/auth/token/refresh/`, { refresh })
        localStorage.setItem('access_token', data.access)
        if (data.refresh) {
          localStorage.setItem('refresh_token', data.refresh)
        }
        original.headers.Authorization = `Bearer ${data.access}`
        return api(original)
      } catch {
        window.dispatchEvent(new Event('auth:logout'))
        return Promise.reject(error)
      }
    }
    return Promise.reject(error)
  }
)

export default api
