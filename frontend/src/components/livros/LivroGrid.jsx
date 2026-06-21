import LivroCard from './LivroCard'

export default function LivroGrid({ livros }) {
  if (!livros?.length) {
    return (
      <div className="py-20 text-center text-muted-foreground">
        Nenhum livro encontrado.
      </div>
    )
  }

  return (
    <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
      {livros.map((livro) => (
        <LivroCard key={livro.id} livro={livro} />
      ))}
    </div>
  )
}
