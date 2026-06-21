import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, CornerDownLeft } from 'lucide-react'
import { staffEmprestimos, staffAlunos, staffLivros } from '@/api/staff'
import DataTable from '@/components/staff/DataTable'
import ConfirmDialog from '@/components/staff/ConfirmDialog'
import Drawer from '@/components/ui/Drawer'
import StatusBadge from '@/components/emprestimos/StatusBadge'
import SearchCombobox from '@/components/ui/SearchCombobox'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'

function fmt(date) {
  if (!date) return '—'
  return new Date(date).toLocaleDateString('pt-BR')
}

export default function EmprestimosPage() {
  const qc = useQueryClient()
  const [q, setQ] = useState('')
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [drawerOpen, setDrawerOpen] = useState(false)
  const [newEmp, setNewEmp] = useState({ aluno_id: '', livro_id: '' })
  const [formError, setFormError] = useState('')
  const [devolverTarget, setDevolverTarget] = useState(null)

  const { data = [], isLoading } = useQuery({
    queryKey: ['staff-emprestimos', search, statusFilter],
    queryFn: () => staffEmprestimos.list({ q: search, status: statusFilter }),
  })

  // Carregar alunos e livros disponíveis apenas quando o form está aberto
  const { data: alunosData = [] } = useQuery({
    queryKey: ['staff-alunos-todos'],
    queryFn: () => staffAlunos.list({ page_size: 1000 }),
    enabled: drawerOpen,
    staleTime: 60_000,
  })
  const alunos = Array.isArray(alunosData) ? alunosData : (alunosData?.results ?? [])

  const { data: livrosData } = useQuery({
    queryKey: ['staff-livros-disponiveis'],
    queryFn: () => staffLivros.list({ page_size: 1000 }),
    enabled: drawerOpen,
    staleTime: 60_000,
  })
  const livros = (Array.isArray(livrosData) ? livrosData : (livrosData?.results ?? [])).filter(l => l.disponivel)

  const criarMutation = useMutation({
    mutationFn: () => staffEmprestimos.create(newEmp.livro_id, newEmp.aluno_id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['staff-emprestimos'] })
      qc.invalidateQueries({ queryKey: ['staff-livros-disponiveis'] })
      setDrawerOpen(false)
      setNewEmp({ aluno_id: '', livro_id: '' })
      setFormError('')
    },
    onError: (err) => setFormError(err.response?.data?.detail || 'Erro ao registrar empréstimo.'),
  })

  const devolverMutation = useMutation({
    mutationFn: () => staffEmprestimos.devolver(devolverTarget.id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['staff-emprestimos'] })
      qc.invalidateQueries({ queryKey: ['staff-livros-disponiveis'] })
      setDevolverTarget(null)
    },
    onError: (err) => alert(err.response?.data?.detail || 'Erro ao devolver.'),
  })

  const alunoItems = alunos.map((a) => ({
    id: a.id,
    label: a.nome_completo,
    sublabel: a.matricula + (a.turma ? ` · ${a.turma.nome}` : ''),
  }))

  const livroItems = livros.map((l) => ({
    id: l.id,
    label: l.titulo,
    sublabel: l.autor?.nome,
  }))

  const columns = [
    { key: 'livro', label: 'Livro', render: (row) => row.livro?.titulo },
    { key: 'aluno_nome', label: 'Aluno' },
    { key: 'aluno_matricula', label: 'Matrícula' },
    { key: 'data_emprestimo', label: 'Retirada', render: (row) => fmt(row.data_emprestimo) },
    { key: 'data_devolucao_prevista', label: 'Prev. Devolução', render: (row) => fmt(row.data_devolucao_prevista) },
    { key: 'data_devolucao_real', label: 'Devolvido em', render: (row) => fmt(row.data_devolucao_real) },
    { key: 'status', label: 'Status', render: (row) => <StatusBadge status={row.status} estaAtrasado={row.esta_atrasado} /> },
  ]

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-foreground">Empréstimos</h1>
        <Button size="sm" onClick={() => { setDrawerOpen(true); setFormError('') }}>
          <Plus className="mr-1.5 h-4 w-4" />
          Registrar empréstimo
        </Button>
      </div>

      <Drawer
        open={drawerOpen}
        onClose={() => { setDrawerOpen(false); setFormError(''); setNewEmp({ aluno_id: '', livro_id: '' }) }}
        title="Registrar empréstimo"
        width="lg"
      >
        <div className="space-y-4">
          <div className="space-y-1.5">
            <Label>Aluno *</Label>
            <SearchCombobox
              items={alunoItems}
              value={newEmp.aluno_id}
              onChange={(id) => setNewEmp({ ...newEmp, aluno_id: id })}
              placeholder="Buscar por nome ou matrícula..."
            />
          </div>
          <div className="space-y-1.5">
            <Label>Livro disponível *</Label>
            <SearchCombobox
              items={livroItems}
              value={newEmp.livro_id}
              onChange={(id) => setNewEmp({ ...newEmp, livro_id: id })}
              placeholder="Buscar por título ou autor..."
            />
          </div>
          {formError && (
            <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-destructive">{formError}</p>
          )}
          <div className="flex gap-2 pt-2">
            <Button
              onClick={() => criarMutation.mutate()}
              disabled={!newEmp.aluno_id || !newEmp.livro_id || criarMutation.isPending}
            >
              {criarMutation.isPending ? 'Registrando...' : 'Registrar'}
            </Button>
            <Button
              variant="outline"
              onClick={() => { setDrawerOpen(false); setFormError(''); setNewEmp({ aluno_id: '', livro_id: '' }) }}
            >
              Cancelar
            </Button>
          </div>
        </div>
      </Drawer>

      <DataTable
        columns={columns}
        data={data}
        isLoading={isLoading}
        searchPlaceholder="Buscar por livro ou aluno..."
        searchValue={q}
        onSearchChange={setQ}
        onSearch={() => setSearch(q)}
        extraFilters={
          <select
            className="h-9 rounded-xl border border-border bg-white px-3 text-sm outline-none focus:ring-2 focus:ring-primary/20"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="">Todos os status</option>
            <option value="ABERTO">Em aberto</option>
            <option value="DEVOLVIDO">Devolvidos</option>
          </select>
        }
        actions={(row) => row.status === 'ABERTO' && (
          <Button
            size="sm"
            className="gap-1.5 bg-green-600 hover:bg-green-700 text-white"
            onClick={() => setDevolverTarget(row)}
          >
            <CornerDownLeft className="h-3.5 w-3.5" />
            Devolver
          </Button>
        )}
      />

      <ConfirmDialog
        open={!!devolverTarget}
        title="Registrar devolução"
        description={`Confirmar devolução de "${devolverTarget?.livro?.titulo}" por ${devolverTarget?.aluno_nome}?`}
        onConfirm={() => devolverMutation.mutate()}
        onCancel={() => setDevolverTarget(null)}
        isLoading={devolverMutation.isPending}
      />
    </div>
  )
}
