"""Testes das validações e campos calculados dos serializers (core/serializers.py)."""

from datetime import date, timedelta

from django.test import TestCase

from core.models import Emprestimo, Resenha
from core.serializers import (
    AlunoWriteSerializer,
    LivroDetailSerializer,
    LivroWriteSerializer,
    ResenhaWriteSerializer,
)
from core.tests.factories import make_aluno, make_livro, make_turma


class LivroWriteSerializerTest(TestCase):
    def setUp(self):
        self.autor_pk = make_livro("Base").autor_id
        self.genero_pk = make_livro("Base2").genero_id

    def _payload(self, **overrides):
        data = {
            "titulo": "Novo Livro",
            "autor": self.autor_pk,
            "genero": self.genero_pk,
            "quantidade": 3,
            "conteudo_explicito": False,
        }
        data.update(overrides)
        return data

    def test_quantidade_valida(self):
        serializer = LivroWriteSerializer(data=self._payload(quantidade=1))
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_quantidade_zero_rejeitada(self):
        serializer = LivroWriteSerializer(data=self._payload(quantidade=0))
        self.assertFalse(serializer.is_valid())
        self.assertIn("quantidade", serializer.errors)

    def test_quantidade_negativa_rejeitada(self):
        serializer = LivroWriteSerializer(data=self._payload(quantidade=-5))
        self.assertFalse(serializer.is_valid())
        self.assertIn("quantidade", serializer.errors)


class ResenhaWriteSerializerTest(TestCase):
    def test_nota_valida(self):
        serializer = ResenhaWriteSerializer(data={"nota": 3, "texto": "ok"})
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_nota_acima_de_cinco_rejeitada(self):
        serializer = ResenhaWriteSerializer(data={"nota": 6, "texto": ""})
        self.assertFalse(serializer.is_valid())
        self.assertIn("nota", serializer.errors)

    def test_nota_abaixo_de_um_rejeitada(self):
        serializer = ResenhaWriteSerializer(data={"nota": 0, "texto": ""})
        self.assertFalse(serializer.is_valid())
        self.assertIn("nota", serializer.errors)

    def test_texto_opcional(self):
        serializer = ResenhaWriteSerializer(data={"nota": 4})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["texto"], "")


class AlunoWriteSerializerTest(TestCase):
    def setUp(self):
        self.turma = make_turma(nome="9C")
        self.aluno = make_aluno("existente", matricula="555", turma=self.turma)

    def _payload(self, **overrides):
        data = {
            "username": "novo",
            "first_name": "Novo",
            "last_name": "Aluno",
            "email": "novo@example.com",
            "password": "Pass1234!",
            "matricula": "777",
            "turma_id": self.turma.pk,
        }
        data.update(overrides)
        return data

    def test_payload_valido(self):
        serializer = AlunoWriteSerializer(data=self._payload())
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_username_duplicado_rejeitado(self):
        serializer = AlunoWriteSerializer(data=self._payload(username="existente"))
        self.assertFalse(serializer.is_valid())
        self.assertIn("username", serializer.errors)

    def test_matricula_duplicada_rejeitada(self):
        serializer = AlunoWriteSerializer(data=self._payload(matricula="555"))
        self.assertFalse(serializer.is_valid())
        self.assertIn("matricula", serializer.errors)

    def test_senha_fraca_rejeitada(self):
        serializer = AlunoWriteSerializer(data=self._payload(password="123"))
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_senha_obrigatoria_no_create(self):
        serializer = AlunoWriteSerializer(data=self._payload(password=""))
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_senha_opcional_no_update(self):
        serializer = AlunoWriteSerializer(
            data=self._payload(username="existente", matricula="555", password=""),
            context={"aluno_pk": self.aluno.pk},
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_update_permite_manter_username_proprio(self):
        serializer = AlunoWriteSerializer(
            data=self._payload(username="existente", matricula="555"),
            context={"aluno_pk": self.aluno.pk},
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)


class LivroDetailSerializerTest(TestCase):
    def setUp(self):
        self.livro = make_livro("Com Resenhas", quantidade=1)
        self.aluno1 = make_aluno("rev1", matricula="a1")
        self.aluno2 = make_aluno("rev2", matricula="a2")

    def test_media_e_total_resenhas(self):
        Resenha.objects.create(aluno=self.aluno1, livro=self.livro, nota=4, texto="")
        Resenha.objects.create(aluno=self.aluno2, livro=self.livro, nota=2, texto="")
        data = LivroDetailSerializer(self.livro).data
        self.assertEqual(data["total_resenhas"], 2)
        self.assertEqual(data["media_notas"], 3.0)

    def test_media_nula_sem_resenhas(self):
        data = LivroDetailSerializer(self.livro).data
        self.assertIsNone(data["media_notas"])
        self.assertEqual(data["total_resenhas"], 0)

    def test_previsao_retorno_usa_emprestimo_aberto(self):
        prevista = date.today() + timedelta(days=10)
        Emprestimo.objects.create(
            aluno=self.aluno1,
            livro=self.livro,
            data_devolucao_prevista=prevista,
            status="ABERTO",
        )
        data = LivroDetailSerializer(self.livro).data
        self.assertEqual(data["previsao_retorno"], prevista)
