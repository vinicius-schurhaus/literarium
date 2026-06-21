import shutil
import tempfile
from datetime import date, timedelta
from io import BytesIO

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings
from django.utils import timezone
from PIL import Image

from core.models import Aluno, Autor, Emprestimo, Genero, Livro, Reserva, Resenha, Turma


class GeneroModelTest(TestCase):
    def test_str_retorna_nome(self):
        genero = Genero(nome="Ficção Científica")
        self.assertEqual(str(genero), "Ficção Científica")

    def test_nome_duplicado_levanta_erro(self):
        Genero.objects.create(nome="Terror")
        with self.assertRaises(Exception):
            Genero.objects.create(nome="Terror")


class AutorModelTest(TestCase):
    def test_str_retorna_nome(self):
        autor = Autor(nome="Clarice Lispector")
        self.assertEqual(str(autor), "Clarice Lispector")

    def test_nome_duplicado_levanta_erro(self):
        Autor.objects.create(nome="Machado de Assis")
        with self.assertRaises(Exception):
            Autor.objects.create(nome="Machado de Assis")


class LivroModelTest(TestCase):
    def setUp(self):
        self.autor = Autor.objects.create(nome="Jorge Amado")
        self.genero = Genero.objects.create(nome="Romance")

    def _livro(self, quantidade=2):
        return Livro(titulo="Gabriela", autor=self.autor, genero=self.genero, quantidade=quantidade)

    def test_str_retorna_titulo(self):
        self.assertEqual(str(self._livro()), "Gabriela")

    def test_disponivel_quando_quantidade_maior_que_zero(self):
        self.assertTrue(self._livro(2).disponivel)

    def test_indisponivel_quando_quantidade_zero(self):
        livro = self._livro(0)
        livro.quantidade = 0
        self.assertFalse(livro.disponivel)

    def test_clean_levanta_erro_quantidade_negativa(self):
        livro = self._livro(1)
        livro.quantidade = -1
        with self.assertRaises(ValidationError):
            livro.clean()

    def test_clean_aceita_quantidade_zero(self):
        # No nível do model 0 é permitido; a regra "≥1" é aplicada pelo
        # LivroWriteSerializer (ver test_serializers.py).
        livro = self._livro(1)
        livro.quantidade = 0
        livro.clean()  # não deve lançar

    def test_clean_aceita_quantidade_positiva(self):
        livro = self._livro(1)
        livro.clean()  # não deve lançar

    def test_sinopse_padrao_e_string_vazia(self):
        livro = Livro.objects.create(titulo="Teste", autor=self.autor, quantidade=1)
        self.assertEqual(livro.sinopse, "")

    def test_previsao_retorno_none_sem_emprestimos(self):
        livro = Livro.objects.create(titulo="Dom Casmurro", autor=self.autor, quantidade=1)
        self.assertIsNone(livro.previsao_retorno())


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class LivroCapaTest(TestCase):
    @classmethod
    def tearDownClass(cls):
        from django.conf import settings
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.autor = Autor.objects.create(nome="Autor Capa")

    def _upload(self, largura, altura, formato="PNG"):
        buffer = BytesIO()
        Image.new("RGB", (largura, altura), "navy").save(buffer, format=formato)
        return SimpleUploadedFile(
            f"capa.{formato.lower()}", buffer.getvalue(), content_type=f"image/{formato.lower()}"
        )

    def test_capa_e_redimensionada_e_convertida_para_jpg(self):
        livro = Livro.objects.create(
            titulo="Com Capa", autor=self.autor, quantidade=1,
            capa=self._upload(2000, 3000),
        )
        livro.refresh_from_db()
        self.assertTrue(livro.capa.name.endswith(".jpg"))
        with Image.open(livro.capa) as img:
            self.assertEqual(img.format, "JPEG")
            self.assertLessEqual(img.width, Livro.CAPA_TAMANHO_MAXIMO[0])
            self.assertLessEqual(img.height, Livro.CAPA_TAMANHO_MAXIMO[1])

    def test_capa_menor_que_o_limite_preserva_proporcao(self):
        livro = Livro.objects.create(
            titulo="Capa Pequena", autor=self.autor, quantidade=1,
            capa=self._upload(400, 600),
        )
        with Image.open(livro.capa) as img:
            self.assertEqual((img.width, img.height), (400, 600))

    def test_save_sem_trocar_capa_nao_reprocessa(self):
        livro = Livro.objects.create(
            titulo="Estável", autor=self.autor, quantidade=1,
            capa=self._upload(1500, 2000),
        )
        nome_apos_criar = livro.capa.name
        livro.titulo = "Estável (editado)"
        livro.save()
        livro.refresh_from_db()
        self.assertEqual(livro.capa.name, nome_apos_criar)


class AlunoModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="aluno1", password="pass", first_name="João")
        self.aluno = Aluno.objects.create(usuario=self.user, matricula="2024001")
        self.autor = Autor.objects.create(nome="Autor Teste")
        self.livro = Livro.objects.create(titulo="Livro Teste", autor=self.autor, quantidade=3)

    def test_str_retorna_first_name(self):
        self.assertIn("João", str(self.aluno))
        self.assertIn("2024001", str(self.aluno))

    def test_str_retorna_username_quando_sem_first_name(self):
        user2 = User.objects.create_user(username="aluno2", password="pass")
        aluno2 = Aluno.objects.create(usuario=user2, matricula="2024002")
        self.assertIn("aluno2", str(aluno2))

    def test_sem_pendencia_quando_sem_emprestimos(self):
        self.assertFalse(self.aluno.tem_pendencia)

    def test_sem_pendencia_com_emprestimo_em_dia(self):
        Emprestimo.objects.create(
            aluno=self.aluno,
            livro=self.livro,
            data_devolucao_prevista=date.today() + timedelta(days=7),
        )
        self.assertFalse(self.aluno.tem_pendencia)

    def test_com_pendencia_quando_emprestimo_atrasado(self):
        emprestimo = Emprestimo(
            aluno=self.aluno,
            livro=self.livro,
            data_devolucao_prevista=date.today() - timedelta(days=1),
        )
        emprestimo.save()
        self.assertTrue(self.aluno.tem_pendencia)


class EmprestimoModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="aluno1", password="pass")
        self.aluno = Aluno.objects.create(usuario=self.user, matricula="2024001", turma=None)
        self.autor = Autor.objects.create(nome="Autor")
        self.livro = Livro.objects.create(titulo="Livro", autor=self.autor, quantidade=2)

    def test_str_retorna_titulo_e_aluno(self):
        emp = Emprestimo(livro=self.livro, aluno=self.aluno)
        self.assertIn("Livro", str(emp))

    def test_save_decrementa_quantidade_ao_criar(self):
        Emprestimo.objects.create(aluno=self.aluno, livro=self.livro)
        self.livro.refresh_from_db()
        self.assertEqual(self.livro.quantidade, 1)

    def test_save_incrementa_quantidade_ao_devolver(self):
        emp = Emprestimo.objects.create(aluno=self.aluno, livro=self.livro)
        emp.status = "DEVOLVIDO"
        emp.save()
        self.livro.refresh_from_db()
        self.assertEqual(self.livro.quantidade, 2)

    def test_save_define_data_devolucao_prevista_automaticamente(self):
        emp = Emprestimo.objects.create(aluno=self.aluno, livro=self.livro)
        esperado = timezone.now().date() + timedelta(days=7)
        self.assertEqual(emp.data_devolucao_prevista, esperado)

    def test_save_levanta_erro_quando_sem_estoque(self):
        self.livro.quantidade = 0
        self.livro.save()
        with self.assertRaises((ValidationError, Exception)):
            Emprestimo.objects.create(aluno=self.aluno, livro=self.livro)

    def test_delete_restaura_quantidade_se_aberto(self):
        emp = Emprestimo.objects.create(aluno=self.aluno, livro=self.livro)
        self.livro.refresh_from_db()
        qtd_antes = self.livro.quantidade
        emp.delete()
        self.livro.refresh_from_db()
        self.assertEqual(self.livro.quantidade, qtd_antes + 1)

    def test_delete_nao_restaura_quantidade_se_devolvido(self):
        emp = Emprestimo.objects.create(aluno=self.aluno, livro=self.livro)
        emp.status = "DEVOLVIDO"
        emp.save()
        self.livro.refresh_from_db()
        qtd_antes = self.livro.quantidade
        emp.delete()
        self.livro.refresh_from_db()
        self.assertEqual(self.livro.quantidade, qtd_antes)

    def test_esta_atrasado_quando_em_aberto_e_vencido(self):
        emp = Emprestimo(
            aluno=self.aluno,
            livro=self.livro,
            data_devolucao_prevista=date.today() - timedelta(days=1),
        )
        emp.save()
        self.assertTrue(emp.esta_atrasado)

    def test_nao_esta_atrasado_quando_devolvido(self):
        emp = Emprestimo.objects.create(aluno=self.aluno, livro=self.livro)
        emp.status = "DEVOLVIDO"
        emp.save()
        self.assertFalse(emp.esta_atrasado)

    def test_manager_abertos_filtra_corretamente(self):
        emp1 = Emprestimo.objects.create(aluno=self.aluno, livro=self.livro)
        user2 = User.objects.create_user(username="aluno2", password="pass")
        aluno2 = Aluno.objects.create(usuario=user2, matricula="2024002", turma=None)
        livro2 = Livro.objects.create(titulo="Livro2", autor=self.autor, quantidade=2)
        emp2 = Emprestimo.objects.create(aluno=aluno2, livro=livro2)
        emp2.status = "DEVOLVIDO"
        emp2.save()
        abertos = Emprestimo.objects.abertos()
        self.assertIn(emp1, abertos)
        self.assertNotIn(emp2, abertos)

    def test_manager_no_periodo_filtra_corretamente(self):
        emp = Emprestimo.objects.create(aluno=self.aluno, livro=self.livro)
        inicio = date.today()
        fim = date.today()
        resultado = Emprestimo.objects.no_periodo(inicio, fim)
        self.assertIn(emp, resultado)

    def test_clean_levanta_erro_data_devolucao_real_anterior_a_emprestimo(self):
        emp = Emprestimo(
            aluno=self.aluno,
            livro=self.livro,
            data_devolucao_real=date.today() - timedelta(days=10),
        )
        emp.data_emprestimo = date.today()
        with self.assertRaises(ValidationError):
            emp.clean()


class ReservaModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="aluno1", password="pass")
        self.aluno = Aluno.objects.create(usuario=self.user, matricula="2024001", turma=None)
        self.autor = Autor.objects.create(nome="Autor")
        self.livro = Livro.objects.create(titulo="Livro", autor=self.autor, quantidade=0)

    def test_str_retorna_reserva_titulo_e_aluno(self):
        reserva = Reserva(livro=self.livro, aluno=self.aluno)
        self.assertIn("Reserva:", str(reserva))

    def test_manager_ativas_filtra_por_status(self):
        r1 = Reserva.objects.create(aluno=self.aluno, livro=self.livro, status="ATIVA")
        r2 = Reserva.objects.create(aluno=self.aluno, livro=self.livro, status="CANCELADA")
        # Precisa contornar unique constraint
        r2.status = "CANCELADA"
        r2.save()
        ativas = Reserva.objects.ativas()
        self.assertIn(r1, ativas)


