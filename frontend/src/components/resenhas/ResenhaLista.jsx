import StarRating from './StarRating'

export default function ResenhaLista({ resenhas }) {
  if (!resenhas?.length) {
    return (
      <p className="text-sm text-muted-foreground py-4">
        Nenhuma resenha ainda. Seja o primeiro!
      </p>
    )
  }

  return (
    <div className="divide-y divide-border">
      {resenhas.map((r) => (
        <div key={r.id} className="py-4 space-y-1.5">
          <div className="flex items-center gap-3">
            <span className="text-sm font-medium text-foreground">{r.aluno_nome}</span>
            <StarRating value={r.nota} readonly size="sm" />
            {r.is_minha && (
              <span className="text-xs text-primary font-medium">sua resenha</span>
            )}
          </div>
          {r.texto && (
            <p className="text-sm text-foreground/80 leading-relaxed">{r.texto}</p>
          )}
          <p className="text-xs text-muted-foreground">
            {new Date(r.data_criacao).toLocaleDateString('pt-BR')}
          </p>
        </div>
      ))}
    </div>
  )
}
