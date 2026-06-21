import { useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { CalendarClock, AlertCircle, CheckCircle, BookOpen } from 'lucide-react'
import { getLivro, getLivroStatusAluno, getResenhas, reservarLivro } from '@/api/livros'
import { useAuth } from '@/auth/AuthContext'
import CapaLivro from '@/components/livros/CapaLivro'
import ResenhaLista from '@/components/resenhas/ResenhaLista'
import ResenhaForm from '@/components/resenhas/ResenhaForm'
import StarRating from '@/components/resenhas/StarRating'
import ErrorBoundary from '@/components/ErrorBoundary'
import { Button } from '@/components/ui/button'

export default function LivroDetalhesContent({ livroId }) {
  const { user } = useAuth()
  const qc = useQueryClient()

  const { data: livro, isLoading } = useQuery({
    queryKey: ['livro', livroId],
    queryFn: () => getLivro(livroId),
    enabled: !!livroId,
  })

  const { data: status } = useQuery({
    queryKey: ['livro', livroId, 'status'],
    queryFn: () => getLivroStatusAluno(livroId),
    enabled: !!livroId && !!user?.has_aluno_perfil,
  })

  const { data: resenhas } = useQuery({
    queryKey: ['resenhas', livroId],
    queryFn: () => getResenhas(livroId),
    enabled: !!livroId,
  })

  const reservaMutation = useMutation({
    mutationFn: () => reservarLivro(livroId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['livro', livroId, 'status'] })
      qc.invalidateQueries({ queryKey: ['meus-emprestimos'] })
    },
  })

  useEffect(() => {
    if (!livro) return
    const entry = { id: livro.id, titulo: livro.titulo, autor: { nome: livro.autor?.nome }, capa: livro.capa }
    try {
      const existing = JSON.parse(localStorage.getItem('literarium_vistos') || '[]')
      const updated = [entry, ...existing.filter((l) => l.id !== livro.id)].slice(0, 10)
      localStorage.setItem('literarium_vistos', JSON.stringify(updated))
    } catch {
      // localStorage pode estar indisponível (modo privado/cota): ignora o histórico.
    }
  }, [livro?.id])

  if (isLoading) {
    return (
      <div className="flex justify-center py-20">
        <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
      </div>
    )
  }

  if (!livro) {
    return <p className="text-muted-foreground py-10 text-center">Livro não encontrado.</p>
  }

  const minhaResenha = resenhas?.find((r) => r.is_minha)

  return (
    <div className="space-y-7">
      {/* Capa + info principal */}
      <div className="flex gap-6">
        <div className="shrink-0">
          <CapaLivro
            capa={livro.capa}
            titulo={livro.titulo}
            classificacao={livro.classificacao_indicativa}
            size="lg"
          />
        </div>

        <div className="flex-1 space-y-3 min-w-0">
          <div>
            <h2 className="text-xl font-bold text-foreground leading-snug">{livro.titulo}</h2>
            <p className="text-sm text-muted-foreground mt-0.5">{livro.autor?.nome}</p>
          </div>

          <div className="flex flex-wrap gap-2">
            {livro.genero && (
              <span className="rounded-full border border-border px-2.5 py-0.5 text-xs text-muted-foreground">
                {livro.genero.nome}
              </span>
            )}
            <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${livro.disponivel ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-500'}`}>
              {livro.disponivel ? 'Disponível' : 'Indisponível'}
            </span>
          </div>

          {livro.media_notas ? (
            <div className="flex items-center gap-2">
              <StarRating value={Math.round(livro.media_notas)} readonly size="sm" />
              <span className="text-xs text-muted-foreground">
                {Number(livro.media_notas).toFixed(1)} · {livro.total_resenhas} resenha{livro.total_resenhas !== 1 ? 's' : ''}
              </span>
            </div>
          ) : null}

          {!livro.disponivel && livro.previsao_retorno && (
            <p className="flex items-center gap-1.5 text-xs text-muted-foreground">
              <CalendarClock className="h-3.5 w-3.5 shrink-0" />
              Previsão de retorno: {new Date(livro.previsao_retorno).toLocaleDateString('pt-BR')}
            </p>
          )}

          {/* Ações do aluno */}
          {user?.has_aluno_perfil && (
            <div className="pt-1 space-y-2">
              {status?.ja_tem_emprestimo && (
                <p className="flex items-center gap-1.5 text-sm text-green-700">
                  <CheckCircle className="h-4 w-4 shrink-0" />
                  Você tem este livro emprestado.
                </p>
              )}
              {status?.ja_reservou && (
                <p className="flex items-center gap-1.5 text-sm text-muted-foreground">
                  <CalendarClock className="h-4 w-4 shrink-0" />
                  Você já reservou este livro.
                </p>
              )}
              {status?.pode_reservar && (
                <div className="space-y-1.5">
                  {reservaMutation.isError && (
                    <p className="flex items-center gap-1.5 text-sm text-destructive">
                      <AlertCircle className="h-4 w-4 shrink-0" />
                      {reservaMutation.error?.response?.data?.detail || 'Erro ao reservar.'}
                    </p>
                  )}
                  <Button
                    onClick={() => reservaMutation.mutate()}
                    disabled={reservaMutation.isPending}
                    size="sm"
                  >
                    <BookOpen className="h-4 w-4" />
                    {reservaMutation.isPending ? 'Reservando...' : 'Reservar livro'}
                  </Button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Sinopse */}
      {livro.sinopse && (
        <section className="border-t border-border pt-5">
          <h3 className="text-sm font-semibold text-foreground mb-2">Sinopse</h3>
          <p className="text-sm leading-relaxed text-foreground/75">{livro.sinopse}</p>
        </section>
      )}

      {/* Resenhas */}
      <section className="border-t border-border pt-5">
        <h3 className="text-sm font-semibold text-foreground mb-4">
          Resenhas {resenhas?.length ? `(${resenhas.length})` : ''}
        </h3>
        <ErrorBoundary>
          {user?.has_aluno_perfil && (
            <div className="mb-5">
              <ResenhaForm livroId={livroId} minhaResenha={minhaResenha} />
            </div>
          )}
          <ResenhaLista resenhas={resenhas} />
        </ErrorBoundary>
      </section>
    </div>
  )
}
