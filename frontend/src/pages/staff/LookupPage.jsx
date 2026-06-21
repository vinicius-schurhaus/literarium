import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus } from 'lucide-react'
import DataTable from '@/components/staff/DataTable'
import ConfirmDialog from '@/components/staff/ConfirmDialog'
import Drawer from '@/components/ui/Drawer'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

export default function LookupPage({ title, queryKey, api }) {
  const qc = useQueryClient()
  const [drawerOpen, setDrawerOpen] = useState(false)
  const [editing, setEditing] = useState(null)
  const [nome, setNome] = useState('')
  const [deleteTarget, setDeleteTarget] = useState(null)
  const [formError, setFormError] = useState('')
  const [q, setQ] = useState('')

  const { data = [], isLoading } = useQuery({
    queryKey: [queryKey],
    queryFn: api.list,
  })

  const filtered = q
    ? data.filter((item) => item.nome.toLowerCase().includes(q.toLowerCase()))
    : data

  const saveMutation = useMutation({
    mutationFn: (data) => editing ? api.update(editing.id, data) : api.create(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: [queryKey] })
      setDrawerOpen(false)
      setEditing(null)
      setNome('')
      setFormError('')
    },
    onError: (err) => setFormError(err.response?.data?.nome?.[0] || 'Erro ao salvar.'),
  })

  const deleteMutation = useMutation({
    mutationFn: () => api.delete(deleteTarget.id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: [queryKey] })
      setDeleteTarget(null)
    },
    onError: (err) => alert(err.response?.data?.detail || 'Erro ao excluir.'),
  })

  const openCreate = () => { setEditing(null); setNome(''); setFormError(''); setDrawerOpen(true) }
  const openEdit = (row) => { setEditing(row); setNome(row.nome); setFormError(''); setDrawerOpen(true) }
  const closeDrawer = () => { setDrawerOpen(false); setEditing(null); setNome(''); setFormError('') }
  const handleSave = (e) => { e.preventDefault(); saveMutation.mutate({ nome }) }

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-foreground">{title}</h1>
        <Button size="sm" onClick={openCreate}>
          <Plus className="mr-1.5 h-4 w-4" />
          Novo
        </Button>
      </div>

      <DataTable
        columns={[{ key: 'nome', label: 'Nome' }]}
        data={filtered}
        isLoading={isLoading}
        searchPlaceholder="Buscar..."
        searchValue={q}
        onSearchChange={setQ}
        onSearch={() => {}}
        onEdit={openEdit}
        onDelete={(row) => setDeleteTarget(row)}
      />

      <Drawer
        open={drawerOpen}
        onClose={closeDrawer}
        title={editing ? `Editar ${title.toLowerCase()}` : `Novo ${title.toLowerCase()}`}
        width="lg"
      >
        <form onSubmit={handleSave} className="space-y-4">
          <div className="space-y-1.5">
            <Label>Nome</Label>
            <Input value={nome} onChange={(e) => setNome(e.target.value)} autoFocus required />
            {formError && <p className="text-xs text-red-500">{formError}</p>}
          </div>
          <div className="flex gap-2 pt-2">
            <Button type="submit" disabled={saveMutation.isPending}>
              {saveMutation.isPending ? 'Salvando...' : editing ? 'Salvar' : 'Criar'}
            </Button>
            <Button type="button" variant="outline" onClick={closeDrawer}>
              Cancelar
            </Button>
          </div>
        </form>
      </Drawer>

      <ConfirmDialog
        open={!!deleteTarget}
        title="Excluir item"
        description={`Tem certeza que deseja excluir "${deleteTarget?.nome}"?`}
        onConfirm={() => deleteMutation.mutate()}
        onCancel={() => setDeleteTarget(null)}
        isLoading={deleteMutation.isPending}
      />
    </div>
  )
}
