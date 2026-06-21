import api from './client'

// Livros
export const staffLivros = {
  list: (params = {}) => api.get('/staff/livros/', { params }).then(r => r.data),
  get: (id) => api.get(`/staff/livros/${id}/`).then(r => r.data),
  create: (data) => api.post('/staff/livros/', data, { headers: { 'Content-Type': 'multipart/form-data' } }).then(r => r.data),
  update: (id, data) => api.put(`/staff/livros/${id}/`, data, { headers: { 'Content-Type': 'multipart/form-data' } }).then(r => r.data),
  delete: (id) => api.delete(`/staff/livros/${id}/`),
}

// Alunos
export const staffAlunos = {
  list: (params = {}) => api.get('/staff/alunos/', { params }).then(r => r.data),
  get: (id) => api.get(`/staff/alunos/${id}/`).then(r => r.data),
  create: (data) => api.post('/staff/alunos/', data).then(r => r.data),
  update: (id, data) => api.put(`/staff/alunos/${id}/`, data).then(r => r.data),
  delete: (id) => api.delete(`/staff/alunos/${id}/`),
}

// Empréstimos
export const staffEmprestimos = {
  list: (params = {}) => api.get('/staff/emprestimos/', { params }).then(r => r.data),
  create: (livro_id, aluno_id) => api.post('/staff/emprestimos/', { livro_id, aluno_id }).then(r => r.data),
  devolver: (id) => api.post(`/staff/emprestimos/${id}/devolver/`).then(r => r.data),
}

// Reservas
export const staffReservas = {
  list: (params = {}) => api.get('/staff/reservas/', { params }).then(r => r.data),
  cancelar: (id) => api.post(`/staff/reservas/${id}/cancelar/`).then(r => r.data),
}

// Resenhas
export const staffResenhas = {
  list: (params = {}) => api.get('/staff/resenhas/', { params }).then(r => r.data),
  delete: (id) => api.delete(`/staff/resenhas/${id}/`),
}

// Lookups
export const staffAutores = {
  list: () => api.get('/staff/autores/').then(r => r.data),
  create: (data) => api.post('/staff/autores/', data).then(r => r.data),
  update: (id, data) => api.put(`/staff/autores/${id}/`, data).then(r => r.data),
  delete: (id) => api.delete(`/staff/autores/${id}/`),
}

export const staffGeneros = {
  list: () => api.get('/staff/generos/').then(r => r.data),
  create: (data) => api.post('/staff/generos/', data).then(r => r.data),
  update: (id, data) => api.put(`/staff/generos/${id}/`, data).then(r => r.data),
  delete: (id) => api.delete(`/staff/generos/${id}/`),
}

export const staffTurmas = {
  list: () => api.get('/staff/turmas/').then(r => r.data),
  create: (data) => api.post('/staff/turmas/', data).then(r => r.data),
  update: (id, data) => api.put(`/staff/turmas/${id}/`, data).then(r => r.data),
  delete: (id) => api.delete(`/staff/turmas/${id}/`),
}
