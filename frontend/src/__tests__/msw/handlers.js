import { http, HttpResponse } from 'msw'

/**
 * Fábricas de fixtures usadas pelos handlers e pelos testes.
 * Espelham o formato dos serializers do backend (core/serializers.py).
 */
export function makeLivro(overrides = {}) {
  return {
    id: 1,
    titulo: 'Dom Casmurro',
    autor: { id: 1, nome: 'Machado de Assis' },
    genero: { id: 1, nome: 'Romance' },
    conteudo_explicito: false,
    disponivel: true,
    capa: null,
    data_cadastro: '2024-01-01T00:00:00Z',
    total_emprestimos: 0,
    ...overrides,
  }
}

export function makeAluno(overrides = {}) {
  return {
    id: 1,
    matricula: '001',
    turma: { id: 1, nome: '1A', exibe_conteudo_explicito: false },
    nome_completo: 'Ana Souza',
    email: 'ana@example.com',
    username: 'ana',
    tem_pendencia: false,
    ...overrides,
  }
}

export function makeEmprestimo(overrides = {}) {
  return {
    id: 1,
    livro: makeLivro(),
    aluno_nome: 'Ana Souza',
    aluno_matricula: '001',
    data_emprestimo: '2024-01-01',
    data_devolucao_prevista: '2024-01-08',
    data_devolucao_real: null,
    status: 'ABERTO',
    esta_atrasado: false,
    ...overrides,
  }
}

export function makeReserva(overrides = {}) {
  return {
    id: 1,
    livro: makeLivro({ disponivel: false }),
    aluno_nome: 'Ana Souza',
    data_reserva: '2024-01-01',
    data_disponivel_prevista: '2024-01-10',
    status: 'ATIVA',
    ...overrides,
  }
}

export function makeResenha(overrides = {}) {
  return {
    id: 1,
    nota: 5,
    texto: 'Excelente',
    data_criacao: '2024-01-01T00:00:00Z',
    aluno_nome: 'Ana Souza',
    is_minha: false,
    livro: { id: 1, titulo: 'Dom Casmurro' },
    ...overrides,
  }
}

function paginated(results) {
  return { count: results.length, next: null, previous: null, results }
}

/**
 * Handlers padrão — retornam coleções vazias para evitar requisições
 * não tratadas. Cada teste sobrescreve o que precisa via `server.use(...)`.
 * O prefixo `*` casa com qualquer origem (jsdom resolve para http://localhost).
 */
export const handlers = [
  http.get('*/api/home/', () =>
    HttpResponse.json({ livros_recentes: [], livros_populares: [], livros_vestibular: [] })
  ),
  http.get('*/api/livros/', () => HttpResponse.json(paginated([]))),
  http.get('*/api/generos/', () => HttpResponse.json([])),
  http.get('*/api/meus-emprestimos/', () =>
    HttpResponse.json({ emprestimos: [], reservas: [] })
  ),
  http.get('*/api/staff/livros/', () => HttpResponse.json(paginated([]))),
  http.get('*/api/staff/alunos/', () => HttpResponse.json([])),
  http.get('*/api/staff/emprestimos/', () => HttpResponse.json([])),
  http.get('*/api/staff/reservas/', () => HttpResponse.json([])),
  http.get('*/api/staff/resenhas/', () => HttpResponse.json([])),
  http.get('*/api/staff/autores/', () => HttpResponse.json([])),
  http.get('*/api/staff/generos/', () => HttpResponse.json([])),
  http.get('*/api/staff/turmas/', () => HttpResponse.json([])),
]

export { paginated }
