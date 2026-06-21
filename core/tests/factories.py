"""Helpers centralizados de criação de dados para a suíte de testes.

Reúne os fabricantes (`make_*`) e utilitários de autenticação JWT antes
espalhados/duplicados entre os módulos de teste. Os arquivos novos importam
daqui; os antigos seguem com seus próprios helpers para evitar regressões.
"""

from django.contrib.auth.models import User
from rest_framework.test import APIClient

from core.models import Aluno, Autor, Genero, Livro, Turma

DEFAULT_PASSWORD = "Pass1234!"


def make_user(username="user", password=DEFAULT_PASSWORD, staff=False, **kwargs):
    return User.objects.create_user(
        username=username,
        password=password,
        first_name=kwargs.pop("first_name", "Test"),
        last_name=kwargs.pop("last_name", "User"),
        is_staff=staff,
        **kwargs,
    )


def make_staff(username="staff", password=DEFAULT_PASSWORD):
    return make_user(username=username, password=password, staff=True)


def make_turma(nome="1A", exibe_conteudo_explicito=False):
    return Turma.objects.create(
        nome=nome, exibe_conteudo_explicito=exibe_conteudo_explicito
    )


def make_aluno(username="aluno", password=DEFAULT_PASSWORD, matricula="001", turma=None):
    user = make_user(username=username, password=password)
    if turma is None:
        turma = make_turma(nome=f"turma-{username}"[:50])
    return Aluno.objects.create(usuario=user, matricula=matricula, turma=turma)


def make_autor(nome="Machado de Assis"):
    return Autor.objects.get_or_create(nome=nome)[0]


def make_genero(nome="Romance"):
    return Genero.objects.get_or_create(nome=nome)[0]


def make_livro(titulo="Dom Casmurro", disponivel=True, autor=None, genero=None, **kwargs):
    autor = autor or make_autor()
    genero = genero or make_genero()
    quantidade = kwargs.pop("quantidade", 2 if disponivel else 0)
    return Livro.objects.create(
        titulo=titulo, autor=autor, genero=genero, quantidade=quantidade, **kwargs
    )


def jwt_for(username, password=DEFAULT_PASSWORD):
    client = APIClient()
    resp = client.post(
        "/api/auth/token/",
        {"username": username, "password": password},
        format="json",
    )
    return resp.data["access"]


def auth_client(username, password=DEFAULT_PASSWORD):
    client = APIClient()
    token = jwt_for(username, password)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client
