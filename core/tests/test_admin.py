from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from core.models import Aluno, Autor, Emprestimo, Livro, Reserva
from core import services


def _criar_livro(titulo, quantidade=2):
    autor, _ = Autor.objects.get_or_create(nome="Autor Padrão")
    return Livro.objects.create(titulo=titulo, autor=autor, quantidade=quantidade)


class EmprestimoAdminActionTest(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username="staff", password="pass", is_staff=True, is_superuser=True
        )
        self.client.login(username="staff", password="pass")

        user = User.objects.create_user(username="aluno1", password="pass")
        self.aluno = Aluno.objects.create(usuario=user, matricula="001")
        self.livro = _criar_livro("Livro Admin", quantidade=2)
        self.emprestimo = services.registrar_emprestimo(self.aluno, self.livro)

    def test_marcar_como_devolvido_atualiza_status(self):
        url = reverse("admin:core_emprestimo_changelist")
        resp = self.client.post(url, {
            "action": "marcar_como_devolvido",
            "_selected_action": [str(self.emprestimo.pk)],
        })
        self.assertIn(resp.status_code, [200, 302])
        self.emprestimo.refresh_from_db()
        self.assertEqual(self.emprestimo.status, "DEVOLVIDO")


class ReservaAdminActionTest(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username="staff", password="pass", is_staff=True, is_superuser=True
        )
        self.client.login(username="staff", password="pass")

        user = User.objects.create_user(username="aluno1", password="pass")
        self.aluno = Aluno.objects.create(usuario=user, matricula="001")
        self.livro = _criar_livro("Livro Reserva", quantidade=0)
        self.reserva = Reserva.objects.create(aluno=self.aluno, livro=self.livro, status="ATIVA")

    def test_cancelar_reservas_atualiza_status(self):
        url = reverse("admin:core_reserva_changelist")
        resp = self.client.post(url, {
            "action": "cancelar_reservas",
            "_selected_action": [str(self.reserva.pk)],
        })
        self.assertIn(resp.status_code, [200, 302])
        self.reserva.refresh_from_db()
        self.assertEqual(self.reserva.status, "CANCELADA")
