import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import DataTable from '@/components/staff/DataTable'

const columns = [
  { key: 'titulo', label: 'Título' },
  { key: 'autor', label: 'Autor', render: (row) => row.autor?.nome ?? '—' },
]

const rows = [
  { id: 1, titulo: 'Dom Casmurro', autor: { nome: 'Machado' } },
  { id: 2, titulo: 'O Cortiço', autor: { nome: 'Aluísio' } },
]

describe('DataTable', () => {
  it('shows a loading spinner when isLoading', () => {
    const { container } = render(<DataTable columns={columns} data={[]} isLoading />)
    expect(container.querySelector('.animate-spin')).toBeTruthy()
  })

  it('shows empty state when there are no rows', () => {
    render(<DataTable columns={columns} data={[]} isLoading={false} />)
    expect(screen.getByText('Nenhum item encontrado.')).toBeInTheDocument()
  })

  it('renders rows including custom column renderers', () => {
    render(<DataTable columns={columns} data={rows} isLoading={false} />)
    expect(screen.getByText('Dom Casmurro')).toBeInTheDocument()
    expect(screen.getByText('Machado')).toBeInTheDocument()
    expect(screen.getByText('Aluísio')).toBeInTheDocument()
  })

  it('accepts paginated shape ({ results })', () => {
    render(<DataTable columns={columns} data={{ results: rows }} isLoading={false} />)
    expect(screen.getByText('O Cortiço')).toBeInTheDocument()
  })

  it('calls onSearch when the search form is submitted', async () => {
    const onSearch = vi.fn()
    const onSearchChange = vi.fn()
    render(
      <DataTable
        columns={columns}
        data={rows}
        isLoading={false}
        searchValue=""
        onSearchChange={onSearchChange}
        onSearch={onSearch}
      />
    )
    await userEvent.type(screen.getByPlaceholderText('Buscar...'), 'dom{enter}')
    expect(onSearch).toHaveBeenCalled()
  })

  it('calls onEdit and onDelete for the matching row', async () => {
    const onEdit = vi.fn()
    const onDelete = vi.fn()
    render(
      <DataTable columns={columns} data={rows} isLoading={false} onEdit={onEdit} onDelete={onDelete} />
    )
    const editButtons = screen.getAllByTitle('Editar')
    const deleteButtons = screen.getAllByTitle('Excluir')
    await userEvent.click(editButtons[0])
    await userEvent.click(deleteButtons[1])
    expect(onEdit).toHaveBeenCalledWith(rows[0])
    expect(onDelete).toHaveBeenCalledWith(rows[1])
  })
})
