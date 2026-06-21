"""
API integration tests — verifica conformidade entre frontend e backend.

Cada test class cobre um grupo de endpoints da API REST, garantindo que:
  - Respostas têm o formato esperado pelo frontend
  - Permissões estão corretas (público, aluno, staff)
  - Regras de negócio são aplicadas
"""

from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Aluno, Autor, Emprestimo, Genero, Livro, Reserva, Resenha, Turma


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_user(username="user", password="Pass1234!", staff=False):
    return User.objects.create_user(
        username=username,
        password=password,
        first_name="Test",
        last_name="User",
        is_staff=staff,
    )


def make_aluno(username="aluno", password="Pass1234!"):
    user = make_user(username=username, password=password)
    turma = Turma.objects.create(nome="1A")
    return Aluno.objects.create(usuario=user, matricula="001", turma=turma)


def make_livro(titulo="Dom Casmurro", disponivel=True):
    autor = Autor.objects.get_or_create(nome="Machado de Assis")[0]
    genero = Genero.objects.get_or_create(nome="Romance")[0]
    quantidade = 2 if disponivel else 0
    return Livro.objects.create(
        titulo=titulo,
        autor=autor,
        genero=genero,
        quantidade=quantidade,
    )


def jwt_for(client, username, password="Pass1234!"):
    resp = client.post(
        "/api/auth/token/",
        {"username": username, "password": password},
        format="json",
    )
    return resp.data["access"]


def auth_client(username, password="Pass1234!"):
    client = APIClient()
    token = jwt_for(client, username, password)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

