import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { staffResenhas } from '@/api/staff'
import DataTable from '@/components/staff/DataTable'
import ConfirmDialog from '@/components/staff/ConfirmDialog'
import StarRating from '@/components/resenhas/StarRating'

export default function ResenhasPage() {
  const qc = useQueryClient()
  const [q, setQ] = useState('')
  const [search, setSearch] = useState('')
  const [deleteTarget, setDeleteTarget] = useState(null)

  const { data = [], isLoading } = useQuery({
    queryKey: ['staff-resenhas', search],
    queryFn: () => staffResenhas.list({ q: search }),
  })

  const deleteMutation = useMutation({
    mutationFn: () => staffResenhas.delete(deleteTarget.id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['staff-resenhas'] })
      setDeleteTarget(null)
    },
    onError: (err) => alert(err.response?.data?.detail || 'Erro ao excluir.'),
  })

  const columns = [
    { key: 'livro', label: 'Livro', render: (row) => row.livro?.titulo ?? '—' },
    { key: 'aluno_nome', label: 'Aluno' },
    { key: 'nota', label: 'Nota', render: (row) => <StarRating value={row.nota} readonly size="sm" /> },
    {
      key: 'texto',
      label: 'Comentário',
      render: (row) => row.texto
        ? <span className="line-clamp-1 max-w-xs">{row.texto}</span>
        : <span className="text-muted-foreground text-xs">—</span>,
    },
    {
      key: 'data_criacao',
      label: 'Data',
      render: (row) => new Date(row.data_criacao).toLocaleDateString('pt-BR'),
    },
  ]

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-foreground">Resenhas</h1>
      </div>

      <DataTable
        columns={columns}
        data={data}
        isLoading={isLoading}
        searchPlaceholder="Buscar por livro ou aluno..."
        searchValue={q}
        onSearchChange={setQ}
        onSearch={() => setSearch(q)}
        onDelete={(row) => setDeleteTarget(row)}
      />

      <ConfirmDialog
        open={!!deleteTarget}
        title="Excluir resenha"
        description="Tem certeza que deseja excluir esta resenha?"
        onConfirm={() => deleteMutation.mutate()}
        onCancel={() => setDeleteTarget(null)}
        isLoading={deleteMutation.isPending}
      />
    </div>
  )
}
