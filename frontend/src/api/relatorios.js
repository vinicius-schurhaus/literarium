import api from './client'

export async function getRelatorioEmprestimos({ data_inicio, data_fim }) {
  const { data } = await api.get('/relatorios/emprestimos/', { params: { data_inicio, data_fim } })
  return data
}

export async function getRelatorioDevolucoes({ data_inicio, data_fim }) {
  const { data } = await api.get('/relatorios/devolucoes/', { params: { data_inicio, data_fim } })
  return data
}

export function exportarCsvUrl(tipo, data_inicio, data_fim) {
  const params = new URLSearchParams({ data_inicio, data_fim, exportar: '1' })
  return `/api/relatorios/${tipo}/?${params}`
}
