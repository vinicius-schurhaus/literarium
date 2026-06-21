import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, AlertTriangle } from 'lucide-react'
import { staffAlunos, staffTurmas } from '@/api/staff'
import DataTable from '@/components/staff/DataTable'
import ConfirmDialog from '@/components/staff/ConfirmDialog'
import Drawer from '@/components/ui/Drawer'
import SearchCombobox from '@/components/ui/SearchCombobox'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

const emptyForm = {
  username: '', first_name: '', last_name: '',
  email: '', password: '', matricula: '', turma_id: '',
}

export default function AlunosPage() {
  const qc = useQueryClient()
  const [q, setQ] = useState('')
  const [search, setSearch] = useState('')
  const [deleteTarget, setDeleteTarget] = useState(null)
  const [drawerOpen, setDrawerOpen] = useState(false)
  const [editId, setEditId] = useState(null)
  const [form, setForm] = useState(emptyForm)
  const [errors, setErrors] = useState({})
  const [showNewTurma, setShowNewTurma] = useState(false)
  const [newTurmaNome, setNewTurmaNome] = useState('')

  const { data = [], isLoading } = useQuery({
    queryKey: ['staff-alunos', search],
    queryFn: () => staffAlunos.list({ q: search }),
  })

  const { data: turmas = [] } = useQuery({
    queryKey: ['staff-turmas'],
    queryFn: staffTurmas.list,
    enabled: drawerOpen,
  })

  const { data: alunoData } = useQuery({
    queryKey: ['staff-aluno', editId],
    queryFn: () => staffAlunos.get(editId),
    enabled: !!editId,
  })

  useEffect(() => {
    if (alunoData) {
      setForm({
        username: alunoData.username || '',
        first_name: alunoData.nome_completo?.split(' ')[0] || '',
        last_name: alunoData.nome_completo?.split(' ').slice(1).join(' ') || '',
        email: alunoData.email || '',
        password: '',
        matricula: alunoData.matricula || '',
        turma_id: alunoData.turma?.id ? String(alunoData.turma.id) : '',
      })
    }
  }, [alunoData])

  const saveMutation = useMutation({
    mutationFn: () => {
      const payload = { ...form }
      if (!payload.password) delete payload.password
      payload.turma_id = payload.turma_id ? Number(payload.turma_id) : null
      return editId ? staffAlunos.update(editId, payload) : staffAlunos.create(payload)
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['staff-alunos'] })
      closeDrawer()
    },
    onError: (err) => setErrors(err.response?.data || {}),
  })

  const deleteMutation = useMutation({
    mutationFn: () => staffAlunos.delete(deleteTarget.id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['staff-alunos'] })
      setDeleteTarget(null)
    },
    onError: (err) => alert(err.response?.data?.detail || 'Erro ao excluir.'),
  })

  const criarTurmaMutation = useMutation({
    mutationFn: (nome) => staffTurmas.create({ nome }),
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: ['staff-turmas'] })
      setForm((f) => ({ ...f, turma_id: String(data.id) }))
      setShowNewTurma(false)
      setNewTurmaNome('')
    },
    onError: (err) => alert(err.response?.data?.nome?.[0] || 'Erro ao criar turma.'),
  })

  const openCreate = () => {
    setEditId(null); setForm(emptyForm); setErrors({})
    setShowNewTurma(false); setNewTurmaNome('')
    setDrawerOpen(true)
  }

  const openEdit = (row) => {
    setEditId(row.id); setForm(emptyForm); setErrors({})
    setShowNewTurma(false); setNewTurmaNome('')
    setDrawerOpen(true)
  }

  const closeDrawer = () => {
    setDrawerOpen(false); setEditId(null); setForm(emptyForm)
    setErrors({}); setShowNewTurma(false); setNewTurmaNome('')
  }

  const set = (field) => (e) => setForm((f) => ({ ...f, [field]: e.target.value }))

  const fields = [
    { key: 'first_name', label: 'Nome *', type: 'text', required: true },
    { key: 'last_name', label: 'Sobrenome', type: 'text', required: false },
    { key: 'username', label: 'Usuário *', type: 'text', required: !editId },
    { key: 'password', label: editId ? 'Nova senha (deixe vazio para manter)' : 'Senha *', type: 'password', required: !editId },
    { key: 'email', label: 'E-mail', type: 'email', required: false },
    { key: 'matricula', label: 'Matrícula *', type: 'text', required: true },
  ]

  const turmaItems = turmas.map((t) => ({ id: t.id, label: t.nome }))

  const columns = [
    { key: 'nome_completo', label: 'Nome' },
    { key: 'matricula', label: 'Matrícula' },
    { key: 'turma', label: 'Turma', render: (row) => row.turma?.nome || '—' },
    { key: 'email', label: 'E-mail' },
    {
      key: 'tem_pendencia',
      label: 'Pendência',
      render: (row) => row.tem_pendencia
        ? <Badge variant="destructive" className="gap-1"><AlertTriangle className="h-3 w-3" />Sim</Badge>
        : <Badge variant="success">Não</Badge>,
    },
  ]

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-foreground">Alunos</h1>
        <Button size="sm" onClick={openCreate}>
          <Plus className="mr-1.5 h-4 w-4" />
          Novo aluno
        </Button>
      </div>

      <DataTable
        columns={columns}
        data={data}
        isLoading={isLoading}
        searchPlaceholder="Buscar por nome ou matrícula..."
        searchValue={q}
        onSearchChange={setQ}
        onSearch={() => setSearch(q)}
        onEdit={openEdit}
        onDelete={(row) => setDeleteTarget(row)}
      />

      <Drawer open={drawerOpen} onClose={closeDrawer} title={editId ? 'Editar aluno' : 'Novo aluno'} width="lg">
        <div className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            {fields.map(({ key, label, type, required }) => (
              <div key={key} className="space-y-1.5">
                <Label>{label}</Label>
                <Input
                  type={type}
                  value={form[key]}
                  onChange={set(key)}
                  required={required}
                  autoComplete={key === 'password' ? 'new-password' : undefined}
                />
                {errors[key] && (
                  <p className="text-xs text-red-500">
                    {Array.isArray(errors[key]) ? errors[key].join(' ') : errors[key]}
                  </p>
                )}
              </div>
            ))}

            <div className="space-y-1.5 sm:col-span-2">
              <div className="flex items-center justify-between">
                <Label>Turma</Label>
                {!showNewTurma && (
                  <button
                    type="button"
                    onClick={() => setShowNewTurma(true)}
                    className="text-xs text-primary hover:underline"
                  >
                    + Nova turma
                  </button>
                )}
              </div>
              {showNewTurma ? (
                <div className="flex gap-2">
                  <Input
                    autoFocus
                    placeholder="Nome da turma"
                    value={newTurmaNome}
                    onChange={(e) => setNewTurmaNome(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') criarTurmaMutation.mutate(newTurmaNome.trim())
                      if (e.key === 'Escape') { setShowNewTurma(false); setNewTurmaNome('') }
                    }}
                  />
                  <Button
                    size="sm"
                    onClick={() => criarTurmaMutation.mutate(newTurmaNome.trim())}
                    disabled={!newTurmaNome.trim() || criarTurmaMutation.isPending}
                  >
                    {criarTurmaMutation.isPending ? '...' : 'Criar'}
                  </Button>
                  <Button size="sm" variant="ghost" onClick={() => { setShowNewTurma(false); setNewTurmaNome('') }}>
                    ✕
                  </Button>
                </div>
              ) : (
                <SearchCombobox
                  items={turmaItems}
                  value={form.turma_id}
                  onChange={(id) => setForm((f) => ({ ...f, turma_id: id }))}
                  placeholder="Selecionar turma..."
                  allowCreate
                  onCreateNew={(text) => { setNewTurmaNome(text); setShowNewTurma(true) }}
                />
              )}
            </div>
          </div>

          {errors.detail && <p className="text-sm text-red-500">{errors.detail}</p>}

          <div className="flex gap-2 pt-2">
            <Button onClick={() => saveMutation.mutate()} disabled={saveMutation.isPending}>
              {saveMutation.isPending ? 'Salvando...' : editId ? 'Salvar' : 'Criar aluno'}
            </Button>
            <Button variant="outline" onClick={closeDrawer}>Cancelar</Button>
          </div>
        </div>
      </Drawer>

      <ConfirmDialog
        open={!!deleteTarget}
        title="Excluir aluno"
        description={`Tem certeza que deseja excluir "${deleteTarget?.nome_completo}"? O usuário associado também será removido.`}
        onConfirm={() => deleteMutation.mutate()}
        onCancel={() => setDeleteTarget(null)}
        isLoading={deleteMutation.isPending}
      />
    </div>
  )
}
