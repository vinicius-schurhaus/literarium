// CapaLivro — usado em páginas de detalhe, listagem popular, etc.
// No catálogo e prateleiras, LivroCard controla diretamente o aspect-ratio.

const CLASSIFICACAO_LABELS = { L: 'L', '10': '+10', '12': '+12', '14': '+14', '16': '+16', '18': '+18' }
const CLASSIFICACAO_COLORS = {
  L: 'bg-green-100 text-green-800',
  '10': 'bg-blue-100 text-blue-800',
  '12': 'bg-yellow-100 text-yellow-800',
  '14': 'bg-orange-100 text-orange-800',
  '16': 'bg-red-100 text-red-800',
  '18': 'bg-red-200 text-red-900',
}

const SIZE = {
  xs: { width: 96, height: 144 },
  sm: { width: 112, height: 168 },
  md: { width: 160, height: 240 },
  lg: { width: 176, height: 264 },
}

export default function CapaLivro({ capa, titulo, classificacao, size = 'md' }) {
  const { width, height } = SIZE[size] ?? SIZE.md
  const cl = classificacao

  return (
    <div className="relative shrink-0" style={{ width, height }}>
      <div className="w-full h-full overflow-hidden bg-slate-100 shadow-sm" style={{ borderRadius: 4 }}>
        {capa ? (
          <img
            src={capa}
            alt={titulo}
            className="h-full w-full object-cover"
            onError={(e) => {
              e.currentTarget.style.display = 'none'
              e.currentTarget.nextSibling?.style.setProperty('display', 'flex')
            }}
          />
        ) : null}
        <div
          className="flex h-full w-full items-center justify-center p-2 bg-slate-100"
          style={capa ? { display: 'none' } : {}}
        >
          <span className="text-xs text-slate-400 text-center leading-tight font-medium">{titulo}</span>
        </div>
      </div>
      {cl && (
        <span className={`absolute right-1 top-1 px-1.5 py-0.5 text-xs font-bold leading-none shadow-sm ${CLASSIFICACAO_COLORS[cl] || 'bg-muted text-muted-foreground'}`}>
          {CLASSIFICACAO_LABELS[cl] || cl}
        </span>
      )}
    </div>
  )
}
