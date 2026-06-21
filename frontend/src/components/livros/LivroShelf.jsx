import { Link } from 'react-router-dom'
import { ChevronRight } from 'lucide-react'
import LivroCard from './LivroCard'

export default function LivroShelf({ title, livros = [], verTudoLink, isLoading }) {
  return (
    <section>
      <div className="flex items-center justify-between mb-3">
        <h2 className="font-bold text-foreground" style={{ fontSize: 24 }}>{title}</h2>
        {verTudoLink && (
          <Link
            to={verTudoLink}
            className="flex items-center gap-1 text-sm text-primary hover:text-accent-foreground font-semibold transition-colors"
          >
            Ver tudo <ChevronRight size={14} />
          </Link>
        )}
      </div>

      <div
        className="flex gap-3 overflow-x-auto scrollbar-hide snap-x"
        style={{ paddingTop: 8, paddingLeft: 8, paddingRight: 8, paddingBottom: 16, margin: -8, marginBottom: 0 }}
      >
        {isLoading
          ? Array.from({ length: 7 }).map((_, i) => (
              <div key={i} className="shrink-0 snap-start flex flex-col items-center" style={{ width: 176 }}>
                <div className="bg-slate-100 animate-pulse" style={{ width: 176, height: 264, borderRadius: 4 }} />
                <div className="mt-2 w-full space-y-1.5 text-center">
                  <div className="h-3.5 w-5/6 rounded bg-slate-100 animate-pulse mx-auto" />
                  <div className="h-3 w-2/3 rounded bg-slate-100 animate-pulse mx-auto" />
                </div>
              </div>
            ))
          : livros.map((livro) => (
              <div key={livro.id} className="shrink-0 snap-start flex justify-center" style={{ width: 176 }}>
                <LivroCard livro={livro} />
              </div>
            ))}
      </div>
    </section>
  )
}
