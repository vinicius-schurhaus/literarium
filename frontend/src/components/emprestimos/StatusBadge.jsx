import { Badge } from '@/components/ui/badge'

export default function StatusBadge({ status, estaAtrasado }) {
  if (estaAtrasado) {
    return <Badge variant="destructive">Atrasado</Badge>
  }
  if (status === 'DEVOLVIDO') {
    return <Badge variant="success">Devolvido</Badge>
  }
  return <Badge variant="warning">Em aberto</Badge>
}
