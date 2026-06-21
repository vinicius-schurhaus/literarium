import { Star } from 'lucide-react'
import { cn } from '@/lib/utils'

export default function StarRating({ value, onChange, readonly = false, size = 'md' }) {
  const sizeClass = { sm: 'h-3.5 w-3.5', md: 'h-5 w-5', lg: 'h-6 w-6' }[size]

  return (
    <div className="flex gap-0.5">
      {[1, 2, 3, 4, 5].map((star) => (
        <button
          key={star}
          type="button"
          disabled={readonly}
          onClick={() => onChange?.(star)}
          className={cn('focus:outline-none transition-colors', !readonly && 'hover:scale-110')}
        >
          <Star
            className={cn(
              sizeClass,
              star <= value ? 'fill-orange-400 text-orange-400' : 'text-gray-300',
              !readonly && 'cursor-pointer'
            )}
          />
        </button>
      ))}
    </div>
  )
}
