import { useState, useRef, useEffect } from 'react'
import { Search, X, Plus, Check } from 'lucide-react'
import { cn } from '@/lib/utils'

/**
 * SearchCombobox — input com busca e lista dropdown.
 *
 * Props:
 *   items        [{id, label, sublabel?}]
 *   value        id selecionado (string ou number)
 *   onChange     (id) => void
 *   placeholder  string
 *   allowCreate  bool — mostra opção "Criar: X" quando sem resultado
 *   onCreateNew  (text) => void
 *   disabled     bool
 */
export default function SearchCombobox({
  items = [],
  value,
  onChange,
  placeholder = 'Buscar...',
  allowCreate = false,
  onCreateNew,
  disabled = false,
}) {
  const selected = items.find((i) => String(i.id) === String(value))
  const [query, setQuery] = useState('')
  const [open, setOpen] = useState(false)
  const containerRef = useRef(null)

  useEffect(() => {
    const handler = (e) => {
      if (containerRef.current && !containerRef.current.contains(e.target)) setOpen(false)
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  const filtered = query
    ? items.filter(
        (i) =>
          i.label.toLowerCase().includes(query.toLowerCase()) ||
          i.sublabel?.toLowerCase().includes(query.toLowerCase())
      )
    : items

  const handleSelect = (id) => {
    onChange(id)
    setQuery('')
    setOpen(false)
  }

  const handleClear = () => {
    onChange('')
    setQuery('')
  }

  const handleCreate = () => {
    onCreateNew?.(query)
    setQuery('')
    setOpen(false)
  }

  return (
    <div className="relative" ref={containerRef}>
      <div
        className={cn(
          'flex items-center gap-2 rounded-xl border border-border bg-white px-3 py-2 transition-colors',
          open ? 'border-primary ring-2 ring-primary/15' : 'hover:border-slate-300',
          disabled && 'opacity-50 pointer-events-none'
        )}
        onClick={() => !disabled && setOpen(true)}
      >
        <Search className="h-3.5 w-3.5 text-muted-foreground shrink-0" />
        {open || !selected ? (
          <input
            autoFocus={open}
            className="flex-1 bg-transparent text-sm outline-none placeholder-muted-foreground"
            placeholder={selected ? selected.label : placeholder}
            value={query}
            onChange={(e) => { setQuery(e.target.value); setOpen(true) }}
            onFocus={() => setOpen(true)}
          />
        ) : (
          <span className="flex-1 text-sm text-foreground truncate">{selected.label}</span>
        )}
        {selected && !open && (
          <button
            type="button"
            onClick={(e) => { e.stopPropagation(); handleClear() }}
            className="text-muted-foreground hover:text-foreground transition-colors"
          >
            <X className="h-3.5 w-3.5" />
          </button>
        )}
      </div>

      {open && (
        <div className="absolute z-50 mt-1 w-full rounded-xl border border-border bg-white shadow-lg overflow-hidden max-h-56 overflow-y-auto">
          {filtered.length === 0 && !allowCreate && (
            <p className="px-4 py-3 text-sm text-muted-foreground">Nenhum resultado.</p>
          )}
          {filtered.map((item) => (
            <button
              key={item.id}
              type="button"
              onClick={() => handleSelect(String(item.id))}
              className="flex w-full items-center justify-between gap-2 px-4 py-2.5 text-left text-sm hover:bg-orange-50 transition-colors"
            >
              <span className="min-w-0">
                <span className="block font-medium text-foreground truncate">{item.label}</span>
                {item.sublabel && (
                  <span className="block text-xs text-muted-foreground truncate">{item.sublabel}</span>
                )}
              </span>
              {String(value) === String(item.id) && (
                <Check className="h-3.5 w-3.5 text-primary shrink-0" />
              )}
            </button>
          ))}
          {allowCreate && query.trim() && filtered.length === 0 && (
            <button
              type="button"
              onClick={handleCreate}
              className="flex w-full items-center gap-2 px-4 py-2.5 text-sm text-primary hover:bg-accent transition-colors font-medium"
            >
              <Plus className="h-3.5 w-3.5 shrink-0" />
              Criar &quot;{query.trim()}&quot;
            </button>
          )}
        </div>
      )}
    </div>
  )
}