class AuthTests(TestCase):
    def setUp(self):
        self.user = make_user("authuser")
        self.client = APIClient()

    def test_login_returns_tokens(self):
        resp = self.client.post(
            "/api/auth/token/",
            {"username": "authuser", "password": "Pass1234!"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("access", resp.data)
        self.assertIn("refresh", resp.data)

    def test_login_invalid_credentials(self):
        resp = self.client.post(
            "/api/auth/token/",
            {"username": "authuser", "password": "wrongpassword"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_returns_user_profile(self):
        client = auth_client("authuser")
        resp = client.get("/api/auth/me/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["username"], "authuser")
        self.assertIn("is_staff", resp.data)
        self.assertIn("has_aluno_perfil", resp.data)

    def test_me_requires_auth(self):
        resp = self.client.get("/api/auth/me/")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh(self):
        resp = self.client.post(
            "/api/auth/token/",
            {"username": "authuser", "password": "Pass1234!"},
            format="json",
        )
        refresh = resp.data["refresh"]
        resp2 = self.client.post(
            "/api/auth/token/refresh/",
            {"refresh": refresh},
            format="json",
        )
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)
        self.assertIn("access", resp2.data)

    def test_change_password(self):
        client = auth_client("authuser")
        resp = client.post(
            "/api/auth/change-password/",
            {
                "old_password": "Pass1234!",
                "new_password1": "NewPass5678!",
                "new_password2": "NewPass5678!",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # Old token still works until it expires; just check password changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewPass5678!"))

    def test_change_password_wrong_old(self):
        client = auth_client("authuser")
        resp = client.post(
            "/api/auth/change-password/",
            {
                "old_password": "wrongold",
                "new_password1": "NewPass5678!",
                "new_password2": "NewPass5678!",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


# ---------------------------------------------------------------------------
# Catálogo (livros)
# ---------------------------------------------------------------------------

class CatalogoTests(TestCase):
    def setUp(self):
        self.user = make_user("catalogouser")
        self.client = auth_client("catalogouser")
        self.livro = make_livro("Capitães da Areia")
        self.livro2 = make_livro("O Guarani")

    def test_list_livros_paginated(self):
        resp = self.client.get("/api/livros/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("results", resp.data)
        self.assertIn("count", resp.data)
        self.assertEqual(resp.data["count"], 2)

    def test_livro_detail(self):
        resp = self.client.get(f"/api/livros/{self.livro.pk}/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["titulo"], "Capitães da Areia")
        # detail fields
        self.assertIn("sinopse", resp.data)
        self.assertIn("quantidade", resp.data)

    def test_livro_capa_is_relative_url(self):
        resp = self.client.get(f"/api/livros/{self.livro.pk}/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        capa = resp.data.get("capa")
        if capa:
            self.assertFalse(capa.startswith("http"), "capa URL deve ser relativa")

    def test_search_by_titulo(self):
        resp = self.client.get("/api/livros/?q=Capitães")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["count"], 1)
        self.assertEqual(resp.data["results"][0]["titulo"], "Capitães da Areia")

    def test_filter_by_genero(self):
        genero = Genero.objects.get(nome="Romance")
        resp = self.client.get(f"/api/livros/?genero={genero.pk}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["count"], 2)

    def test_livros_populares(self):
        resp = self.client.get("/api/livros/populares/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIsInstance(resp.data, list)

    def test_home_endpoint(self):
        resp = self.client.get("/api/home/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("livros_recentes", resp.data)
        self.assertIn("livros_populares", resp.data)

    def test_generos_list(self):
        resp = self.client.get("/api/generos/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIsInstance(resp.data, list)

    def test_unauthenticated_denied(self):
        resp = APIClient().get("/api/livros/")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


# ---------------------------------------------------------------------------
# Resenhas
# ---------------------------------------------------------------------------

class ResenhaTests(TestCase):
    def setUp(self):
        self.aluno = make_aluno("alunorev")
        self.livro = make_livro()
        self.client = auth_client("alunorev")

    def test_get_resenhas_empty(self):
        resp = self.client.get(f"/api/livros/{self.livro.pk}/resenhas/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, [])

    def test_create_resenha(self):
        resp = self.client.post(
            f"/api/livros/{self.livro.pk}/resenha/",
            {"nota": 4, "texto": "Ótimo livro!"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["nota"], 4)
        self.assertTrue(resp.data["is_minha"])

    def test_update_resenha_upsert(self):
        self.client.post(
            f"/api/livros/{self.livro.pk}/resenha/",
            {"nota": 3, "texto": "Bom"},
            format="json",
        )
        resp = self.client.post(
            f"/api/livros/{self.livro.pk}/resenha/",
            {"nota": 5, "texto": "Excelente!"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["nota"], 5)

    def test_resenha_visible_in_list(self):
        Resenha.objects.create(aluno=self.aluno, livro=self.livro, nota=5, texto="Top")
        resp = self.client.get(f"/api/livros/{self.livro.pk}/resenhas/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)
        self.assertIn("aluno_nome", resp.data[0])
        self.assertIn("is_minha", resp.data[0])

    def test_non_aluno_cannot_post_resenha(self):
        user = make_user("staffonly", staff=True)
        client = auth_client("staffonly")
        resp = client.post(
            f"/api/livros/{self.livro.pk}/resenha/",
            {"nota": 5, "texto": "Test"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)


# ---------------------------------------------------------------------------
# Empréstimos e reservas (aluno)
# ---------------------------------------------------------------------------

class EmprestimoAlunoTests(TestCase):
    def setUp(self):
        self.aluno = make_aluno("alunolib")
        self.livro_disp = make_livro("Livro Disponível", disponivel=True)
        self.livro_indisp = make_livro("Livro Indisponível", disponivel=False)
        self.client = auth_client("alunolib")

    def test_status_aluno_disponivel(self):
        resp = self.client.get(f"/api/livros/{self.livro_disp.pk}/status-aluno/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertFalse(resp.data["ja_tem_emprestimo"])
        self.assertFalse(resp.data["ja_reservou"])
        self.assertFalse(resp.data["pode_reservar"])  # disponível não precisa de reserva

    def test_status_aluno_indisponivel(self):
        resp = self.client.get(f"/api/livros/{self.livro_indisp.pk}/status-aluno/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data["pode_reservar"])

    def test_reservar_livro_indisponivel(self):
        resp = self.client.post(f"/api/livros/{self.livro_indisp.pk}/reservar/")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Reserva.objects.filter(aluno=self.aluno).count(), 1)

    def test_reservar_duas_vezes_falha(self):
        self.client.post(f"/api/livros/{self.livro_indisp.pk}/reservar/")
        resp = self.client.post(f"/api/livros/{self.livro_indisp.pk}/reservar/")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_meus_emprestimos_empty(self):
        resp = self.client.get("/api/meus-emprestimos/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["emprestimos"], [])
        self.assertEqual(resp.data["reservas"], [])

    def test_non_aluno_cannot_access_meus_emprestimos(self):
        staff = make_user("staffuser2", staff=True)
        client = auth_client("staffuser2")
        resp = client.get("/api/meus-emprestimos/")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)


# ---------------------------------------------------------------------------
# Staff — CRUD e operações
# ---------------------------------------------------------------------------

class StaffTests(TestCase):
    def setUp(self):
        self.staff = make_user("staff1", staff=True)
        self.client = auth_client("staff1")
        self.livro = make_livro()
        turma = Turma.objects.create(nome="2B")
        aluno_user = make_user("aluno2")
        self.aluno = Aluno.objects.create(usuario=aluno_user, matricula="002", turma=turma)

    def test_staff_list_livros(self):
        resp = self.client.get("/api/staff/livros/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_staff_create_livro(self):
        autor = Autor.objects.get_or_create(nome="Clarice Lispector")[0]
        genero = Genero.objects.get_or_create(nome="Ficção")[0]
        resp = self.client.post(
            "/api/staff/livros/",
            {
                "titulo": "A Hora da Estrela",
                "autor": autor.pk,
                "genero": genero.pk,
                "quantidade": 3,
                "conteudo_explicito": False,
            },
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Livro.objects.filter(titulo="A Hora da Estrela").count(), 1)

    def test_staff_delete_livro(self):
        resp = self.client.delete(f"/api/staff/livros/{self.livro.pk}/")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Livro.objects.filter(pk=self.livro.pk).exists())

    def test_staff_list_alunos(self):
        resp = self.client.get("/api/staff/alunos/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIsInstance(resp.data, list)

    def test_staff_create_aluno(self):
        turma = Turma.objects.first()
        resp = self.client.post(
            "/api/staff/alunos/",
            {
                "username": "novaaluno",
                "first_name": "Nova",
                "last_name": "Aluna",
                "password": "Pass1234!",
                "matricula": "999",
                "turma_id": turma.pk,
            },
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="novaaluno").exists())

    def test_staff_registrar_emprestimo(self):
        resp = self.client.post(
            "/api/staff/emprestimos/",
            {"livro_id": self.livro.pk, "aluno_id": self.aluno.pk},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Emprestimo.objects.filter(aluno=self.aluno, livro=self.livro).count(), 1)

    def test_staff_devolver_emprestimo(self):
        emp = Emprestimo.objects.create(
            aluno=self.aluno,
            livro=self.livro,
            data_emprestimo=date.today(),
            data_devolucao_prevista=date.today() + timedelta(days=14),
            status="ABERTO",
        )
        resp = self.client.post(f"/api/staff/emprestimos/{emp.pk}/devolver/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        emp.refresh_from_db()
        self.assertEqual(emp.status, "DEVOLVIDO")

    def test_non_staff_cannot_access_staff_endpoints(self):
        aluno_user = make_user("alunonstaff")
        Aluno.objects.create(usuario=aluno_user, matricula="003")
        client = auth_client("alunonstaff")
        resp = client.get("/api/staff/livros/")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_crud_autores(self):
        resp = self.client.post("/api/staff/autores/", {"nome": "Fernando Pessoa"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        pk = resp.data["id"]

        resp = self.client.patch(f"/api/staff/autores/{pk}/", {"nome": "F. Pessoa"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        resp = self.client.delete(f"/api/staff/autores/{pk}/")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_relatorio_emprestimos_requires_dates(self):
        resp = self.client.get("/api/relatorios/emprestimos/")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_relatorio_emprestimos_with_dates(self):
        resp = self.client.get(
            "/api/relatorios/emprestimos/",
            {"data_inicio": "2024-01-01", "data_fim": "2024-12-31"},
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIsInstance(resp.data, list)
