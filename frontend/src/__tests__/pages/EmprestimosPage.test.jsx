import { describe, it, expect, beforeEach } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { http, HttpResponse } from 'msw'
import { server } from '../msw/server'
import { makeEmprestimo } from '../msw/handlers'
import { renderWithProviders, staffUser } from '../utils'
import EmprestimosPage from '@/pages/staff/EmprestimosPage'

describe('EmprestimosPage (staff)', () => {
  beforeEach(() => {
    server.use(
      http.get('*/api/staff/emprestimos/', () =>
        HttpResponse.json([
          makeEmprestimo({ id: 5, status: 'ABERTO', aluno_nome: 'Ana Souza' }),
        ])
      )
    )
  })

  it('lists loans with book and student', async () => {
    renderWithProviders(<EmprestimosPage />, { user: staffUser })
    expect(await screen.findByText('Dom Casmurro')).toBeInTheDocument()
    expect(screen.getByText('Ana Souza')).toBeInTheDocument()
    // "Em aberto" aparece no badge de status e na opção do filtro <select>.
    expect(screen.getAllByText('Em aberto').length).toBeGreaterThan(0)
  })

  it('returns a loan via the "Devolver" action', async () => {
    let devolvido = false
    server.use(
      http.post('*/api/staff/emprestimos/5/devolver/', () => {
        devolvido = true
        return HttpResponse.json(makeEmprestimo({ id: 5, status: 'DEVOLVIDO' }))
      })
    )

    renderWithProviders(<EmprestimosPage />, { user: staffUser })
    await screen.findByText('Dom Casmurro')

    await userEvent.click(screen.getByRole('button', { name: /Devolver/i }))
    expect(await screen.findByText('Registrar devolução')).toBeInTheDocument()
    await userEvent.click(screen.getByRole('button', { name: 'Confirmar' }))

    await waitFor(() => expect(devolvido).toBe(true))
  })
})
