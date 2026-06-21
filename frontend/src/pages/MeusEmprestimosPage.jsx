import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { RefreshCw, XCircle, CalendarClock } from 'lucide-react'
import { getMeusEmprestimos, renovarEmprestimo, cancelarReserva } from '@/api/emprestimos'

function fmt(date) {
  if (!date) return '—'
  return new Date(date).toLocaleDateString('pt-BR')
}

function StatusBadgeSimple({ status, atrasado }) {
  if (atrasado) return <span className="rounded px-2 py-0.5 text-xs font-semibold bg-red-100 text-red-700">Atrasado</span>
  if (status === 'ABERTO') return <span className="rounded px-2 py-0.5 text-xs font-semibold bg-amber-100 text-amber-700">Em aberto</span>
  return <span className="rounded px-2 py-0.5 text-xs font-semibold bg-slate-100 text-slate-500">Devolvido</span>
}

function Capa({ livro }) {
  return (
    <div className="transition-transform duration-300 group-hover:scale-[1.03]" style={{ width: 220, height: 282 }}>
      <div className="relative w-full h-full" style={{ borderRadius: 4, boxShadow: '0 4px 12px rgba(0,0,0,0.08)', overflow: 'hidden' }}>
        {livro.capa ? (
          <img src={livro.capa} alt={livro.titulo} className="absolute inset-0 h-full w-full object-cover" />
        ) : (
          <div className="absolute inset-0 flex items-center justify-center bg-slate-100 p-3">
            <span className="text-xs text-slate-400 text-center leading-tight">{livro.titulo}</span>
          </div>
        )}
      </div>
    </div>
  )
}

function LivroEmprestimoCard({ emprestimo, onRenovar, renovando }) {
  const { livro } = emprestimo
  return (
    <div style={{ width: 220 }}>
      <Link to={`/livros/${livro.id}`} className="block group">
        <Capa livro={livro} />
      </Link>
      <div className="mt-2 space-y-1">
        <p className="font-semibold line-clamp-2 leading-snug" style={{ fontSize: 16, color: '#1C1C1C' }}>
          {livro.titulo}
        </p>
        <p className="truncate" style={{ fontSize: 14, color: '#646464' }}>{livro.autor?.nome}</p>
        <div className="flex items-center gap-1 text-xs" style={{ color: '#646464' }}>
          <CalendarClock size={12} />
          <span>Dev. {fmt(emprestimo.data_devolucao_prevista)}</span>
        </div>
        <div className="flex items-center gap-2 pt-0.5">
          <StatusBadgeSimple status={emprestimo.status} atrasado={emprestimo.esta_atrasado} />
          {emprestimo.status === 'ABERTO' && (
            <button
              onClick={onRenovar}
              disabled={renovando}
              className="flex items-center gap-1 text-xs text-primary hover:underline disabled:opacity-50"
            >
              <RefreshCw size={11} />
              Renovar
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

function LivroReservaCard({ reserva, onCancelar, cancelando }) {
  const { livro } = reserva
  return (
    <div style={{ width: 220 }}>
      <Link to={`/livros/${livro.id}`} className="block group">
        <Capa livro={livro} />
      </Link>
      <div className="mt-2 space-y-1">
        <p className="font-semibold line-clamp-2 leading-snug" style={{ fontSize: 16, color: '#1C1C1C' }}>
          {livro.titulo}
        </p>
        <p className="truncate" style={{ fontSize: 14, color: '#646464' }}>{livro.autor?.nome}</p>
        {reserva.data_disponivel_prevista && (
          <div className="flex items-center gap-1 text-xs" style={{ color: '#646464' }}>
            <CalendarClock size={12} />
            <span>Disp. {fmt(reserva.data_disponivel_prevista)}</span>
          </div>
        )}
        <div className="flex items-center gap-2 pt-0.5">
          <span className="rounded px-2 py-0.5 text-xs font-semibold bg-amber-100 text-amber-700">Reservado</span>
          {reserva.status === 'ATIVA' && (
            <button
              onClick={onCancelar}
              disabled={cancelando}
              className="flex items-center gap-1 text-xs text-destructive hover:underline disabled:opacity-50"
            >
              <XCircle size={11} />
              Cancelar
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

export default function MeusEmprestimosPage() {
  const qc = useQueryClient()
  const { data, isLoading } = useQuery({
    queryKey: ['meus-emprestimos'],
    queryFn: getMeusEmprestimos,
  })

  const renovarMutation = useMutation({
    mutationFn: renovarEmprestimo,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['meus-emprestimos'] }),
    onError: (err) => alert(err.response?.data?.detail || 'Erro ao renovar.'),
  })

  const cancelarMutation = useMutation({
    mutationFn: cancelarReserva,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['meus-emprestimos'] }),
    onError: (err) => alert(err.response?.data?.detail || 'Erro ao cancelar reserva.'),
  })

  if (isLoading) {
    return (
      <div className="space-y-10">
        {[0, 1].map((s) => (
          <section key={s}>
            <div className="h-8 w-48 rounded bg-slate-100 animate-pulse mb-4" />
            <div className="flex gap-6">
              {[0, 1, 2].map((i) => (
                <div key={i}>
                  <div className="bg-slate-100 animate-pulse" style={{ width: 220, height: 282, borderRadius: 4 }} />
                  <div className="mt-2 h-4 w-3/4 rounded bg-slate-100 animate-pulse" />
                </div>
              ))}
            </div>
          </section>
        ))}
      </div>
    )
  }

  const { emprestimos = [], reservas = [] } = data || {}

  return (
    <div className="space-y-10">
      <section>
        <h2 className="font-bold text-foreground mb-5" style={{ fontSize: 32 }}>Meus Empréstimos</h2>
        {emprestimos.length === 0 ? (
          <p style={{ color: '#646464' }}>Nenhum empréstimo registrado.</p>
        ) : (
          <div className="flex flex-wrap gap-6">
            {emprestimos.map((e) => (
              <LivroEmprestimoCard
                key={e.id}
                emprestimo={e}
                onRenovar={() => renovarMutation.mutate(e.id)}
                renovando={renovarMutation.isPending && renovarMutation.variables === e.id}
              />
            ))}
          </div>
        )}
      </section>

      <section>
        <h2 className="font-bold text-foreground mb-5" style={{ fontSize: 32 }}>Minhas Reservas</h2>
        {reservas.length === 0 ? (
          <p style={{ color: '#646464' }}>Nenhuma reserva ativa.</p>
        ) : (
          <div className="flex flex-wrap gap-6">
            {reservas.map((r) => (
              <LivroReservaCard
                key={r.id}
                reserva={r}
                onCancelar={() => cancelarMutation.mutate(r.id)}
                cancelando={cancelarMutation.isPending && cancelarMutation.variables === r.id}
              />
            ))}
          </div>
        )}
      </section>
    </div>
  )
}
