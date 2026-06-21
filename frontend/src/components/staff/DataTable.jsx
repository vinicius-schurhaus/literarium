import { Search, Pencil, Trash2 } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'

export default function DataTable({
  columns,
  data: rawData = [],
  isLoading,
  onEdit,
  onDelete,
  actions,
  searchPlaceholder = 'Buscar...',
  onSearch,
  searchValue,
  onSearchChange,
  extraFilters,
}) {
  const data = Array.isArray(rawData) ? rawData : (rawData?.results ?? [])

  const handleSearchSubmit = (e) => {
    e.preventDefault()
    onSearch?.()
  }

  return (
    <div className="space-y-3">
      {(onSearchChange || extraFilters) && (
        <form onSubmit={handleSearchSubmit} className="flex flex-wrap gap-2">
          {onSearchChange && (
            <div className="flex gap-2 flex-1 min-w-48">
              <Input
                placeholder={searchPlaceholder}
                value={searchValue || ''}
                onChange={(e) => onSearchChange(e.target.value)}
              />
              <Button type="submit" variant="outline" size="icon">
                <Search className="h-4 w-4" />
              </Button>
            </div>
          )}
          {extraFilters}
        </form>
      )}

      <div className="rounded-xl border border-border bg-card overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border bg-muted/60">
                {columns.map((col) => (
                  <th
                    key={col.key}
                    className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-muted-foreground"
                    style={col.width ? { width: col.width } : undefined}
                  >
                    {col.label}
                  </th>
                ))}
                {(onEdit || onDelete || actions) && (
                  <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                    Ações
                  </th>
                )}
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr>
                  <td colSpan={columns.length + 1} className="py-16 text-center text-muted-foreground">
                    <div className="flex justify-center">
                      <div className="h-6 w-6 animate-spin rounded-full border-4 border-primary border-t-transparent" />
                    </div>
                  </td>
                </tr>
              ) : data.length === 0 ? (
                <tr>
                  <td colSpan={columns.length + 1} className="py-16 text-center text-muted-foreground text-sm">
                    Nenhum item encontrado.
                  </td>
                </tr>
              ) : (
                data.map((row, i) => (
                  <tr
                    key={row.id ?? i}
                    className="border-b border-border last:border-0 hover:bg-muted/40 transition-colors h-16"
                  >
                    {columns.map((col) => (
                      <td key={col.key} className="px-4 py-2 text-sm text-foreground align-middle">
                        {col.render ? col.render(row) : (row[col.key] ?? <span className="text-muted-foreground">—</span>)}
                      </td>
                    ))}
                    {(onEdit || onDelete || actions) && (
                      <td className="px-4 py-3">
                        <div className="flex justify-end gap-1.5">
                          {actions?.(row)}
                          {onEdit && (
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => onEdit(row)}
                              title="Editar"
                              className="h-8 w-8 text-muted-foreground hover:text-foreground"
                            >
                              <Pencil className="h-3.5 w-3.5" />
                            </Button>
                          )}
                          {onDelete && (
                            <Button
                              variant="ghost"
                              size="icon"
                              className="h-8 w-8 text-muted-foreground hover:text-destructive hover:bg-destructive/10"
                              onClick={() => onDelete(row)}
                              title="Excluir"
                            >
                              <Trash2 className="h-3.5 w-3.5" />
                            </Button>
                          )}
                        </div>
                      </td>
                    )}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
