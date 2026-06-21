import { useState, useEffect } from 'react'
import { useQueryClient, useMutation } from '@tanstack/react-query'
import { salvarResenha } from '@/api/livros'
import StarRating from './StarRating'

export default function ResenhaForm({ livroId, minhaResenha }) {
  const [nota, setNota] = useState(minhaResenha?.nota ?? 0)
  const [texto, setTexto] = useState(minhaResenha?.texto ?? '')
  const qc = useQueryClient()

  // Preenche o formulário quando a resenha já existente do aluno é carregada
  useEffect(() => {
    if (minhaResenha) {
      setNota(minhaResenha.nota)
      setTexto(minhaResenha.texto ?? '')
    }
  }, [minhaResenha])

  const mutation = useMutation({
    mutationFn: () => salvarResenha(livroId, nota, texto),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['resenhas', livroId] }),
  })

  return (
    <div className="rounded-md border border-border bg-muted/40 p-4 space-y-3">
      <p className="text-sm font-medium text-foreground">
        {minhaResenha ? 'Editar minha resenha' : 'Escrever uma resenha'}
      </p>
      <div className="space-y-1">
        <p className="text-xs text-muted-foreground">Avaliação</p>
        <StarRating value={nota} onChange={setNota} />
      </div>
      <textarea
        className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm text-foreground placeholder-muted-foreground resize-none outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors"
        rows={3}
        placeholder="Escreva um comentário (opcional)..."
        value={texto}
        onChange={(e) => setTexto(e.target.value)}
      />
      {mutation.isError && (
        <p className="text-xs text-destructive">
          {mutation.error?.response?.data?.detail || 'Erro ao salvar resenha.'}
        </p>
      )}
      {mutation.isSuccess && (
        <p className="text-xs text-green-600">Resenha salva.</p>
      )}
      <button
        type="button"
        onClick={() => mutation.mutate()}
        disabled={nota === 0 || mutation.isPending}
        className="rounded-md bg-primary px-4 py-1.5 text-xs font-medium text-white transition-colors hover:bg-accent-foreground disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {mutation.isPending ? 'Salvando...' : 'Salvar'}
      </button>
    </div>
  )
}
