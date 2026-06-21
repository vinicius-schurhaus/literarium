import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Search } from 'lucide-react'
import { getLivros } from '@/api/livros'
import LivroGrid from '@/components/livros/LivroGrid'

function useDebounce(value, ms = 350) {
  const [debounced, setDebounced] = useState(value)
  useEffect(() => {
    const t = setTimeout(() => setDebounced(value), ms)
    return () => clearTimeout(t)
  }, [value, ms])
  return debounced
}

export default function PesquisarPage() {
  const [input, setInput] = useState('')
  const q = useDebounce(input)

  const { data, isLoading, isFetching } = useQuery({
    queryKey: ['pesquisar', q],
    queryFn: () => getLivros({ q }),
    enabled: q.length >= 2,
  })

  return (
    <div className="-m-6 md:-m-8 flex flex-col min-h-full">
      {/* Barra de busca — mesma cor da topbar (laranja) */}
      <div style={{ background: 'linear-gradient(90deg, #F79633 0%, #D83135 100%)', padding: '8px 60px 60px' }}>
        <div className="relative max-w-2xl mx-auto">
          <Search
            size={18}
            className="absolute left-4 top-1/2 -translate-y-1/2 pointer-events-none"
            style={{ color: '#9CA3AF' }}
          />
          <input
            autoFocus
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Procure por título ou autor..."
            className="w-full rounded-full bg-white pl-11 pr-5 py-3 text-sm text-foreground placeholder-slate-400 outline-none shadow-sm"
          />
          {(isLoading || isFetching) && q.length >= 2 && (
            <div className="absolute right-4 top-1/2 -translate-y-1/2">
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-primary border-t-transparent" />
            </div>
          )}
        </div>
      </div>

      {/* Conteúdo */}
      <div className="flex-1 px-10 py-8">
        {q.length < 2 ? (
          /* Estado vazio */
          <div className="flex flex-col items-center justify-center py-24 text-center">
            <div className="mb-6 flex h-24 w-24 items-center justify-center rounded-full bg-slate-100">
              <Search size={40} className="text-slate-300" />
            </div>
            <p className="text-lg font-semibold text-foreground">
              Encontre qualquer livro do acervo
            </p>
            <p className="text-sm text-muted-foreground mt-2 max-w-sm">
              Busque por título ou nome do autor para localizar um livro disponível na biblioteca.
            </p>
          </div>
        ) : (
          /* Resultados */
          <div className="space-y-4">
            {!isLoading && data && (
              <p className="text-sm" style={{ color: '#646464' }}>
                {data.count} resultado{data.count !== 1 ? 's' : ''} para{' '}
                <span style={{ color: '#1C1C1C', fontWeight: 600 }}>&ldquo;{q}&rdquo;</span>
              </p>
            )}
            <LivroGrid livros={data?.results} />
          </div>
        )}
      </div>
    </div>
  )
}
