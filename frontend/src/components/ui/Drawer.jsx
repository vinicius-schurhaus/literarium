import { X } from 'lucide-react'
import { cn } from '@/lib/utils'

/**
 * Drawer — painel lateral deslizante.
 * Props: open, onClose, title, children, width ('md'|'lg')
 */
export default function Drawer({ open, onClose, title, children, width = 'md' }) {
  if (!open) return null

  const widthClass = width === 'lg' ? 'max-w-2xl' : 'max-w-xl'

  return (
    <>
      {/* Overlay */}
      <div
        className="fixed inset-0 z-40 bg-black/30 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Painel */}
      <div className={cn(
        'fixed right-0 top-0 z-50 flex h-full w-full flex-col bg-white shadow-2xl',
        widthClass
      )}>
        {/* Header */}
        <div className="flex items-center justify-between border-b border-border px-6 py-4 shrink-0">
          <h2 className="text-lg font-bold text-foreground">{title}</h2>
          <button
            onClick={onClose}
            className="flex h-8 w-8 items-center justify-center rounded-lg text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Conteúdo */}
        <div className="flex-1 overflow-y-auto px-6 py-5">
          {children}
        </div>
      </div>
    </>
  )
}
