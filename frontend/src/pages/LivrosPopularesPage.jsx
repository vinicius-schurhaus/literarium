import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { TrendingUp } from 'lucide-react'
import { getLivrosPopulares } from '@/api/livros'
import CapaLivro from '@/components/livros/CapaLivro'

export default function LivrosPopularesPage() {
  const { data: livros, isLoading } = useQuery({
    queryKey: ['livros-populares'],
    queryFn: getLivrosPopulares,
  })

  if (isLoading) {
    return (
      <div className="space-y-3">
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="flex items-center gap-4 rounded-xl border border-border bg-white p-3 animate-pulse">
            <div className="h-3.5 w-8 rounded bg-muted shrink-0" />
            <div className="h-44 w-28 rounded-xl bg-muted shrink-0" />
            <div className="flex-1 space-y-2">
              <div className="h-4 w-2/3 rounded bg-muted" />
              <div className="h-3 w-1/3 rounded bg-muted" />
            </div>
          </div>
        ))}
      </div>
    )
  }

  return (
    <div>
      <div className="mb-6 flex items-center gap-2.5">
        <TrendingUp className="h-6 w-6 text-primary" />
        <h1 className="text-2xl font-bold text-foreground">Em alta</h1>
        <span className="text-sm text-muted-foreground">— últimos 3 meses</span>
      </div>

      {!livros?.length ? (
        <p className="text-muted-foreground">Nenhum dado disponível.</p>
      ) : (
        <div className="space-y-2">
          {livros.map((livro, i) => (
            <Link
              key={livro.id}
              to={`/livros/${livro.id}`}
              className="flex items-center gap-4 rounded-xl border border-border bg-white p-3 hover:shadow-sm hover:border-primary/30 transition-all"
            >
              <span className="w-8 text-center text-lg font-bold text-primary/50 shrink-0">
                #{i + 1}
              </span>
              <CapaLivro capa={livro.capa} titulo={livro.titulo} size="sm" />
              <div className="flex-1 min-w-0 space-y-0.5">
                <p className="font-semibold text-foreground line-clamp-2">{livro.titulo}</p>
                <p className="text-sm text-muted-foreground">{livro.autor?.nome}</p>
              </div>
              <div className="flex flex-col items-end gap-1.5 shrink-0">
                <span className="rounded-full bg-primary/10 px-2.5 py-1 text-xs font-semibold text-primary">
                  {livro.total_emprestimos} empréstimo{livro.total_emprestimos !== 1 ? 's' : ''}
                </span>
                <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${livro.disponivel ? 'bg-green-50 text-green-700' : 'bg-slate-100 text-slate-500'}`}>
                  {livro.disponivel ? 'Disponível' : 'Indisponível'}
                </span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
