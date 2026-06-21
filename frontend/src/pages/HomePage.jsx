import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { BookOpen } from 'lucide-react'
import { useMemo } from 'react'
import { useAuth } from '@/auth/AuthContext'
import { getHome } from '@/api/livros'
import LivroShelf from '@/components/livros/LivroShelf'

export default function HomePage() {
  const { user } = useAuth()

  const { data, isLoading } = useQuery({
    queryKey: ['home'],
    queryFn: getHome,
  })

  const vistos = useMemo(() => {
    try {
      return JSON.parse(localStorage.getItem('literarium_vistos') || '[]')
    } catch {
      return []
    }
  }, [])

  const firstName = user?.first_name || user?.username || 'leitor'
  const hour = new Date().getHours()
  const greeting = hour < 12 ? 'Bom dia' : hour < 18 ? 'Boa tarde' : 'Boa noite'

  return (
    <div className="space-y-10">
      {/* Hero */}
      <div className="rounded-2xl bg-linear-to-br from-primary to-accent-foreground px-8 py-10 text-white shadow-md">
        <div className="flex items-start justify-between gap-4">
          <div className="space-y-2">
            <p className="text-base font-medium opacity-90">{greeting},</p>
            <h1 className="text-4xl font-bold capitalize">{firstName}!</h1>
            <p className="text-base opacity-80 mt-1">O que você vai ler hoje?</p>
          </div>
        </div>

        <div className="mt-8">
          <Link
            to="/catalogo"
            className="inline-flex items-center gap-2 rounded-xl bg-white/20 px-5 py-3 text-sm font-semibold text-white hover:bg-white/30 transition-colors backdrop-blur-sm"
          >
            <BookOpen size={16} />
            Explorar catálogo
          </Link>
        </div>
      </div>

      {/* Vistos recentemente */}
      {vistos.length > 0 && (
        <LivroShelf title="Vistos recentemente" livros={vistos} />
      )}

      {/* Vestibular */}
      {(isLoading || (data?.livros_vestibular?.length ?? 0) > 0) && (
        <LivroShelf
          title="Vestibular"
          livros={data?.livros_vestibular}
          isLoading={isLoading}
        />
      )}
    </div>
  )
}
