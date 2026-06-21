import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { staffLivros, staffAutores, staffGeneros } from '@/api/staff'
import SearchCombobox from '@/components/ui/SearchCombobox'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'

export default function LivroForm({ id, onSuccess, onCancel }) {
  const qc = useQueryClient()
  const isEdit = !!id

  const [form, setForm] = useState({
    titulo: '', autor: '', genero: '', quantidade: 1,
    sinopse: '', conteudo_explicito: false, capa: null,
  })
  const [errors, setErrors] = useState({})

  // Cadastro rápido de autor sem sair do formulário do livro
  const [showNewAutor, setShowNewAutor] = useState(false)
  const [newAutorNome, setNewAutorNome] = useState('')

  // Cadastro rápido de gênero sem sair do formulário do livro
  const [showNewGenero, setShowNewGenero] = useState(false)
  const [newGeneroNome, setNewGeneroNome] = useState('')

  const { data: autores = [] } = useQuery({ queryKey: ['staff-autores'], queryFn: staffAutores.list })
  const { data: generos = [] } = useQuery({ queryKey: ['staff-generos'], queryFn: staffGeneros.list })

  const { data: livro } = useQuery({
    queryKey: ['staff-livro', id],
    queryFn: () => staffLivros.get(id),
    enabled: isEdit,
  })

  useEffect(() => {
    if (livro) {
      setForm({
        titulo: livro.titulo,
        autor: String(livro.autor?.id || ''),
        genero: String(livro.genero?.id || ''),
        quantidade: livro.quantidade,
        sinopse: livro.sinopse || '',
        conteudo_explicito: livro.conteudo_explicito ?? false,
        capa: null,
      })
    }
  }, [livro])

  const criarAutorMutation = useMutation({
    mutationFn: (nome) => staffAutores.create({ nome }),
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: ['staff-autores'] })
      setForm((f) => ({ ...f, autor: String(data.id) }))
      setShowNewAutor(false)
      setNewAutorNome('')
    },
    onError: (err) => alert(err.response?.data?.nome?.[0] || 'Erro ao criar autor.'),
  })

  const criarGeneroMutation = useMutation({
    mutationFn: (nome) => staffGeneros.create({ nome }),
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: ['staff-generos'] })
      setForm((f) => ({ ...f, genero: String(data.id) }))
      setShowNewGenero(false)
      setNewGeneroNome('')
    },
    onError: (err) => alert(err.response?.data?.nome?.[0] || 'Erro ao criar gênero.'),
  })

  const salvarMutation = useMutation({
    mutationFn: () => {
      const fd = new FormData()
      fd.append('titulo', form.titulo)
      fd.append('autor', form.autor)
      if (form.genero) fd.append('genero', form.genero)
      fd.append('quantidade', form.quantidade)
      fd.append('sinopse', form.sinopse)
      fd.append('conteudo_explicito', form.conteudo_explicito)
      if (form.capa) fd.append('capa', form.capa)
      return isEdit ? staffLivros.update(id, fd) : staffLivros.create(fd)
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['staff-livros'] })
      onSuccess?.()
    },
    onError: (err) => setErrors(err.response?.data || {}),
  })

  const f = form

  const autorItems = autores.map((a) => ({ id: a.id, label: a.nome }))
  const generoItems = generos.map((g) => ({ id: g.id, label: g.nome }))

  return (
    <div className="space-y-5">
      {/* Título */}
      <div className="space-y-1.5">
        <Label>Título *</Label>
        <Input
          value={f.titulo}
          onChange={(e) => setForm({ ...f, titulo: e.target.value })}
          placeholder="Título do livro"
        />
        {errors.titulo && <p className="text-xs text-destructive">{errors.titulo}</p>}
      </div>

      {/* Autor */}
      <div className="space-y-1.5">
        <div className="flex items-center justify-between">
          <Label>Autor *</Label>
          {!showNewAutor && (
            <button
              type="button"
              onClick={() => setShowNewAutor(true)}
              className="text-xs text-primary hover:underline"
            >
              + Novo autor
            </button>
          )}
        </div>
        {showNewAutor ? (
          <div className="flex gap-2">
            <Input
              autoFocus
              placeholder="Nome do autor"
              value={newAutorNome}
              onChange={(e) => setNewAutorNome(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') criarAutorMutation.mutate(newAutorNome.trim())
                if (e.key === 'Escape') { setShowNewAutor(false); setNewAutorNome('') }
              }}
            />
            <Button
              size="sm"
              onClick={() => criarAutorMutation.mutate(newAutorNome.trim())}
              disabled={!newAutorNome.trim() || criarAutorMutation.isPending}
            >
              {criarAutorMutation.isPending ? '...' : 'Criar'}
            </Button>
            <Button
              size="sm"
              variant="ghost"
              onClick={() => { setShowNewAutor(false); setNewAutorNome('') }}
            >
              ✕
            </Button>
          </div>
        ) : (
          <SearchCombobox
            items={autorItems}
            value={f.autor}
            onChange={(id) => setForm({ ...f, autor: id })}
            placeholder="Buscar autor..."
            allowCreate
            onCreateNew={(text) => { setNewAutorNome(text); setShowNewAutor(true) }}
          />
        )}
        {errors.autor && <p className="text-xs text-destructive">{errors.autor}</p>}
      </div>

      {/* Gênero */}
      <div className="space-y-1.5">
        <div className="flex items-center justify-between">
          <Label>Gênero</Label>
          {!showNewGenero && (
            <button
              type="button"
              onClick={() => setShowNewGenero(true)}
              className="text-xs text-primary hover:underline"
            >
              + Novo gênero
            </button>
          )}
        </div>
        {showNewGenero ? (
          <div className="flex gap-2">
            <Input
              autoFocus
              placeholder="Nome do gênero"
              value={newGeneroNome}
              onChange={(e) => setNewGeneroNome(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') criarGeneroMutation.mutate(newGeneroNome.trim())
                if (e.key === 'Escape') { setShowNewGenero(false); setNewGeneroNome('') }
              }}
            />
            <Button
              size="sm"
              onClick={() => criarGeneroMutation.mutate(newGeneroNome.trim())}
              disabled={!newGeneroNome.trim() || criarGeneroMutation.isPending}
            >
              {criarGeneroMutation.isPending ? '...' : 'Criar'}
            </Button>
            <Button
              size="sm"
              variant="ghost"
              onClick={() => { setShowNewGenero(false); setNewGeneroNome('') }}
            >
              ✕
            </Button>
          </div>
        ) : (
          <SearchCombobox
            items={generoItems}
            value={f.genero}
            onChange={(id) => setForm({ ...f, genero: id })}
            placeholder="Buscar gênero..."
            allowCreate
            onCreateNew={(text) => { setNewGeneroNome(text); setShowNewGenero(true) }}
          />
        )}
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        {/* Quantidade */}
        <div className="space-y-1.5">
          <Label>Quantidade *</Label>
          <Input
            type="number"
            min="1"
            value={f.quantidade}
            onChange={(e) => setForm({ ...f, quantidade: e.target.value })}
          />
          {errors.quantidade && <p className="text-xs text-destructive">{errors.quantidade}</p>}
        </div>

        {/* Conteúdo explícito */}
        <div className="flex items-center gap-3 pt-6">
          <input
            id="conteudo_explicito"
            type="checkbox"
            className="h-4 w-4 rounded border-border accent-primary cursor-pointer"
            checked={f.conteudo_explicito}
            onChange={(e) => setForm({ ...f, conteudo_explicito: e.target.checked })}
          />
          <Label htmlFor="conteudo_explicito" className="cursor-pointer">
            Contém conteúdo explícito
          </Label>
        </div>
      </div>

      {/* Sinopse */}
      <div className="space-y-1.5">
        <Label>Sinopse</Label>
        <textarea
          className="w-full rounded-xl border border-border bg-white px-3 py-2.5 text-sm resize-none outline-none focus:ring-2 focus:ring-primary/20"
          rows={4}
          placeholder="Resumo do livro (opcional)"
          value={f.sinopse}
          onChange={(e) => setForm({ ...f, sinopse: e.target.value })}
        />
      </div>

      {/* Capa */}
      <div className="space-y-1.5">
        <Label>
          Capa {isEdit && <span className="font-normal text-muted-foreground">(deixe vazio para manter)</span>}
        </Label>
        <Input
          type="file"
          accept="image/*"
          onChange={(e) => setForm({ ...f, capa: e.target.files[0] || null })}
        />
      </div>

      {errors.non_field_errors && (
        <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-destructive">{errors.non_field_errors}</p>
      )}

      {/* Botões */}
      <div className="flex justify-end gap-3 pt-2 border-t border-border">
        <Button variant="outline" onClick={onCancel}>Cancelar</Button>
        <Button
          onClick={() => salvarMutation.mutate()}
          disabled={!f.titulo || !f.autor || salvarMutation.isPending}
        >
          {salvarMutation.isPending ? 'Salvando...' : isEdit ? 'Salvar' : 'Criar livro'}
        </Button>
      </div>
    </div>
  )
}
