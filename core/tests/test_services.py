from datetime import date, timedelta

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from core.models import Aluno, Autor, Emprestimo, Genero, Livro, Reserva
from core import services


def _criar_aluno(username, matricula, turma=None):
    user = User.objects.create_user(username=username, password="pass")
    return Aluno.objects.create(usuario=user, matricula=matricula, turma=turma)


def _criar_livro(titulo, quantidade=2):
    autor, _ = Autor.objects.get_or_create(nome="Autor Padrão")
    return Livro.objects.create(titulo=titulo, autor=autor, quantidade=quantidade)


class RegistrarEmprestimoServiceTest(TestCase):
    def setUp(self):
        self.aluno = _criar_aluno("aluno1", "001")
        self.livro = _criar_livro("Livro A", quantidade=2)

    def test_registrar_emprestimo_cria_e_decrementa(self):
        emp = services.registrar_emprestimo(self.aluno, self.livro)
        self.livro.refresh_from_db()
        self.assertEqual(self.livro.quantidade, 1)
        self.assertIsNotNone(emp.pk)

    def test_registrar_emprestimo_bloqueia_aluno_com_pendencia(self):
        emp = Emprestimo(
            aluno=self.aluno,
            livro=self.livro,
            data_devolucao_prevista=date.today() - timedelta(days=1),
        )
        emp.save()
        livro2 = _criar_livro("Livro B", quantidade=1)
        with self.assertRaises(ValidationError):
            services.registrar_emprestimo(self.aluno, livro2)

    def test_registrar_emprestimo_sem_estoque_levanta_erro(self):
        self.livro.quantidade = 0
        self.livro.save()
        with self.assertRaises((ValidationError, Exception)):
            services.registrar_emprestimo(self.aluno, self.livro)


class DevolverEmprestimoServiceTest(TestCase):
    def setUp(self):
        self.aluno = _criar_aluno("aluno1", "001")
        self.livro = _criar_livro("Livro A", quantidade=1)
        self.emprestimo = services.registrar_emprestimo(self.aluno, self.livro)

    def test_devolver_atualiza_status_e_estoque(self):
        services.devolver_emprestimo(self.emprestimo)
        self.emprestimo.refresh_from_db()
        self.livro.refresh_from_db()
        self.assertEqual(self.emprestimo.status, "DEVOLVIDO")
        self.assertEqual(self.livro.quantidade, 1)

    def test_devolver_ja_devolvido_levanta_erro(self):
        services.devolver_emprestimo(self.emprestimo)
        with self.assertRaises(ValidationError):
            services.devolver_emprestimo(self.emprestimo)

    def test_devolver_atende_proxima_reserva(self):
        aluno2 = _criar_aluno("aluno2", "002")
        reserva = Reserva.objects.create(aluno=aluno2, livro=self.livro, status="ATIVA")
        services.devolver_emprestimo(self.emprestimo)
        reserva.refresh_from_db()
        self.assertEqual(reserva.status, "ATENDIDA")


class RenovarEmprestimoServiceTest(TestCase):
    def setUp(self):
        self.aluno = _criar_aluno("aluno1", "001")
        self.livro = _criar_livro("Livro A", quantidade=1)
        self.emprestimo = services.registrar_emprestimo(self.aluno, self.livro)

    def test_renovar_adiciona_sete_dias(self):
        data_original = self.emprestimo.data_devolucao_prevista
        services.renovar_emprestimo(self.emprestimo)
        self.emprestimo.refresh_from_db()
        self.assertEqual(self.emprestimo.data_devolucao_prevista, timezone.now().date() + timedelta(days=7))

    def test_renovar_devolvido_levanta_erro(self):
        services.devolver_emprestimo(self.emprestimo)
        with self.assertRaises(ValidationError):
            services.renovar_emprestimo(self.emprestimo)

    def test_renovar_respeita_proxima_reserva(self):
        aluno2 = _criar_aluno("aluno2", "002")
        proxima_data = timezone.now().date() + timedelta(days=3)
        Reserva.objects.create(
            aluno=aluno2,
            livro=self.livro,
            status="ATIVA",
            data_disponivel_prevista=proxima_data,
        )
        services.renovar_emprestimo(self.emprestimo)
        self.emprestimo.refresh_from_db()
        self.assertEqual(self.emprestimo.data_devolucao_prevista, proxima_data)


class CriarReservaServiceTest(TestCase):
    def setUp(self):
        self.aluno = _criar_aluno("aluno1", "001")
        self.livro = _criar_livro("Livro Esgotado", quantidade=0)

    def test_criar_reserva_cria_com_data_prevista(self):
        reserva = services.criar_reserva(self.aluno, self.livro)
        self.assertEqual(reserva.status, "ATIVA")
        self.assertIsNotNone(reserva.data_disponivel_prevista)

    def test_criar_reserva_duplicada_levanta_erro(self):
        services.criar_reserva(self.aluno, self.livro)
        with self.assertRaises(ValidationError):
            services.criar_reserva(self.aluno, self.livro)

    def test_criar_reserva_em_livro_disponivel_levanta_erro(self):
        livro_disponivel = _criar_livro("Livro Disponível", quantidade=1)
        with self.assertRaises(ValidationError):
            services.criar_reserva(self.aluno, livro_disponivel)


class LivrosPopularesServiceTest(TestCase):
    def setUp(self):
        self.aluno = _criar_aluno("aluno1", "001")
        self.livro = _criar_livro("Mais Emprestado", quantidade=5)
        for _ in range(3):
            emp = services.registrar_emprestimo(self.aluno, self.livro)
            services.devolver_emprestimo(emp)

    def test_livros_populares_retorna_livros_com_total(self):
        resultado = list(services.livros_mais_populares(meses=3))
        self.assertTrue(len(resultado) > 0)
        self.assertTrue(hasattr(resultado[0], "total_emprestimos"))

    def test_livros_recentes_retorna_por_data(self):
        resultado = list(services.livros_recentes(limite=10))
        self.assertGreater(len(resultado), 0)
