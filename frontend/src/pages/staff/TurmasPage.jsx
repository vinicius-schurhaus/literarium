import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus } from 'lucide-react'
import DataTable from '@/components/staff/DataTable'
import ConfirmDialog from '@/components/staff/ConfirmDialog'
import Drawer from '@/components/ui/Drawer'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { staffTurmas } from '@/api/staff'

const emptyForm = { nome: '', exibe_conteudo_explicito: false }

export default function TurmasPage() {
  const qc = useQueryClient()
  const [drawerOpen, setDrawerOpen] = useState(false)
  const [editing, setEditing] = useState(null)
  const [form, setForm] = useState(emptyForm)
  const [deleteTarget, setDeleteTarget] = useState(null)
  const [formError, setFormError] = useState('')
  const [q, setQ] = useState('')

  const { data = [], isLoading } = useQuery({
    queryKey: ['staff-turmas'],
    queryFn: staffTurmas.list,
  })

  const filtered = q
    ? data.filter((t) => t.nome.toLowerCase().includes(q.toLowerCase()))
    : data

  const saveMutation = useMutation({
    mutationFn: (payload) =>
      editing ? staffTurmas.update(editing.id, payload) : staffTurmas.create(payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['staff-turmas'] })
      closeDrawer()
    },
    onError: (err) => setFormError(err.response?.data?.nome?.[0] || 'Erro ao salvar.'),
  })

  const deleteMutation = useMutation({
    mutationFn: () => staffTurmas.delete(deleteTarget.id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['staff-turmas'] })
      setDeleteTarget(null)
    },
    onError: (err) => alert(err.response?.data?.detail || 'Erro ao excluir.'),
  })

  const openCreate = () => { setEditing(null); setForm(emptyForm); setFormError(''); setDrawerOpen(true) }
  const openEdit = (row) => {
    setEditing(row)
    setForm({ nome: row.nome, exibe_conteudo_explicito: row.exibe_conteudo_explicito ?? false })
    setFormError('')
    setDrawerOpen(true)
  }
  const closeDrawer = () => { setDrawerOpen(false); setEditing(null); setForm(emptyForm); setFormError('') }
  const handleSave = (e) => { e.preventDefault(); saveMutation.mutate(form) }

  const columns = [
    { key: 'nome', label: 'Nome' },
    {
      key: 'exibe_conteudo_explicito',
      label: 'Exibe conteúdo explícito',
      render: (v) => (
        <span className={v ? 'text-green-600 font-medium' : 'text-muted-foreground'}>
          {v ? 'Sim' : 'Não'}
        </span>
      ),
    },
  ]

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-foreground">Turmas</h1>
        <Button size="sm" onClick={openCreate}>
          <Plus className="mr-1.5 h-4 w-4" />
          Nova
        </Button>
      </div>

      <DataTable
        columns={columns}
        data={filtered}
        isLoading={isLoading}
        searchPlaceholder="Buscar turma..."
        searchValue={q}
        onSearchChange={setQ}
        onSearch={() => {}}
        onEdit={openEdit}
        onDelete={(row) => setDeleteTarget(row)}
      />

      <Drawer
        open={drawerOpen}
        onClose={closeDrawer}
        title={editing ? 'Editar turma' : 'Nova turma'}
        width="lg"
      >
        <form onSubmit={handleSave} className="space-y-4">
          <div className="space-y-1.5">
            <Label>Nome</Label>
            <Input
              value={form.nome}
              onChange={(e) => setForm({ ...form, nome: e.target.value })}
              autoFocus
              required
            />
            {formError && <p className="text-xs text-red-500">{formError}</p>}
          </div>

          <div className="flex items-center gap-3">
            <input
              id="exibe_conteudo_explicito"
              type="checkbox"
              className="h-4 w-4 rounded border-border accent-primary cursor-pointer"
              checked={form.exibe_conteudo_explicito}
              onChange={(e) => setForm({ ...form, exibe_conteudo_explicito: e.target.checked })}
            />
            <Label htmlFor="exibe_conteudo_explicito" className="cursor-pointer">
              Exibe conteúdo explícito
            </Label>
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
        title="Excluir turma"
        description={`Tem certeza que deseja excluir "${deleteTarget?.nome}"?`}
        onConfirm={() => deleteMutation.mutate()}
        onCancel={() => setDeleteTarget(null)}
        isLoading={deleteMutation.isPending}
      />
    </div>
  )
}
