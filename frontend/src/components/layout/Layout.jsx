import { Outlet, NavLink, useLocation, useNavigate, Link } from 'react-router-dom'
import {
  Home, Search, BookOpen, BookMarked, CalendarClock,
  LogOut, Settings, User, GraduationCap, Users, Star,
  BarChart2, Tag, UserSquare2,
} from 'lucide-react'
import { useState, useRef, useEffect } from 'react'
import { useAuth } from '@/auth/AuthContext'
import ErrorBoundary from '@/components/ErrorBoundary'
import { LivroDrawerProvider, useLivroDrawer } from '@/contexts/LivroDrawerContext'
import Drawer from '@/components/ui/Drawer'
import LivroDetalhesContent from '@/components/livros/LivroDetalhesContent'

function NavItem({ to, icon: Icon, label, end = false }) {
  return (
    <NavLink
      to={to}
      end={end}
      className={({ isActive }) =>
        [
          'flex w-full items-center gap-3 text-sm font-medium transition-colors border-r-4',
          isActive
            ? 'bg-accent text-primary border-primary'
            : 'text-slate-500 border-transparent hover:bg-slate-50 hover:text-slate-800',
        ].join(' ')
      }
      style={{ padding: '21px 24px' }}
    >
      {Icon && <Icon size={18} className="shrink-0" />}
      {label}
    </NavLink>
  )
}

function SectionLabel({ children }) {
  return (
    <p className="px-5 pt-5 pb-1 text-xs font-semibold uppercase tracking-widest text-slate-400">
      {children}
    </p>
  )
}

function LayoutInner() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const { pathname } = useLocation()
  const [menuOpen, setMenuOpen] = useState(false)
  const menuRef = useRef(null)
  const { livroId, closeLivro } = useLivroDrawer()

  const handleLogout = () => {
    logout()
    navigate('/login', { replace: true })
  }

  useEffect(() => {
    const handler = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) setMenuOpen(false)
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <aside className="flex w-64 flex-col bg-white border-r border-border shrink-0">

        <div className="flex items-center gap-3 px-5 py-5">
          <img src="/favicon.svg" alt="Literarium" className="h-12 w-12 shrink-0" />
          <span className="font-bold text-foreground text-xl">Literarium</span>
        </div>

        <nav className="flex-1 overflow-y-auto py-2">
          <NavItem to="/home" icon={Home} label="Início" end />
          <NavItem to="/pesquisar" icon={Search} label="Pesquisar" />
          <NavItem to="/catalogo" icon={BookOpen} label="Catálogo" />

          {/* Seção do aluno */}
          {user?.has_aluno_perfil && (
            <>
              <SectionLabel>Minhas estantes</SectionLabel>
              <NavItem to="/meus-emprestimos" icon={BookMarked} label="Meus Livros" />
            </>
          )}

          {/* Seção de gestão — integrada ao mesmo menu */}
          {user?.is_staff && (
            <>
              <SectionLabel>Gestão</SectionLabel>
              <NavItem to="/staff/livros" icon={BookOpen} label="Livros" />
              <NavItem to="/staff/autores" icon={UserSquare2} label="Autores" />
              <NavItem to="/staff/generos" icon={Tag} label="Gêneros" />
              <NavItem to="/staff/alunos" icon={GraduationCap} label="Alunos" />
              <NavItem to="/staff/turmas" icon={Users} label="Turmas" />
              <NavItem to="/staff/emprestimos" icon={BookMarked} label="Empréstimos" />
              <NavItem to="/staff/reservas" icon={CalendarClock} label="Reservas" />
              <NavItem to="/staff/resenhas" icon={Star} label="Resenhas" />
              <SectionLabel>Relatórios</SectionLabel>
              <NavItem to="/staff/relatorios/emprestimos" icon={BarChart2} label="Empréstimos" />
              <NavItem to="/staff/relatorios/devolucoes" icon={BarChart2} label="Devoluções" />
            </>
          )}
        </nav>

        {/* Rodapé — apenas info do usuário */}
        <div className="border-t border-border px-5 py-4">
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/15 text-primary font-bold text-sm shrink-0">
              {(user?.first_name?.[0] || user?.username?.[0] || 'U').toUpperCase()}
            </div>
            <div className="min-w-0">
              <p className="text-sm font-medium text-foreground truncate leading-tight">
                {user?.first_name
                  ? `${user.first_name} ${user.last_name || ''}`.trim()
                  : user?.username}
              </p>
              <p className="text-xs text-muted-foreground truncate">
                {user?.email || ''}
              </p>
            </div>
          </div>
        </div>
      </aside>

      {/* Área principal */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Topbar com avatar (alterar senha + sair) */}
        <div
          className="flex items-center justify-end shrink-0"
          style={{ padding: 16, ...(pathname === '/pesquisar' ? { background: 'linear-gradient(90deg, #F79633 0%, #D83135 100%)' } : { background: 'transparent' }) }}
        >
          <div className="relative" ref={menuRef}>
            <button
              onClick={() => setMenuOpen((v) => !v)}
              title="Perfil"
              className="flex items-center justify-center cursor-pointer hover:scale-110 transition-transform"
              style={{
                width: 48,
                height: 48,
                borderRadius: 10,
                backgroundColor: pathname === '/pesquisar' ? '#F4A460' : '#DFE4EB',
              }}
            >
              <User size={22} strokeWidth={2.5} style={{ color: pathname === '/pesquisar' ? '#ffffff' : '#1C1C1C' }} />
            </button>

            {menuOpen && (
              <div className="absolute right-0 mt-2 w-52 border border-border bg-white shadow-lg py-1 z-50 rounded-xl overflow-hidden">
                <div className="px-4 py-2.5 border-b border-border">
                  <p className="text-sm font-semibold text-foreground truncate">
                    {user?.first_name
                      ? `${user.first_name} ${user.last_name || ''}`.trim()
                      : user?.username}
                  </p>
                  <p className="text-xs text-muted-foreground">{user?.email || ''}</p>
                </div>
                <Link
                  to="/conta/alterar-senha"
                  onClick={() => setMenuOpen(false)}
                  className="flex items-center gap-2.5 px-4 py-2.5 text-sm text-foreground hover:bg-muted transition-colors"
                >
                  <Settings size={14} className="text-muted-foreground" />
                  Alterar senha
                </Link>
                <div className="border-t border-border mt-1 pt-1">
                  <button
                    onClick={handleLogout}
                    className="flex w-full items-center gap-2.5 px-4 py-2.5 text-sm text-destructive hover:bg-red-50 transition-colors"
                  >
                    <LogOut size={14} />
                    Sair
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        <main className="flex-1 overflow-y-auto bg-background p-6 md:p-8">
          <ErrorBoundary key={pathname}>
            <Outlet />
          </ErrorBoundary>
        </main>
      </div>

      <Drawer
        open={!!livroId}
        onClose={closeLivro}
        title="Detalhes do livro"
        width="lg"
      >
        {livroId && <LivroDetalhesContent livroId={livroId} />}
      </Drawer>
    </div>
  )
}

export default function Layout() {
  return (
    <LivroDrawerProvider>
      <LayoutInner />
    </LivroDrawerProvider>
  )
}
