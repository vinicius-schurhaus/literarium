import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { changePassword } from '@/api/auth'
import { useAuth } from '@/auth/AuthContext'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

const fields = [
  { key: 'old_password', label: 'Senha atual', autoComplete: 'current-password' },
  { key: 'new_password1', label: 'Nova senha', autoComplete: 'new-password' },
  { key: 'new_password2', label: 'Confirmar nova senha', autoComplete: 'new-password' },
]

export default function AlterarSenhaPage() {
  const { logout } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ old_password: '', new_password1: '', new_password2: '' })
  const [errors, setErrors] = useState({})
  const [isLoading, setIsLoading] = useState(false)

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setErrors({})
    setIsLoading(true)
    try {
      await changePassword(form.old_password, form.new_password1, form.new_password2)
      logout()
      navigate('/login', { replace: true, state: { message: 'Senha alterada. Por favor, entre novamente.' } })
    } catch (err) {
      setErrors(err.response?.data || { detail: 'Erro ao alterar senha.' })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="max-w-md space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Alterar senha</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Após salvar você será redirecionado para o login.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4 rounded-xl border border-border bg-card p-6 shadow-sm">
        {fields.map(({ key, label, autoComplete }) => (
          <div key={key} className="space-y-1.5">
            <Label htmlFor={key}>{label}</Label>
            <Input
              id={key}
              name={key}
              type="password"
              value={form[key]}
              onChange={handleChange}
              required
              autoComplete={autoComplete}
            />
            {errors[key] && (
              <p className="text-xs text-red-500">
                {Array.isArray(errors[key]) ? errors[key].join(' ') : errors[key]}
              </p>
            )}
          </div>
        ))}

        {errors.detail && (
          <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-destructive">{errors.detail}</p>
        )}

        <div className="flex gap-2 pt-2">
          <Button type="submit" disabled={isLoading}>
            {isLoading ? 'Salvando...' : 'Alterar senha'}
          </Button>
          <Button type="button" variant="outline" onClick={() => navigate(-1)}>
            Cancelar
          </Button>
        </div>
      </form>
    </div>
  )
}
