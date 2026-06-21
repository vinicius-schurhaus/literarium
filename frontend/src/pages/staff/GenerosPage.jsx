import LookupPage from './LookupPage'
import { staffGeneros } from '@/api/staff'

export default function GenerosPage() {
  return <LookupPage title="Gêneros" queryKey="staff-generos" api={staffGeneros} />
}
