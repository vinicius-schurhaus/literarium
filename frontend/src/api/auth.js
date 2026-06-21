import axios from 'axios'
import api from './client'

export async function login(username, password) {
  const { data } = await axios.post('/api/auth/token/', { username, password })
  localStorage.setItem('access_token', data.access)
  localStorage.setItem('refresh_token', data.refresh)
}

export function logout() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
}

export async function getMe() {
  const { data } = await api.get('/auth/me/')
  return data
}

export async function changePassword(old_password, new_password1, new_password2) {
  const { data } = await api.post('/auth/change-password/', { old_password, new_password1, new_password2 })
  return data
}
