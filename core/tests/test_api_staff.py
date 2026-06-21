"""Testes de integração da API staff — CRUD de cadastros, operações e relatórios."""

from datetime import date, timedelta

from django.contrib.auth.models import User
from rest_framework import status
from django.test import TestCase

from core.models import Aluno, Emprestimo, Genero, Reserva, Resenha, Turma
from core.tests.factories import (
    auth_client,
    make_aluno,
    make_genero,
    make_livro,
    make_staff,
    make_turma,
)


class StaffAlunoCrudTests(TestCase):
    def setUp(self):
        make_staff("staff")
        self.client = auth_client("staff")
        self.turma = make_turma(nome="3A")
        self.aluno = make_aluno("joao", matricula="100", turma=self.turma)

    def test_update_aluno(self):
        resp = self.client.put(
            f"/api/staff/alunos/{self.aluno.pk}/",
            {
                "username": "joao",
                "first_name": "João",
                "last_name": "Silva",
                "email": "joao@example.com",
                "matricula": "100",
                "turma_id": self.turma.pk,
            },
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.aluno.usuario.refresh_from_db()
        self.assertEqual(self.aluno.usuario.first_name, "João")

    def test_partial_update_aluno(self):
        resp = self.client.patch(
            f"/api/staff/alunos/{self.aluno.pk}/",
            {"matricula": "200"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.aluno.refresh_from_db()
        self.assertEqual(self.aluno.matricula, "200")

    def test_delete_aluno_remove_user_em_cascata(self):
        user_id = self.aluno.usuario_id
        resp = self.client.delete(f"/api/staff/alunos/{self.aluno.pk}/")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Aluno.objects.filter(pk=self.aluno.pk).exists())
        self.assertFalse(User.objects.filter(pk=user_id).exists())

    def test_update_matricula_duplicada_falha(self):
        make_aluno("maria", matricula="999", turma=self.turma)
        resp = self.client.patch(
            f"/api/staff/alunos/{self.aluno.pk}/",
            {"matricula": "999"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


class StaffGeneroTurmaCrudTests(TestCase):
    def setUp(self):
        make_staff("staff")
        self.client = auth_client("staff")

    def test_crud_generos(self):
        resp = self.client.post("/api/staff/generos/", {"nome": "Suspense"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        pk = resp.data["id"]

        resp = self.client.put(f"/api/staff/generos/{pk}/", {"nome": "Thriller"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(Genero.objects.get(pk=pk).nome, "Thriller")

        resp = self.client.delete(f"/api/staff/generos/{pk}/")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_crud_turmas(self):
        resp = self.client.post(
            "/api/staff/turmas/",
            {"nome": "8B", "exibe_conteudo_explicito": True},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        pk = resp.data["id"]
        self.assertTrue(resp.data["exibe_conteudo_explicito"])

        resp = self.client.patch(
            f"/api/staff/turmas/{pk}/",
            {"exibe_conteudo_explicito": False},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertFalse(Turma.objects.get(pk=pk).exibe_conteudo_explicito)

        resp = self.client.delete(f"/api/staff/turmas/{pk}/")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)


class StaffEmprestimoTests(TestCase):
    def setUp(self):
        make_staff("staff")
        self.client = auth_client("staff")
        self.turma = make_turma(nome="5A")
        self.aluno = make_aluno("aluno", matricula="001", turma=self.turma)
        self.livro = make_livro("Livro", quantidade=2)

    def test_list_emprestimos(self):
        Emprestimo.objects.create(aluno=self.aluno, livro=self.livro)
        resp = self.client.get("/api/staff/emprestimos/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)

    def test_registrar_emprestimo_bloqueia_aluno_com_pendencia(self):
        # cria empréstimo vencido => pendência
        Emprestimo.objects.create(
            aluno=self.aluno,
            livro=self.livro,
            data_devolucao_prevista=date.today() - timedelta(days=1),
        )
        outro_livro = make_livro("Outro", quantidade=1)
        resp = self.client.post(
            "/api/staff/emprestimos/",
            {"livro_id": outro_livro.pk, "aluno_id": self.aluno.pk},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_devolver_emprestimo_ja_devolvido_falha(self):
        emp = Emprestimo.objects.create(aluno=self.aluno, livro=self.livro)
        emp.status = "DEVOLVIDO"
        emp.save()
        resp = self.client.post(f"/api/staff/emprestimos/{emp.pk}/devolver/")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registrar_emprestimo_sem_ids_falha(self):
        resp = self.client.post("/api/staff/emprestimos/", {}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


class StaffReservaTests(TestCase):
    def setUp(self):
        make_staff("staff")
        self.client = auth_client("staff")
        self.aluno = make_aluno("aluno", matricula="001")
        self.livro = make_livro("Esgotado", disponivel=False)
        self.reserva = Reserva.objects.create(aluno=self.aluno, livro=self.livro, status="ATIVA")

    def test_list_reservas(self):
        resp = self.client.get("/api/staff/reservas/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)

    def test_cancelar_reserva_ativa(self):
        resp = self.client.post(f"/api/staff/reservas/{self.reserva.pk}/cancelar/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.reserva.refresh_from_db()
        self.assertEqual(self.reserva.status, "CANCELADA")

    def test_cancelar_reserva_nao_ativa_falha(self):
        self.reserva.status = "CANCELADA"
        self.reserva.save()
        resp = self.client.post(f"/api/staff/reservas/{self.reserva.pk}/cancelar/")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


class StaffResenhaTests(TestCase):
    def setUp(self):
        make_staff("staff")
        self.client = auth_client("staff")
        self.aluno = make_aluno("aluno", matricula="001")
        self.livro = make_livro("Livro com resenha")
        self.resenha = Resenha.objects.create(
            aluno=self.aluno, livro=self.livro, nota=5, texto="Excelente"
        )

    def test_list_resenhas_inclui_livro(self):
        resp = self.client.get("/api/staff/resenhas/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)
        self.assertIn("livro", resp.data[0])
        self.assertEqual(resp.data[0]["livro"]["titulo"], "Livro com resenha")

    def test_busca_resenhas_por_titulo(self):
        resp = self.client.get("/api/staff/resenhas/", {"q": "resenha"})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)

    def test_delete_resenha(self):
        resp = self.client.delete(f"/api/staff/resenhas/{self.resenha.pk}/")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Resenha.objects.filter(pk=self.resenha.pk).exists())


class RelatoriosTests(TestCase):
    def setUp(self):
        make_staff("staff")
        self.client = auth_client("staff")
        self.aluno = make_aluno("aluno", matricula="001")
        self.livro = make_livro("Livro", quantidade=3)

    def test_relatorio_devolucoes_requer_datas(self):
        resp = self.client.get("/api/relatorios/devolucoes/")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_relatorio_devolucoes_lista(self):
        emp = Emprestimo.objects.create(aluno=self.aluno, livro=self.livro)
        emp.status = "DEVOLVIDO"
        emp.save()
        resp = self.client.get(
            "/api/relatorios/devolucoes/",
            {"data_inicio": "2020-01-01", "data_fim": "2999-12-31"},
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIsInstance(resp.data, list)
        self.assertEqual(len(resp.data), 1)

    def test_relatorio_devolucoes_export_csv(self):
        emp = Emprestimo.objects.create(aluno=self.aluno, livro=self.livro)
        emp.status = "DEVOLVIDO"
        emp.save()
        resp = self.client.get(
            "/api/relatorios/devolucoes/",
            {"data_inicio": "2020-01-01", "data_fim": "2999-12-31", "exportar": "csv"},
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("text/csv", resp["Content-Type"])
        self.assertIn("attachment", resp["Content-Disposition"])

    def test_relatorio_emprestimos_data_fim_anterior_falha(self):
        resp = self.client.get(
            "/api/relatorios/emprestimos/",
            {"data_inicio": "2024-12-31", "data_fim": "2024-01-01"},
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_relatorio_emprestimos_data_invalida_falha(self):
        resp = self.client.get(
            "/api/relatorios/emprestimos/",
            {"data_inicio": "data-ruim", "data_fim": "2024-01-01"},
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_relatorio_emprestimos_export_csv(self):
        Emprestimo.objects.create(aluno=self.aluno, livro=self.livro)
        resp = self.client.get(
            "/api/relatorios/emprestimos/",
            {"data_inicio": "2020-01-01", "data_fim": "2999-12-31", "exportar": "csv"},
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("text/csv", resp["Content-Type"])

    def test_relatorio_requer_staff(self):
        make_aluno("alunonaostaff", matricula="888")
        client = auth_client("alunonaostaff")
        resp = client.get(
            "/api/relatorios/emprestimos/",
            {"data_inicio": "2020-01-01", "data_fim": "2999-12-31"},
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
