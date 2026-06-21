import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import StatusBadge from '@/components/emprestimos/StatusBadge'

describe('StatusBadge', () => {
  it('shows "Atrasado" when estaAtrasado is true (priority over status)', () => {
    render(<StatusBadge status="ABERTO" estaAtrasado />)
    expect(screen.getByText('Atrasado')).toBeInTheDocument()
  })

  it('shows "Devolvido" for DEVOLVIDO', () => {
    render(<StatusBadge status="DEVOLVIDO" estaAtrasado={false} />)
    expect(screen.getByText('Devolvido')).toBeInTheDocument()
  })

  it('shows "Em aberto" for ABERTO not overdue', () => {
    render(<StatusBadge status="ABERTO" estaAtrasado={false} />)
    expect(screen.getByText('Em aberto')).toBeInTheDocument()
  })
})
