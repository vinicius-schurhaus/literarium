import api from './client'

export async function getMeusEmprestimos() {
  const { data } = await api.get('/meus-emprestimos/')
  return data
}

export async function renovarEmprestimo(id) {
  const { data } = await api.post(`/emprestimos/${id}/renovar/`)
  return data
}

export async function cancelarReserva(id) {
  const { data } = await api.post(`/minhas-reservas/${id}/cancelar/`)
  return data
}
