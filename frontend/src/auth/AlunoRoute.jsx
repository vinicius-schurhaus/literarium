import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from './AuthContext'

export function AlunoRoute() {
  const { user } = useAuth()

  if (!user?.has_aluno_perfil) {
    return <Navigate to="/home" replace />
  }

  return <Outlet />
}
