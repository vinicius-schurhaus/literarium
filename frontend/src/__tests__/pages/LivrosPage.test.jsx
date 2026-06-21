import { describe, it, expect, beforeEach } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { http, HttpResponse } from 'msw'
import { server } from '../msw/server'
import { paginated, makeLivro } from '../msw/handlers'
import { renderWithProviders, staffUser } from '../utils'
import LivrosPage from '@/pages/staff/LivrosPage'

describe('LivrosPage (staff)', () => {
  beforeEach(() => {
    server.use(
      http.get('*/api/staff/livros/', () =>
        HttpResponse.json(paginated([makeLivro({ id: 7, titulo: 'A Hora da Estrela' })]))
      )
    )
  })

  it('lists books from the API', async () => {
    renderWithProviders(<LivrosPage />, { user: staffUser })
    expect(await screen.findByText('A Hora da Estrela')).toBeInTheDocument()
  })

  it('opens the "Novo livro" drawer with the form', async () => {
    renderWithProviders(<LivrosPage />, { user: staffUser })
    await screen.findByText('A Hora da Estrela')
    await userEvent.click(screen.getByRole('button', { name: /Novo livro/i }))
    expect(await screen.findByPlaceholderText('Título do livro')).toBeInTheDocument()
  })

  it('deletes a book through the confirm dialog', async () => {
    let deleted = false
    server.use(
      http.delete('*/api/staff/livros/7/', () => {
        deleted = true
        return new HttpResponse(null, { status: 204 })
      })
    )

    renderWithProviders(<LivrosPage />, { user: staffUser })
    await screen.findByText('A Hora da Estrela')

    await userEvent.click(screen.getByTitle('Excluir'))
    expect(await screen.findByText('Excluir livro')).toBeInTheDocument()
    await userEvent.click(screen.getByRole('button', { name: 'Confirmar' }))

    await waitFor(() => expect(deleted).toBe(true))
  })
})
