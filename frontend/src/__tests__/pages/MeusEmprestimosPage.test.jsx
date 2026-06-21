import { describe, it, expect, beforeEach } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { http, HttpResponse } from 'msw'
import { server } from '../msw/server'
import { makeEmprestimo, makeReserva } from '../msw/handlers'
import { renderWithProviders, alunoUser } from '../utils'
import MeusEmprestimosPage from '@/pages/MeusEmprestimosPage'

describe('MeusEmprestimosPage (aluno)', () => {
  beforeEach(() => {
    server.use(
      http.get('*/api/meus-emprestimos/', () =>
        HttpResponse.json({
          emprestimos: [makeEmprestimo({ id: 5, status: 'ABERTO' })],
          reservas: [makeReserva({ id: 9, status: 'ATIVA' })],
        })
      )
    )
  })

  it('renders loans and reservations sections', async () => {
    renderWithProviders(<MeusEmprestimosPage />, { user: alunoUser })
    expect(await screen.findByText('Meus Empréstimos')).toBeInTheDocument()
    expect(screen.getByText('Minhas Reservas')).toBeInTheDocument()
    expect(screen.getAllByText('Dom Casmurro').length).toBeGreaterThan(0)
  })

  it('renews an open loan', async () => {
    let renovado = false
    server.use(
      http.post('*/api/emprestimos/5/renovar/', () => {
        renovado = true
        return HttpResponse.json(makeEmprestimo({ id: 5, status: 'ABERTO' }))
      })
    )

    renderWithProviders(<MeusEmprestimosPage />, { user: alunoUser })
    await screen.findByText('Meus Empréstimos')

    await userEvent.click(screen.getByRole('button', { name: /Renovar/i }))
    await waitFor(() => expect(renovado).toBe(true))
  })

  it('cancels an active reservation', async () => {
    let cancelado = false
    server.use(
      http.post('*/api/minhas-reservas/9/cancelar/', () => {
        cancelado = true
        return HttpResponse.json({ status: 'cancelada' })
      })
    )

    renderWithProviders(<MeusEmprestimosPage />, { user: alunoUser })
    await screen.findByText('Minhas Reservas')

    await userEvent.click(screen.getByRole('button', { name: /Cancelar/i }))
    await waitFor(() => expect(cancelado).toBe(true))
  })
})
