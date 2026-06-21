import LookupPage from './LookupPage'
import { staffAutores } from '@/api/staff'

export default function AutoresPage() {
  return <LookupPage title="Autores" queryKey="staff-autores" api={staffAutores} />
}
