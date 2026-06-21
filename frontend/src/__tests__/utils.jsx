import { render } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { vi } from 'vitest'
import { AuthContext } from '@/auth/AuthContext'

export const staffUser = {
  id: 1,
  username: 'staff',
  first_name: 'Staff',
  is_staff: true,
  has_aluno_perfil: false,
}

export const alunoUser = {
  id: 2,
  username: 'ana',
  first_name: 'Ana',
  is_staff: false,
  has_aluno_perfil: true,
  matricula: '001',
}

function makeClient() {
  return new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })
}

/**
 * Renderiza `ui` com QueryClient, Router e AuthContext simulados.
 *
 * options:
 *   user      objeto de usuário (default null = não autenticado)
 *   isLoading estado de carregamento do auth (default false)
 *   route     rota inicial do MemoryRouter (default '/')
 *   path      se informado, monta <Routes><Route path=... element={ui} /></Routes>
 *             (necessário para páginas que usam useParams)
 */
export function renderWithProviders(ui, { user = null, isLoading = false, route = '/', path } = {}) {
  const auth = { user, isLoading, login: vi.fn(), logout: vi.fn() }
  const client = makeClient()

  const tree = path ? (
    <Routes>
      <Route path={path} element={ui} />
    </Routes>
  ) : (
    ui
  )

  const result = render(
    <QueryClientProvider client={client}>
      <AuthContext.Provider value={auth}>
        <MemoryRouter initialEntries={[route]}>{tree}</MemoryRouter>
      </AuthContext.Provider>
    </QueryClientProvider>
  )
  return { ...result, queryClient: client, auth }
}
