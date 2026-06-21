import { describe, it, expect, beforeEach } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { http, HttpResponse } from 'msw'
import { server } from '../msw/server'
import { makeAluno } from '../msw/handlers'
import { renderWithProviders, staffUser } from '../utils'
import AlunosPage from '@/pages/staff/AlunosPage'

describe('AlunosPage (staff)', () => {
  beforeEach(() => {
    server.use(
      http.get('*/api/staff/alunos/', () =>
        HttpResponse.json([makeAluno({ id: 3, nome_completo: 'Ana Souza', matricula: '001' })])
      )
    )
  })

  it('lists students', async () => {
    renderWithProviders(<AlunosPage />, { user: staffUser })
    expect(await screen.findByText('Ana Souza')).toBeInTheDocument()
    expect(screen.getByText('001')).toBeInTheDocument()
  })

  it('opens the create drawer with the form fields', async () => {
    renderWithProviders(<AlunosPage />, { user: staffUser })
    await screen.findByText('Ana Souza')
    await userEvent.click(screen.getByRole('button', { name: /Novo aluno/i }))
    expect(await screen.findByText('Matrícula *')).toBeInTheDocument()
    expect(screen.getByText('Usuário *')).toBeInTheDocument()
  })

  it('deletes a student (and warns the user is removed too)', async () => {
    let deleted = false
    server.use(
      http.delete('*/api/staff/alunos/3/', () => {
        deleted = true
        return new HttpResponse(null, { status: 204 })
      })
    )

    renderWithProviders(<AlunosPage />, { user: staffUser })
    await screen.findByText('Ana Souza')

    await userEvent.click(screen.getByTitle('Excluir'))
    expect(await screen.findByText('Excluir aluno')).toBeInTheDocument()
    await userEvent.click(screen.getByRole('button', { name: 'Confirmar' }))

    await waitFor(() => expect(deleted).toBe(true))
  })
})
