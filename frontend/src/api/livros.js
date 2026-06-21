import api from './client'

export async function getLivros({ q, genero, page } = {}) {
  const params = {}
  if (q) params.q = q
  if (genero) params.genero = genero
  if (page) params.page = page
  const { data } = await api.get('/livros/', { params })
  return data
}

export async function getLivro(id) {
  const { data } = await api.get(`/livros/${id}/`)
  return data
}

export async function getLivroStatusAluno(id) {
  const { data } = await api.get(`/livros/${id}/status-aluno/`)
  return data
}

export async function getLivrosPopulares() {
  const { data } = await api.get('/livros/populares/')
  return data
}

export async function getHome() {
  const { data } = await api.get('/home/')
  return data
}

export async function getGeneros() {
  const { data } = await api.get('/generos/')
  return data
}

export async function getResenhas(livroId) {
  const { data } = await api.get(`/livros/${livroId}/resenhas/`)
  return data
}

export async function salvarResenha(livroId, nota, texto) {
  const { data } = await api.post(`/livros/${livroId}/resenha/`, { nota, texto })
  return data
}

export async function reservarLivro(livroId) {
  const { data } = await api.post(`/livros/${livroId}/reservar/`)
  return data
}
