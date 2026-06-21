import { Link } from 'react-router-dom'
import { useLivroDrawer } from '@/contexts/LivroDrawerContext'

export default function LivroCard({ livro }) {
  const { openLivro } = useLivroDrawer()

  return (
    <Link
      to={`/livros/${livro.id}`}
      onClick={(e) => { e.preventDefault(); openLivro(livro.id) }}
      className="block group shrink-0"
      style={{ width: 176 }}
    >
      <div
        className="transition-transform duration-300 group-hover:scale-[1.03]"
        style={{ width: 176, height: 264 }}
      >
        <div
          className="relative w-full h-full"
          style={{ borderRadius: 4, boxShadow: '0 4px 12px rgba(0,0,0,0.08)', overflow: 'hidden' }}
        >
          {livro.capa ? (
            <img
              src={livro.capa}
              alt={livro.titulo}
              className="absolute inset-0 h-full w-full object-cover"
              onError={(e) => {
                e.currentTarget.style.display = 'none'
                e.currentTarget.nextSibling?.style.setProperty('display', 'flex')
              }}
            />
          ) : null}
          <div
            className="absolute inset-0 flex items-center justify-center bg-slate-100 p-3"
            style={livro.capa ? { display: 'none' } : {}}
          >
            <span className="text-xs text-slate-400 text-center leading-tight">{livro.titulo}</span>
          </div>
        </div>
      </div>

      <div className="mt-2 space-y-0.5 text-center">
        <p className="font-semibold line-clamp-2 leading-snug" style={{ fontSize: 16, color: '#1C1C1C' }}>
          {livro.titulo}
        </p>
        <p className="truncate" style={{ fontSize: 14, color: '#646464' }}>{livro.autor?.nome}</p>
      </div>
    </Link>
  )
}
