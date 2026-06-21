import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import LivroCard from '@/components/livros/LivroCard'

const livro = {
  id: 1,
  titulo: 'Dom Casmurro',
  autor: { nome: 'Machado de Assis' },
  genero: { nome: 'Romance' },
  capa: null,
  disponivel: true,
}

function renderCard(props = livro) {
  return render(
    <MemoryRouter>
      <LivroCard livro={props} />
    </MemoryRouter>
  )
}

describe('LivroCard', () => {
  it('renders the title', () => {
    renderCard()
    expect(screen.getAllByText('Dom Casmurro').length).toBeGreaterThan(0)
  })

  it('renders the author', () => {
    renderCard()
    expect(screen.getByText('Machado de Assis')).toBeInTheDocument()
  })

  it('links to the correct book detail page', () => {
    renderCard()
    const link = screen.getByRole('link')
    expect(link).toHaveAttribute('href', '/livros/1')
  })

  it('renders the cover image when capa is provided', () => {
    renderCard({ ...livro, capa: '/media/capas/dom.jpg' })
    const img = screen.getByRole('img')
    expect(img).toHaveAttribute('src', '/media/capas/dom.jpg')
    expect(img).toHaveAttribute('alt', 'Dom Casmurro')
  })
})
