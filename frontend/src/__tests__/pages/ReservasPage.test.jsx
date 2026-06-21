import { describe, it, expect, beforeEach } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { http, HttpResponse } from 'msw'
import { server } from '../msw/server'
import { makeReserva } from '../msw/handlers'
import { renderWithProviders, staffUser } from '../utils'
import ReservasPage from '@/pages/staff/ReservasPage'

describe('ReservasPage (staff)', () => {
  beforeEach(() => {
    server.use(
      http.get('*/api/staff/reservas/', () =>
        HttpResponse.json([makeReserva({ id: 9, status: 'ATIVA', aluno_nome: 'Ana Souza' })])
      )
    )
  })

  it('lists active reservations', async () => {
    renderWithProviders(<ReservasPage />, { user: staffUser })
    expect(await screen.findByText('Dom Casmurro')).toBeInTheDocument()
    expect(screen.getByText('ATIVA')).toBeInTheDocument()
  })

  it('cancels a reservation through the confirm dialog', async () => {
    let cancelada = false
    server.use(
      http.post('*/api/staff/reservas/9/cancelar/', () => {
        cancelada = true
        return HttpResponse.json(makeReserva({ id: 9, status: 'CANCELADA' }))
      })
    )

    renderWithProviders(<ReservasPage />, { user: staffUser })
    await screen.findByText('Dom Casmurro')

    await userEvent.click(screen.getByRole('button', { name: /Cancelar/i }))
    expect(await screen.findByText('Cancelar reserva')).toBeInTheDocument()
    await userEvent.click(screen.getByRole('button', { name: 'Confirmar' }))

    await waitFor(() => expect(cancelada).toBe(true))
  })
})
