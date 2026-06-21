"""Testes de integração da API dos fluxos do aluno (status, renovação, reserva)."""

from datetime import date, timedelta

from rest_framework import status
from django.test import TestCase

from core.models import Emprestimo, Reserva
from core.tests.factories import auth_client, make_aluno, make_livro


class StatusAlunoTests(TestCase):
    def setUp(self):
        self.aluno = make_aluno("aluno", matricula="001")
        self.client = auth_client("aluno")

    def test_status_reflete_emprestimo_existente(self):
        livro = make_livro("Emprestado", quantidade=1)
        Emprestimo.objects.create(aluno=self.aluno, livro=livro)
        resp = self.client.get(f"/api/livros/{livro.pk}/status-aluno/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data["ja_tem_emprestimo"])
        self.assertFalse(resp.data["pode_reservar"])

    def test_status_reflete_reserva_existente(self):
        livro = make_livro("Esgotado", disponivel=False)
        Reserva.objects.create(aluno=self.aluno, livro=livro, status="ATIVA")
        resp = self.client.get(f"/api/livros/{livro.pk}/status-aluno/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data["ja_reservou"])
        self.assertFalse(resp.data["pode_reservar"])


class RenovarEmprestimoApiTests(TestCase):
    def setUp(self):
        self.aluno = make_aluno("aluno", matricula="001")
        self.client = auth_client("aluno")
        self.livro = make_livro("Livro", quantidade=2)
        self.emprestimo = Emprestimo.objects.create(aluno=self.aluno, livro=self.livro)

    def test_dono_renova_mais_sete_dias(self):
        resp = self.client.post(f"/api/emprestimos/{self.emprestimo.pk}/renovar/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.emprestimo.refresh_from_db()
        self.assertEqual(
            self.emprestimo.data_devolucao_prevista,
            date.today() + timedelta(days=7),
        )

    def test_nao_dono_recebe_403(self):
        make_aluno("intruso", matricula="002")
        outro_client = auth_client("intruso")
        resp = outro_client.post(f"/api/emprestimos/{self.emprestimo.pk}/renovar/")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_renovar_devolvido_falha(self):
        self.emprestimo.status = "DEVOLVIDO"
        self.emprestimo.save()
        resp = self.client.post(f"/api/emprestimos/{self.emprestimo.pk}/renovar/")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


class CancelarMinhaReservaApiTests(TestCase):
    def setUp(self):
        self.aluno = make_aluno("aluno", matricula="001")
        self.client = auth_client("aluno")
        self.livro = make_livro("Esgotado", disponivel=False)
        self.reserva = Reserva.objects.create(
            aluno=self.aluno, livro=self.livro, status="ATIVA"
        )

    def test_cancela_reserva_ativa(self):
        resp = self.client.post(f"/api/minhas-reservas/{self.reserva.pk}/cancelar/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.reserva.refresh_from_db()
        self.assertEqual(self.reserva.status, "CANCELADA")

    def test_cancelar_reserva_nao_ativa_falha(self):
        self.reserva.status = "ATENDIDA"
        self.reserva.save()
        resp = self.client.post(f"/api/minhas-reservas/{self.reserva.pk}/cancelar/")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_nao_cancela_reserva_de_outro_aluno(self):
        make_aluno("outro", matricula="002")
        outro_client = auth_client("outro")
        resp = outro_client.post(f"/api/minhas-reservas/{self.reserva.pk}/cancelar/")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_reservar_via_api_cria_reserva(self):
        novo_livro = make_livro("Outro Esgotado", disponivel=False)
        resp = self.client.post(f"/api/livros/{novo_livro.pk}/reservar/")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Reserva.objects.filter(aluno=self.aluno, livro=novo_livro, status="ATIVA").exists()
        )
