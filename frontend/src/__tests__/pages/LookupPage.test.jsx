import { describe, it, expect } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { http, HttpResponse } from 'msw'
import { server } from '../msw/server'
import { renderWithProviders, staffUser } from '../utils'
import AutoresPage from '@/pages/staff/AutoresPage'
import GenerosPage from '@/pages/staff/GenerosPage'
import TurmasPage from '@/pages/staff/TurmasPage'

describe('Lookup pages (Autores/Generos/Turmas)', () => {
  it('lists autores', async () => {
    server.use(
      http.get('*/api/staff/autores/', () => HttpResponse.json([{ id: 1, nome: 'Machado de Assis' }]))
    )
    renderWithProviders(<AutoresPage />, { user: staffUser })
    expect(await screen.findByText('Machado de Assis')).toBeInTheDocument()
  })

  it('lists generos', async () => {
    server.use(
      http.get('*/api/staff/generos/', () => HttpResponse.json([{ id: 1, nome: 'Romance' }]))
    )
    renderWithProviders(<GenerosPage />, { user: staffUser })
    expect(await screen.findByText('Romance')).toBeInTheDocument()
  })

  it('lists turmas', async () => {
    server.use(
      http.get('*/api/staff/turmas/', () =>
        HttpResponse.json([{ id: 1, nome: '1A', exibe_conteudo_explicito: false }])
      )
    )
    renderWithProviders(<TurmasPage />, { user: staffUser })
    expect(await screen.findByText('1A')).toBeInTheDocument()
  })

  it('creates a new autor via the drawer', async () => {
    let createdNome = null
    server.use(
      http.get('*/api/staff/autores/', () => HttpResponse.json([{ id: 1, nome: 'Machado de Assis' }])),
      http.post('*/api/staff/autores/', async ({ request }) => {
        const body = await request.json()
        createdNome = body.nome
        return HttpResponse.json({ id: 2, nome: body.nome }, { status: 201 })
      })
    )

    renderWithProviders(<AutoresPage />, { user: staffUser })
    await screen.findByText('Machado de Assis')

    await userEvent.click(screen.getByRole('button', { name: /Novo/i }))
    // O drawer abre com o input de nome (autoFocus) além do campo de busca.
    await screen.findByRole('button', { name: 'Criar' })
    const nomeInput = document.activeElement
    await userEvent.type(nomeInput, 'Clarice Lispector')
    await userEvent.click(screen.getByRole('button', { name: 'Criar' }))

    await waitFor(() => expect(createdNome).toBe('Clarice Lispector'))
  })
})
