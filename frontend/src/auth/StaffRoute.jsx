import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from './AuthContext'

export function StaffRoute() {
  const { user } = useAuth()

  if (!user?.is_staff) {
    return <Navigate to="/home" replace />
  }

  return <Outlet />
}
