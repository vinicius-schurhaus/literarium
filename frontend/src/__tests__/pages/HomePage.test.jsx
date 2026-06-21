import { describe, it, expect } from 'vitest'
import { screen } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { server } from '../msw/server'
import { makeLivro } from '../msw/handlers'
import { renderWithProviders, alunoUser } from '../utils'
import HomePage from '@/pages/HomePage'

describe('HomePage (aluno)', () => {
  it('greets the user and shows the Vestibular shelf', async () => {
    server.use(
      http.get('*/api/home/', () =>
        HttpResponse.json({
          livros_recentes: [],
          livros_populares: [],
          livros_vestibular: [makeLivro({ id: 11, titulo: 'Apostila ENEM' })],
        })
      )
    )

    renderWithProviders(<HomePage />, { user: alunoUser })

    expect(screen.getByText(/Ana/)).toBeInTheDocument()
    expect(screen.getByText('Vestibular')).toBeInTheDocument()
    expect((await screen.findAllByText('Apostila ENEM')).length).toBeGreaterThan(0)
  })
})
