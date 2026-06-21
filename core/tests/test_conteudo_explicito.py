"""Testes da regra de conteúdo explícito (RN005) no nível da API."""

from rest_framework import status
from django.test import TestCase

from core.tests.factories import auth_client, make_aluno, make_genero, make_livro, make_turma


class ConteudoExplicitoTests(TestCase):
    def setUp(self):
        self.livro_normal = make_livro("Livro Normal", conteudo_explicito=False)
        self.livro_explicito = make_livro("Livro Adulto", conteudo_explicito=True)

    def test_aluno_sem_permissao_nao_ve_explicito_no_catalogo(self):
        turma = make_turma(nome="restrita", exibe_conteudo_explicito=False)
        make_aluno("restrito", matricula="001", turma=turma)
        client = auth_client("restrito")
        resp = client.get("/api/livros/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        titulos = [l["titulo"] for l in resp.data["results"]]
        self.assertIn("Livro Normal", titulos)
        self.assertNotIn("Livro Adulto", titulos)

    def test_aluno_com_permissao_ve_explicito_no_catalogo(self):
        turma = make_turma(nome="liberada", exibe_conteudo_explicito=True)
        make_aluno("liberado", matricula="002", turma=turma)
        client = auth_client("liberado")
        resp = client.get("/api/livros/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        titulos = [l["titulo"] for l in resp.data["results"]]
        self.assertIn("Livro Adulto", titulos)

    def test_explicito_oculto_na_home_sem_permissao(self):
        turma = make_turma(nome="restrita", exibe_conteudo_explicito=False)
        make_aluno("restrito", matricula="001", turma=turma)
        client = auth_client("restrito")
        resp = client.get("/api/home/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        titulos = [l["titulo"] for l in resp.data["livros_recentes"]]
        self.assertNotIn("Livro Adulto", titulos)

    def test_aluno_sem_acesso_direto_a_livro_explicito_404(self):
        turma = make_turma(nome="restrita", exibe_conteudo_explicito=False)
        make_aluno("restrito", matricula="001", turma=turma)
        client = auth_client("restrito")
        resp = client.get(f"/api/livros/{self.livro_explicito.pk}/")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


class HomeVestibularTests(TestCase):
    def test_secao_vestibular_lista_livros_do_genero(self):
        vestibular = make_genero("Vestibular")
        make_livro("Apostila ENEM", genero=vestibular)
        make_livro("Romance Comum", genero=make_genero("Romance"))
        make_aluno("aluno", matricula="001")
        client = auth_client("aluno")
        resp = client.get("/api/home/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        titulos = [l["titulo"] for l in resp.data["livros_vestibular"]]
        self.assertIn("Apostila ENEM", titulos)
        self.assertNotIn("Romance Comum", titulos)
