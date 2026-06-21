import { useState } from 'react'
import { useNavigate, Navigate } from 'react-router-dom'
import { useAuth } from '@/auth/AuthContext'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

export default function LoginPage() {
  const { login, user } = useAuth()
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  if (user) return <Navigate to="/home" replace />

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)
    try {
      await login(username, password)
      navigate('/home', { replace: true })
    } catch {
      setError('Usuário ou senha inválidos.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen">
      {/* Painel esquerdo — identidade visual laranja */}
      <div className="hidden lg:flex lg:w-2/5 flex-col justify-between p-10 bg-gradient-highlight">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-white p-1.5 shrink-0">
            <img src="/favicon.svg" alt="Literarium" className="h-full w-full" />
          </div>
          <span className="text-white font-bold text-xl tracking-tight">Literarium</span>
        </div>

        <div className="space-y-3">
          <h2 className="text-3xl font-bold text-white leading-snug">
            Biblioteca do<br />Colégio Ideologia
          </h2>
          <p className="text-white/70 text-sm leading-relaxed max-w-xs">
            Acesse seu acervo, acompanhe seus empréstimos e descubra novos livros.
          </p>
        </div>

        <p className="text-white/35 text-xs">© {new Date().getFullYear()} Colégio Ideologia</p>
      </div>

      {/* Painel direito — formulário */}
      <div className="flex flex-1 items-center justify-center bg-background px-6 py-12">
        <div className="w-full max-w-sm space-y-8">

          {/* Logo mobile */}
          <div className="flex lg:hidden items-center gap-3 justify-center">
            <img src="/favicon.svg" alt="Literarium" className="h-9 w-9" />
            <span className="font-bold text-xl text-foreground">Literarium</span>
          </div>

          <div>
            <h1 className="text-2xl font-bold text-foreground">Bem-vindo</h1>
            <p className="text-sm text-muted-foreground mt-1">
              Entre com seu usuário e senha para continuar.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-1.5">
              <Label htmlFor="username">Usuário</Label>
              <Input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                autoComplete="username"
                autoFocus
                required
                placeholder="seu.usuario"
              />
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="password">Senha</Label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="current-password"
                required
                placeholder="••••••••"
              />
            </div>

            {error && (
              <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-destructive">{error}</p>
            )}

            <Button type="submit" className="w-full mt-2" disabled={isLoading}>
              {isLoading ? 'Entrando...' : 'Entrar'}
            </Button>
          </form>
        </div>
      </div>
    </div>
  )
}
