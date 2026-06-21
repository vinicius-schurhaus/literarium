import { Routes, Route, Navigate } from 'react-router-dom'
import { ProtectedRoute } from './auth/ProtectedRoute'
import { StaffRoute } from './auth/StaffRoute'
import { AlunoRoute } from './auth/AlunoRoute'

import Layout from './components/layout/Layout'

import LoginPage from './pages/LoginPage'
import HomePage from './pages/HomePage'
import PesquisarPage from './pages/PesquisarPage'
import CatalogoPage from './pages/CatalogoPage'
import LivroDetalhesPage from './pages/LivroDetalhesPage'
import LivrosPopularesPage from './pages/LivrosPopularesPage'
import MeusEmprestimosPage from './pages/MeusEmprestimosPage'
import AlterarSenhaPage from './pages/AlterarSenhaPage'

import LivrosPage from './pages/staff/LivrosPage'
import AlunosPage from './pages/staff/AlunosPage'
import EmprestimosPage from './pages/staff/EmprestimosPage'
import ReservasPage from './pages/staff/ReservasPage'
import ResenhasPage from './pages/staff/ResenhasPage'
import AutoresPage from './pages/staff/AutoresPage'
import GenerosPage from './pages/staff/GenerosPage'
import TurmasPage from './pages/staff/TurmasPage'
import RelatorioPage from './pages/staff/RelatorioPage'

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />

      {/* Layout único para todos os usuários */}
      <Route element={<ProtectedRoute />}>
        <Route element={<Layout />}>
          <Route index element={<Navigate to="/home" replace />} />

          {/* Portal do aluno */}
          <Route path="/home" element={<HomePage />} />
          <Route path="/pesquisar" element={<PesquisarPage />} />
          <Route path="/catalogo" element={<CatalogoPage />} />
          <Route path="/livros/populares" element={<LivrosPopularesPage />} />
          <Route path="/livros/:livroId" element={<LivroDetalhesPage />} />
          <Route path="/conta/alterar-senha" element={<AlterarSenhaPage />} />
          <Route element={<AlunoRoute />}>
            <Route path="/meus-emprestimos" element={<MeusEmprestimosPage />} />
          </Route>

          {/* Gestão — no mesmo layout, exibe seção extra na sidebar */}
          <Route element={<StaffRoute />}>
            <Route path="/staff" element={<Navigate to="/staff/livros" replace />} />
            <Route path="/staff/livros" element={<LivrosPage />} />
            <Route path="/staff/alunos" element={<AlunosPage />} />
            <Route path="/staff/emprestimos" element={<EmprestimosPage />} />
            <Route path="/staff/reservas" element={<ReservasPage />} />
            <Route path="/staff/resenhas" element={<ResenhasPage />} />
            <Route path="/staff/autores" element={<AutoresPage />} />
            <Route path="/staff/generos" element={<GenerosPage />} />
            <Route path="/staff/turmas" element={<TurmasPage />} />
            <Route path="/staff/relatorios/emprestimos" element={<RelatorioPage tipo="emprestimos" />} />
            <Route path="/staff/relatorios/devolucoes" element={<RelatorioPage tipo="devolucoes" />} />
          </Route>
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/home" replace />} />
    </Routes>
  )
}
