import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import SearchCombobox from '@/components/ui/SearchCombobox'

const items = [
  { id: 1, label: 'Ana Souza', sublabel: '001' },
  { id: 2, label: 'Bruno Lima', sublabel: '002' },
]

describe('SearchCombobox', () => {
  it('renders the placeholder', () => {
    render(<SearchCombobox items={items} value="" onChange={() => {}} placeholder="Buscar aluno..." />)
    expect(screen.getByPlaceholderText('Buscar aluno...')).toBeInTheDocument()
  })

  it('filters items by query and selects with string id', async () => {
    const onChange = vi.fn()
    render(<SearchCombobox items={items} value="" onChange={onChange} placeholder="Buscar..." />)
    const input = screen.getByPlaceholderText('Buscar...')
    await userEvent.click(input)
    await userEvent.type(input, 'Bruno')
    await userEvent.click(screen.getByText('Bruno Lima'))
    expect(onChange).toHaveBeenCalledWith('2')
  })

  it('offers a create option when allowCreate and no match', async () => {
    const onCreateNew = vi.fn()
    render(
      <SearchCombobox
        items={items}
        value=""
        onChange={() => {}}
        placeholder="Buscar..."
        allowCreate
        onCreateNew={onCreateNew}
      />
    )
    const input = screen.getByPlaceholderText('Buscar...')
    await userEvent.click(input)
    await userEvent.type(input, 'Inexistente')
    const createBtn = screen.getByText(/Criar/)
    await userEvent.click(createBtn)
    expect(onCreateNew).toHaveBeenCalledWith('Inexistente')
  })
})
