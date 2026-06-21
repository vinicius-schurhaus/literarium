import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Download, Search } from 'lucide-react'
import { getRelatorioEmprestimos, getRelatorioDevolucoes, exportarCsvUrl } from '@/api/relatorios'
import StatusBadge from '@/components/emprestimos/StatusBadge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

function fmt(date) {
  if (!date) return '—'
  return new Date(date).toLocaleDateString('pt-BR')
}

export default function RelatorioPage({ tipo }) {
  const isEmprestimos = tipo === 'emprestimos'
  const title = isEmprestimos ? 'Relatório de Empréstimos' : 'Relatório de Devoluções'

  const today = new Date().toISOString().slice(0, 10)
  const firstOfMonth = new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString().slice(0, 10)

  const [dataInicio, setDataInicio] = useState(firstOfMonth)
  const [dataFim, setDataFim] = useState(today)
  const [filtros, setFiltros] = useState(null)

  const { data = [], isLoading } = useQuery({
    queryKey: ['relatorio', tipo, filtros],
    queryFn: () => isEmprestimos
      ? getRelatorioEmprestimos({ data_inicio: filtros.dataInicio, data_fim: filtros.dataFim })
      : getRelatorioDevolucoes({ data_inicio: filtros.dataInicio, data_fim: filtros.dataFim }),
    enabled: !!filtros,
  })

  const handleFiltrar = (e) => {
    e.preventDefault()
    setFiltros({ dataInicio, dataFim })
  }

  const handleExportar = () => {
    if (!filtros) return
    const url = exportarCsvUrl(tipo, filtros.dataInicio, filtros.dataFim)
    const a = document.createElement('a')
    a.href = url
    a.download = `${tipo}.csv`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold">{title}</h1>
        {filtros && (
          <Button variant="outline" size="sm" onClick={handleExportar}>
            <Download className="mr-1.5 h-4 w-4" />
            Exportar CSV
          </Button>
        )}
      </div>

      <form onSubmit={handleFiltrar} className="flex flex-wrap items-end gap-4 rounded-xl border border-border bg-white p-4">
        <div className="space-y-1.5">
          <Label>Data inicial</Label>
          <Input type="date" value={dataInicio} onChange={(e) => setDataInicio(e.target.value)} required />
        </div>
        <div className="space-y-1.5">
          <Label>Data final</Label>
          <Input type="date" value={dataFim} onChange={(e) => setDataFim(e.target.value)} required />
        </div>
        <Button type="submit">
          <Search className="mr-1.5 h-4 w-4" />
          Filtrar
        </Button>
      </form>

      {filtros && (
        isLoading ? (
          <div className="flex justify-center py-10">
            <div className="h-7 w-7 animate-spin rounded-full border-4 border-orange-500 border-t-transparent" />
          </div>
        ) : (
          <div className="rounded-xl border border-border bg-white overflow-hidden">
            <div className="px-4 py-3 border-b border-border text-sm text-muted-foreground">
              {data.length} resultado{data.length !== 1 ? 's' : ''}
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border bg-gray-50">
                    <th className="px-4 py-3 text-left font-medium text-muted-foreground">Livro</th>
                    <th className="px-4 py-3 text-left font-medium text-muted-foreground">Aluno</th>
                    <th className="px-4 py-3 text-left font-medium text-muted-foreground">Matrícula</th>
                    <th className="px-4 py-3 text-left font-medium text-muted-foreground">Retirada</th>
                    <th className="px-4 py-3 text-left font-medium text-muted-foreground">Prev. Devolução</th>
                    {!isEmprestimos && <th className="px-4 py-3 text-left font-medium text-muted-foreground">Devolvido em</th>}
                    <th className="px-4 py-3 text-left font-medium text-muted-foreground">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {data.length === 0 ? (
                    <tr>
                      <td colSpan="7" className="py-10 text-center text-muted-foreground">Nenhum resultado.</td>
                    </tr>
                  ) : data.map((e) => (
                    <tr key={e.id} className="border-b border-border last:border-0">
                      <td className="px-4 py-3">{e.livro?.titulo}</td>
                      <td className="px-4 py-3">{e.aluno_nome}</td>
                      <td className="px-4 py-3">{e.aluno_matricula}</td>
                      <td className="px-4 py-3">{fmt(e.data_emprestimo)}</td>
                      <td className="px-4 py-3">{fmt(e.data_devolucao_prevista)}</td>
                      {!isEmprestimos && <td className="px-4 py-3">{fmt(e.data_devolucao_real)}</td>}
                      <td className="px-4 py-3">
                        <StatusBadge status={e.status} estaAtrasado={e.esta_atrasado} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )
      )}
    </div>
  )
}
