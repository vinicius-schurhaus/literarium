import { useQuery, useQueries } from '@tanstack/react-query'
import { getLivros, getHome, getGeneros } from '@/api/livros'
import LivroShelf from '@/components/livros/LivroShelf'

export default function CatalogoPage() {
  const { data: home, isLoading: homeLoading } = useQuery({
    queryKey: ['home'],
    queryFn: getHome,
    staleTime: 60_000,
  })

  const { data: generos = [] } = useQuery({
    queryKey: ['generos'],
    queryFn: getGeneros,
    staleTime: Infinity,
  })

  // Uma prateleira por gênero (máx. 10 gêneros para não sobrecarregar)
  const generoQueries = useQueries({
    queries: generos.slice(0, 10).map((g) => ({
      queryKey: ['livros', 'genero', g.id],
      queryFn: () => getLivros({ genero: g.id }),
      staleTime: 60_000,
    })),
  })

  return (
    <div className="space-y-10">
      <h1 className="text-2xl font-bold text-foreground">Catálogo</h1>

      {/* Em alta */}
      <LivroShelf
        title="Em alta"
        livros={home?.livros_populares}
        verTudoLink="/livros/populares"
        isLoading={homeLoading}
      />

      {/* Adicionados recentemente */}
      <LivroShelf
        title="Adicionados recentemente"
        livros={home?.livros_recentes}
        isLoading={homeLoading}
      />

      {/* Prateleiras por gênero */}
      {generos.slice(0, 10).map((g, i) => {
        const q = generoQueries[i]
        const livros = q?.data?.results ?? q?.data ?? []
        if (!q?.isLoading && livros.length === 0) return null
        return (
          <LivroShelf
            key={g.id}
            title={g.nome}
            livros={livros}
            isLoading={q?.isLoading}
          />
        )
      })}
    </div>
  )
}
