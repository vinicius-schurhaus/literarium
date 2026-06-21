import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus } from 'lucide-react'
import { staffLivros } from '@/api/staff'
import DataTable from '@/components/staff/DataTable'
import ConfirmDialog from '@/components/staff/ConfirmDialog'
import Drawer from '@/components/ui/Drawer'
import LivroForm from './LivroForm'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'

export default function LivrosPage() {
  const qc = useQueryClient()
  const [q, setQ] = useState('')
  const [search, setSearch] = useState('')
  const [deleteTarget, setDeleteTarget] = useState(null)
  const [drawerOpen, setDrawerOpen] = useState(false)
  const [editId, setEditId] = useState(null)

  const { data = [], isLoading } = useQuery({
    queryKey: ['staff-livros', search],
    queryFn: () => staffLivros.list({ q: search }),
  })

  const deleteMutation = useMutation({
    mutationFn: () => staffLivros.delete(deleteTarget.id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['staff-livros'] })
      setDeleteTarget(null)
    },
    onError: (err) => alert(err.response?.data?.detail || 'Erro ao excluir.'),
  })

  const openNew = () => { setEditId(null); setDrawerOpen(true) }
  const openEdit = (row) => { setEditId(row.id); setDrawerOpen(true) }
  const closeDrawer = () => { setDrawerOpen(false); setEditId(null) }

  const handleSuccess = () => {
    qc.invalidateQueries({ queryKey: ['staff-livros'] })
    closeDrawer()
  }

  const columns = [
    {
      key: 'capa',
      label: '',
      width: 56,
      render: (row) => row.capa
        ? <img src={row.capa} alt={row.titulo} className="h-12 w-8 rounded object-cover" />
        : <div className="h-12 w-8 rounded bg-orange-50 border border-border" />,
    },
    { key: 'titulo', label: 'Título' },
    { key: 'autor', label: 'Autor', render: (row) => row.autor?.nome },
    { key: 'genero', label: 'Gênero', render: (row) => row.genero?.nome || '—' },
    { key: 'quantidade', label: 'Qtd' },
    {
      key: 'disponivel',
      label: 'Status',
      render: (row) => (
        <Badge variant={row.disponivel ? 'success' : 'secondary'}>
          {row.disponivel ? 'Disponível' : 'Indisponível'}
        </Badge>
      ),
    },
  ]

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-foreground">Livros</h1>
        <Button size="sm" onClick={openNew}>
          <Plus className="mr-1.5 h-4 w-4" />
          Novo livro
        </Button>
      </div>

      <DataTable
        columns={columns}
        data={data?.results ?? data}
        isLoading={isLoading}
        searchPlaceholder="Buscar por título ou autor..."
        searchValue={q}
        onSearchChange={setQ}
        onSearch={() => setSearch(q)}
        onEdit={openEdit}
        onDelete={(row) => setDeleteTarget(row)}
      />

      <ConfirmDialog
        open={!!deleteTarget}
        title="Excluir livro"
        description={`Tem certeza que deseja excluir "${deleteTarget?.titulo}"?`}
        onConfirm={() => deleteMutation.mutate()}
        onCancel={() => setDeleteTarget(null)}
        isLoading={deleteMutation.isPending}
      />

      <Drawer
        open={drawerOpen}
        onClose={closeDrawer}
        title={editId ? 'Editar livro' : 'Novo livro'}
        width="lg"
      >
        <LivroForm id={editId} onSuccess={handleSuccess} onCancel={closeDrawer} />
      </Drawer>
    </div>
  )
}
