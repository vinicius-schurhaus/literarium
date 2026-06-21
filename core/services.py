"""Camada de serviços do Literarium.

Toda lógica de negócio que envolve múltiplos models ou regras de domínio
fica aqui, mantendo views e admin finos.
"""
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Count, Q
from django.utils import timezone

from .models import Aluno, Emprestimo, Livro, Reserva


def registrar_emprestimo(aluno: Aluno, livro: Livro, data_devolucao_prevista=None) -> Emprestimo:
    """Cria um empréstimo aplicando RN002 e RN004.

    Args:
        aluno: Perfil do aluno que está realizando o empréstimo.
        livro: Livro a ser emprestado.
        data_devolucao_prevista: Data prevista para devolução; padrão +7 dias.

    Returns:
        Instância de Emprestimo criada.

    Raises:
        ValidationError: Se o aluno tem pendência (RN002) ou o livro não tem
            exemplares disponíveis (RN004).
    """
    if aluno.tem_pendencia:
        raise ValidationError("O aluno possui empréstimo(s) em atraso e não pode realizar novos empréstimos (RN002).")

    emprestimo = Emprestimo(
        aluno=aluno,
        livro=livro,
        data_devolucao_prevista=data_devolucao_prevista,
    )
    emprestimo.full_clean()
    emprestimo.save()
    return emprestimo


def devolver_emprestimo(emprestimo: Emprestimo) -> Emprestimo:
    """Registra a devolução de um empréstimo em aberto.

    Args:
        emprestimo: Instância de Emprestimo com status ABERTO.

    Returns:
        Instância de Emprestimo atualizada.

    Raises:
        ValidationError: Se o empréstimo já foi devolvido.
    """
    if emprestimo.status == "DEVOLVIDO":
        raise ValidationError("Este empréstimo já foi devolvido.")

    emprestimo.status = "DEVOLVIDO"
    emprestimo.save()

    _atender_proxima_reserva(emprestimo.livro)

    return emprestimo


def renovar_emprestimo(emprestimo: Emprestimo) -> Emprestimo:
    """Renova um empréstimo, adicionando 7 dias respeitando reservas ativas (RF012).

    Se houver reserva ativa para o livro com data anterior à nova data prevista,
    o prazo é limitado à data dessa reserva.

    Args:
        emprestimo: Instância de Emprestimo com status ABERTO.

    Returns:
        Instância de Emprestimo atualizada.

    Raises:
        ValidationError: Se o empréstimo já foi devolvido.
    """
    if emprestimo.status == "DEVOLVIDO":
        raise ValidationError("Não é possível renovar um empréstimo já devolvido.")

    nova_data = timezone.now().date() + timedelta(days=7)

    proxima_reserva = (
        Reserva.objects.do_livro(emprestimo.livro)
        .ativas()
        .order_by("data_disponivel_prevista")
        .first()
    )
    if proxima_reserva and proxima_reserva.data_disponivel_prevista:
        if proxima_reserva.data_disponivel_prevista < nova_data:
            nova_data = proxima_reserva.data_disponivel_prevista

    emprestimo.data_devolucao_prevista = nova_data
    emprestimo.save(update_fields=["data_devolucao_prevista"])
    return emprestimo


@transaction.atomic
def criar_reserva(aluno: Aluno, livro: Livro) -> Reserva:
    """Cria uma reserva calculando a próxima data disponível (RF011).

    A data disponível prevista é calculada como MAX(data_devolucao_prevista)
    dos empréstimos em aberto + 1 dia. Se o livro estiver disponível, a reserva
    é criada com data imediata.

    Args:
        aluno: Perfil do aluno que está realizando a reserva.
        livro: Livro a ser reservado.

    Returns:
        Instância de Reserva criada.

    Raises:
        ValidationError: Se o aluno já possui reserva ativa para o livro, ou
            o livro está disponível (deve fazer empréstimo direto).
    """
    if Reserva.objects.do_livro(livro).do_aluno(aluno).ativas().exists():
        raise ValidationError("Você já possui uma reserva ativa para este livro.")

    if Emprestimo.objects.do_aluno(aluno).do_livro(livro).abertos().exists():
        raise ValidationError("Você já possui um empréstimo ativo para este livro.")

    if livro.disponivel:
        raise ValidationError(
            "O livro está disponível para empréstimo direto. Reserve apenas quando não houver exemplares."
        )

    data_disponivel = _calcular_proxima_data_disponivel(livro)
    reserva = Reserva(aluno=aluno, livro=livro, data_disponivel_prevista=data_disponivel)
    reserva.save()
    return reserva


def livros_mais_populares(meses: int = 3, limite: int = 10):
    """Retorna livros ordenados por número de empréstimos nos últimos N meses (RF018).

    Args:
        meses: Janela de tempo em meses para contagem de empréstimos.
        limite: Quantidade máxima de livros retornados.

    Returns:
        QuerySet de Livro anotado com `total_emprestimos`, ordenado decrescentemente.
    """
    desde = timezone.now().date() - timedelta(days=30 * meses)
    return (
        Livro.objects.annotate(
            total_emprestimos=Count(
                "emprestimo",
                filter=Q(emprestimo__data_emprestimo__gte=desde),
            )
        )
        .select_related("autor", "genero")
        .order_by("-total_emprestimos")[:limite]
    )


def livros_recentes(limite: int = 10):
    """Retorna os livros mais recentemente adicionados ao catálogo (RF019).

    Args:
        limite: Quantidade máxima de livros retornados.

    Returns:
        QuerySet de Livro ordenado por data de cadastro decrescente.
    """
    return Livro.objects.select_related("autor", "genero").order_by("-data_cadastro")[:limite]


# ---------------------------------------------------------------------------
# Auxiliares internos
# ---------------------------------------------------------------------------

def _calcular_proxima_data_disponivel(livro: Livro):
    from django.db.models import Max
    resultado = Emprestimo.objects.do_livro(livro).abertos().aggregate(Max("data_devolucao_prevista"))
    max_data = resultado["data_devolucao_prevista__max"]
    if max_data:
        return max_data + timedelta(days=1)
    return timezone.now().date() + timedelta(days=1)


def _atender_proxima_reserva(livro: Livro):
    reserva = (
        Reserva.objects.do_livro(livro)
        .ativas()
        .order_by("data_reserva")
        .first()
    )
    if reserva:
        reserva.status = "ATENDIDA"
        reserva.save(update_fields=["status"])
