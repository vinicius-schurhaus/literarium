import { useParams } from 'react-router-dom'
import LivroDetalhesContent from '@/components/livros/LivroDetalhesContent'

export default function LivroDetalhesPage() {
  const { livroId } = useParams()
  return (
    <div className="mx-auto max-w-3xl">
      <LivroDetalhesContent livroId={livroId} />
    </div>
  )
}
