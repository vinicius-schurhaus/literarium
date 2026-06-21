import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { X } from 'lucide-react'
import { staffReservas } from '@/api/staff'
import DataTable from '@/components/staff/DataTable'
import ConfirmDialog from '@/components/staff/ConfirmDialog'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'

function fmt(date) {
  if (!date) return '—'
  return new Date(date).toLocaleDateString('pt-BR')
}

export default function ReservasPage() {
  const qc = useQueryClient()
  const [q, setQ] = useState('')
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('ATIVA')
  const [cancelTarget, setCancelTarget] = useState(null)

  const { data = [], isLoading } = useQuery({
    queryKey: ['staff-reservas', search, statusFilter],
    queryFn: () => staffReservas.list({ q: search, status: statusFilter }),
  })

  const cancelarMutation = useMutation({
    mutationFn: () => staffReservas.cancelar(cancelTarget.id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['staff-reservas'] })
      setCancelTarget(null)
    },
    onError: (err) => alert(err.response?.data?.detail || 'Erro ao cancelar.'),
  })

  const STATUS_VARIANT = { ATIVA: 'warning', ATENDIDA: 'success', CANCELADA: 'secondary' }

  const columns = [
    { key: 'livro', label: 'Livro', render: (row) => row.livro?.titulo },
    { key: 'aluno_nome', label: 'Aluno' },
    { key: 'data_reserva', label: 'Reservado em', render: (row) => fmt(row.data_reserva) },
    { key: 'data_disponivel_prevista', label: 'Prev. Disponível', render: (row) => fmt(row.data_disponivel_prevista) },
    {
      key: 'status',
      label: 'Status',
      render: (row) => <Badge variant={STATUS_VARIANT[row.status] || 'outline'}>{row.status}</Badge>,
    },
  ]

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-foreground">Reservas</h1>
      </div>

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
            <option value="">Todas</option>
            <option value="ATIVA">Ativas</option>
            <option value="ATENDIDA">Atendidas</option>
            <option value="CANCELADA">Canceladas</option>
          </select>
        }
        actions={(row) => row.status === 'ATIVA' && (
          <Button
            variant="ghost"
            size="sm"
            className="gap-1 text-red-500 hover:text-red-700 hover:bg-red-50"
            onClick={() => setCancelTarget(row)}
          >
            <X className="h-3.5 w-3.5" />
            Cancelar
          </Button>
        )}
      />

      <ConfirmDialog
        open={!!cancelTarget}
        title="Cancelar reserva"
        description={`Cancelar reserva de "${cancelTarget?.livro?.titulo}" para ${cancelTarget?.aluno_nome}?`}
        onConfirm={() => cancelarMutation.mutate()}
        onCancel={() => setCancelTarget(null)}
        isLoading={cancelarMutation.isPending}
      />
    </div>
  )
}
