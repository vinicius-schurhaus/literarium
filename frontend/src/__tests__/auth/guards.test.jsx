import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { AuthContext } from '@/auth/AuthContext'
import { ProtectedRoute } from '@/auth/ProtectedRoute'
import { StaffRoute } from '@/auth/StaffRoute'
import { AlunoRoute } from '@/auth/AlunoRoute'

function renderGuard(Guard, authValue, { start = '/secret' } = {}) {
  return render(
    <AuthContext.Provider value={authValue}>
      <MemoryRouter initialEntries={[start]}>
        <Routes>
          <Route element={<Guard />}>
            <Route path="/secret" element={<div>conteúdo protegido</div>} />
          </Route>
          <Route path="/login" element={<div>tela de login</div>} />
          <Route path="/home" element={<div>home</div>} />
        </Routes>
      </MemoryRouter>
    </AuthContext.Provider>
  )
}

describe('ProtectedRoute', () => {
  it('shows a spinner while loading', () => {
    const { container } = renderGuard(ProtectedRoute, { user: null, isLoading: true })
    expect(container.querySelector('.animate-spin')).toBeTruthy()
  })

  it('redirects to /login when not authenticated', () => {
    renderGuard(ProtectedRoute, { user: null, isLoading: false })
    expect(screen.getByText('tela de login')).toBeInTheDocument()
  })

  it('renders the outlet when authenticated', () => {
    renderGuard(ProtectedRoute, { user: { id: 1 }, isLoading: false })
    expect(screen.getByText('conteúdo protegido')).toBeInTheDocument()
  })
})

describe('StaffRoute', () => {
  it('redirects non-staff to /home', () => {
    renderGuard(StaffRoute, { user: { id: 1, is_staff: false } })
    expect(screen.getByText('home')).toBeInTheDocument()
  })

  it('renders the outlet for staff', () => {
    renderGuard(StaffRoute, { user: { id: 1, is_staff: true } })
    expect(screen.getByText('conteúdo protegido')).toBeInTheDocument()
  })
})

describe('AlunoRoute', () => {
  it('redirects users without aluno profile to /home', () => {
    renderGuard(AlunoRoute, { user: { id: 1, has_aluno_perfil: false } })
    expect(screen.getByText('home')).toBeInTheDocument()
  })

  it('renders the outlet for alunos', () => {
    renderGuard(AlunoRoute, { user: { id: 1, has_aluno_perfil: true } })
    expect(screen.getByText('conteúdo protegido')).toBeInTheDocument()
  })
})
