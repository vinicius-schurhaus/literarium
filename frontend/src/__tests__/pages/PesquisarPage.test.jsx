import { describe, it, expect } from 'vitest'
import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { http, HttpResponse } from 'msw'
import { server } from '../msw/server'
import { paginated, makeLivro } from '../msw/handlers'
import { renderWithProviders, alunoUser } from '../utils'
import PesquisarPage from '@/pages/PesquisarPage'

describe('PesquisarPage (aluno)', () => {
  it('shows the empty state before searching', () => {
    renderWithProviders(<PesquisarPage />, { user: alunoUser })
    expect(screen.getByText('Encontre qualquer livro do acervo')).toBeInTheDocument()
  })

  it('searches and renders results (debounced)', async () => {
    server.use(
      http.get('*/api/livros/', () =>
        HttpResponse.json(paginated([makeLivro({ id: 1, titulo: 'Dom Casmurro' })]))
      )
    )

    renderWithProviders(<PesquisarPage />, { user: alunoUser })
    await userEvent.type(screen.getByPlaceholderText('Procure por título ou autor...'), 'dom')

    expect((await screen.findAllByText('Dom Casmurro')).length).toBeGreaterThan(0)
    expect(screen.getByText(/resultado/)).toBeInTheDocument()
  })
})