class UniqueConstraintsTest(TestCase):
    """Cobre as UniqueConstraints declaradas nos models."""

    def setUp(self):
        self.autor = Autor.objects.create(nome="Autor Único")
        self.user = User.objects.create_user(username="aluno1", password="pass")
        self.aluno = Aluno.objects.create(usuario=self.user, matricula="m1", turma=None)
        self.livro = Livro.objects.create(titulo="Indisponível", autor=self.autor, quantidade=0)

    def test_livro_titulo_autor_unico(self):
        Livro.objects.create(titulo="Mesmo Título", autor=self.autor, quantidade=1)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Livro.objects.create(titulo="Mesmo Título", autor=self.autor, quantidade=1)

    def test_livro_titulo_repetido_com_outro_autor_permitido(self):
        outro = Autor.objects.create(nome="Outro Autor")
        Livro.objects.create(titulo="Mesmo Título", autor=self.autor, quantidade=1)
        Livro.objects.create(titulo="Mesmo Título", autor=outro, quantidade=1)
        self.assertEqual(Livro.objects.filter(titulo="Mesmo Título").count(), 2)

    def test_reserva_ativa_unica_por_aluno_livro(self):
        Reserva.objects.create(aluno=self.aluno, livro=self.livro, status="ATIVA")
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Reserva.objects.create(aluno=self.aluno, livro=self.livro, status="ATIVA")

    def test_reserva_cancelada_nao_conflita_com_ativa(self):
        Reserva.objects.create(aluno=self.aluno, livro=self.livro, status="CANCELADA")
        Reserva.objects.create(aluno=self.aluno, livro=self.livro, status="ATIVA")
        self.assertEqual(Reserva.objects.filter(aluno=self.aluno, livro=self.livro).count(), 2)

    def test_resenha_unica_por_aluno_livro(self):
        Resenha.objects.create(aluno=self.aluno, livro=self.livro, nota=4)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Resenha.objects.create(aluno=self.aluno, livro=self.livro, nota=2)


class EmprestimoSaveEdgeCasesTest(TestCase):
    """Casos de borda do Emprestimo.save() (troca de livro, reabertura)."""

    def setUp(self):
        self.user = User.objects.create_user(username="aluno1", password="pass")
        self.aluno = Aluno.objects.create(usuario=self.user, matricula="m1", turma=None)
        self.autor = Autor.objects.create(nome="Autor")
        self.livro_a = Livro.objects.create(titulo="Livro A", autor=self.autor, quantidade=2)
        self.livro_b = Livro.objects.create(titulo="Livro B", autor=self.autor, quantidade=2)

    def test_troca_de_livro_restaura_antigo_e_decrementa_novo(self):
        emp = Emprestimo.objects.create(aluno=self.aluno, livro=self.livro_a)
        self.livro_a.refresh_from_db()
        self.assertEqual(self.livro_a.quantidade, 1)  # decrementou ao criar

        emp.livro = self.livro_b
        emp.save()

        self.livro_a.refresh_from_db()
        self.livro_b.refresh_from_db()
        self.assertEqual(self.livro_a.quantidade, 2)  # restaurado
        self.assertEqual(self.livro_b.quantidade, 1)  # decrementado

    def test_reabertura_decrementa_estoque_novamente(self):
        emp = Emprestimo.objects.create(aluno=self.aluno, livro=self.livro_a)
        emp.status = "DEVOLVIDO"
        emp.save()
        self.livro_a.refresh_from_db()
        self.assertEqual(self.livro_a.quantidade, 2)  # devolveu

        emp.status = "ABERTO"
        emp.save()
        self.livro_a.refresh_from_db()
        self.assertEqual(self.livro_a.quantidade, 1)  # decrementou de novo

    def test_reabertura_sem_estoque_levanta_erro(self):
        emp = Emprestimo.objects.create(aluno=self.aluno, livro=self.livro_a)
        emp.status = "DEVOLVIDO"
        emp.save()
        # zera estoque antes de reabrir
        Livro.objects.filter(pk=self.livro_a.pk).update(quantidade=0)
        emp.status = "ABERTO"
        with self.assertRaises(ValidationError):
            emp.save()

    def test_previsao_retorno_retorna_data_mais_proxima(self):
        outro_user = User.objects.create_user(username="aluno2", password="pass")
        outro_aluno = Aluno.objects.create(usuario=outro_user, matricula="m2", turma=None)
        Emprestimo.objects.create(
            aluno=self.aluno,
            livro=self.livro_a,
            data_devolucao_prevista=date.today() + timedelta(days=10),
        )
        Emprestimo.objects.create(
            aluno=outro_aluno,
            livro=self.livro_a,
            data_devolucao_prevista=date.today() + timedelta(days=3),
        )
        self.assertEqual(self.livro_a.previsao_retorno(), date.today() + timedelta(days=3))
