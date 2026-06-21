import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ConfirmDialog from '@/components/staff/ConfirmDialog'

describe('ConfirmDialog', () => {
  it('renders nothing when closed', () => {
    const { container } = render(<ConfirmDialog open={false} title="X" />)
    expect(container).toBeEmptyDOMElement()
  })

  it('shows title and description when open', () => {
    render(<ConfirmDialog open title="Excluir livro" description="Tem certeza?" />)
    expect(screen.getByText('Excluir livro')).toBeInTheDocument()
    expect(screen.getByText('Tem certeza?')).toBeInTheDocument()
  })

  it('calls onConfirm and onCancel', async () => {
    const onConfirm = vi.fn()
    const onCancel = vi.fn()
    render(<ConfirmDialog open title="X" onConfirm={onConfirm} onCancel={onCancel} />)
    await userEvent.click(screen.getByText('Confirmar'))
    await userEvent.click(screen.getByText('Cancelar'))
    expect(onConfirm).toHaveBeenCalled()
    expect(onCancel).toHaveBeenCalled()
  })

  it('disables buttons and shows loading label when isLoading', () => {
    render(<ConfirmDialog open title="X" isLoading />)
    const confirm = screen.getByText('Aguarde...')
    expect(confirm).toBeDisabled()
  })
})
