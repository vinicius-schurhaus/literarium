import { describe, it, expect, beforeEach } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { http, HttpResponse } from 'msw'
import { server } from '../msw/server'
import { makeResenha } from '../msw/handlers'
import { renderWithProviders, staffUser } from '../utils'
import ResenhasPage from '@/pages/staff/ResenhasPage'

describe('ResenhasPage (staff)', () => {
  beforeEach(() => {
    server.use(
      http.get('*/api/staff/resenhas/', () =>
        HttpResponse.json([
          makeResenha({ id: 4, aluno_nome: 'Ana Souza', texto: 'Muito bom' }),
        ])
      )
    )
  })

  it('lists reviews with book and student', async () => {
    renderWithProviders(<ResenhasPage />, { user: staffUser })
    expect(await screen.findByText('Dom Casmurro')).toBeInTheDocument()
    expect(screen.getByText('Ana Souza')).toBeInTheDocument()
    expect(screen.getByText('Muito bom')).toBeInTheDocument()
  })

  it('deletes a review', async () => {
    let deleted = false
    server.use(
      http.delete('*/api/staff/resenhas/4/', () => {
        deleted = true
        return new HttpResponse(null, { status: 204 })
      })
    )

    renderWithProviders(<ResenhasPage />, { user: staffUser })
    await screen.findByText('Dom Casmurro')

    await userEvent.click(screen.getByTitle('Excluir'))
    expect(await screen.findByText('Excluir resenha')).toBeInTheDocument()
    await userEvent.click(screen.getByRole('button', { name: 'Confirmar' }))

    await waitFor(() => expect(deleted).toBe(true))
  })
})
