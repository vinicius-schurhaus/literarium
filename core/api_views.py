import csv
from datetime import timedelta

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services
from .models import Aluno, Autor, Emprestimo, Genero, Livro, Reserva, Resenha, Turma
from .serializers import (
    AlunoSerializer,
    AlunoWriteSerializer,
    AutorSerializer,
    EmprestimoSerializer,
    GeneroSerializer,
    LivroDetailSerializer,
    LivroListSerializer,
    LivroWriteSerializer,
    ResenhaSerializer,
    ResenhaWriteSerializer,
    ReservaSerializer,
    StaffResenhaSerializer,
    TurmaSerializer,
    UserProfileSerializer,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _livros_qs(user):
    """Queryset base de livros com filtro de conteúdo explícito por turma."""
    qs = Livro.objects.select_related("autor", "genero")
    if user.is_staff:
        return qs
    aluno = getattr(user, "aluno_perfil", None)
    turma = aluno.turma if aluno else None
    if not turma or not turma.exibe_conteudo_explicito:
        qs = qs.filter(conteudo_explicito=False)
    return qs


# ---------------------------------------------------------------------------
# Permissões customizadas
# ---------------------------------------------------------------------------

class IsAluno(IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and hasattr(request.user, "aluno_perfil")


class IsStaff(IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.is_staff


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        old_password = request.data.get("old_password", "")
        new_password1 = request.data.get("new_password1", "")
        new_password2 = request.data.get("new_password2", "")

        if not request.user.check_password(old_password):
            return Response(
                {"old_password": "Senha atual incorreta."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if new_password1 != new_password2:
            return Response(
                {"new_password2": "As senhas não coincidem."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            from django.contrib.auth.password_validation import validate_password
            validate_password(new_password1, request.user)
        except DjangoValidationError as exc:
            return Response({"new_password1": list(exc.messages)}, status=status.HTTP_400_BAD_REQUEST)

        request.user.set_password(new_password1)
        request.user.save()
        return Response({"detail": "Senha alterada com sucesso."})


# ---------------------------------------------------------------------------
# Endpoints de aluno / catálogo
# ---------------------------------------------------------------------------

class HomeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        base = _livros_qs(request.user)
        desde = timezone.now().date() - timedelta(days=90)

        livros_recentes = base.order_by("-data_cadastro")[:8]
        livros_populares = (
            base.annotate(
                total_emprestimos=Count(
                    "emprestimo",
                    filter=Q(emprestimo__data_emprestimo__gte=desde),
                )
            ).order_by("-total_emprestimos")[:8]
        )
        livros_vestibular = base.filter(genero__nome__iexact="vestibular").order_by("-data_cadastro")[:8]

        ctx = {"request": request}
        return Response({
            "livros_recentes": LivroListSerializer(livros_recentes, many=True, context=ctx).data,
            "livros_populares": LivroListSerializer(livros_populares, many=True, context=ctx).data,
            "livros_vestibular": LivroListSerializer(livros_vestibular, many=True, context=ctx).data,
        })


class LivroViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = _livros_qs(self.request.user)
        q = self.request.query_params.get("q")
        if q:
            qs = qs.filter(Q(titulo__icontains=q) | Q(autor__nome__icontains=q))
        genero_id = self.request.query_params.get("genero")
        if genero_id:
            qs = qs.filter(genero_id=genero_id)
        return qs.order_by("-data_cadastro")

    def get_serializer_class(self):
        if self.action == "retrieve":
            return LivroDetailSerializer
        return LivroListSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx

    @action(detail=False, methods=["get"], url_path="populares")
    def populares(self, request):
        livros = services.livros_mais_populares(meses=3, limite=20)
        serializer = LivroListSerializer(livros, many=True, context={"request": request})
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="status-aluno", permission_classes=[IsAluno])
    def status_aluno(self, request, pk=None):
        livro = self.get_object()
        aluno = request.user.aluno_perfil
        ja_tem_emprestimo = Emprestimo.objects.do_aluno(aluno).do_livro(livro).abertos().exists()
        ja_reservou = Reserva.objects.do_livro(livro).do_aluno(aluno).ativas().exists()
        pode_reservar = not livro.disponivel and not ja_reservou and not ja_tem_emprestimo
        return Response({
            "ja_tem_emprestimo": ja_tem_emprestimo,
            "ja_reservou": ja_reservou,
            "pode_reservar": pode_reservar,
        })


class GeneroListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GeneroSerializer
    queryset = Genero.objects.all()
    pagination_class = None


class ResenhaView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]
        return [IsAluno()]

    def get(self, request, livro_id):
        livro = get_object_or_404(Livro, pk=livro_id)
        resenhas = livro.resenhas.select_related("aluno__usuario").order_by("-data_criacao")
        serializer = ResenhaSerializer(resenhas, many=True, context={"request": request})
        return Response(serializer.data)

    def post(self, request, livro_id):
        livro = get_object_or_404(Livro, pk=livro_id)
        aluno = request.user.aluno_perfil
        serializer = ResenhaWriteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        resenha, criada = Resenha.objects.update_or_create(
            aluno=aluno,
            livro=livro,
            defaults={"nota": serializer.validated_data["nota"], "texto": serializer.validated_data["texto"]},
        )
        result = ResenhaSerializer(resenha, context={"request": request})
        return Response(result.data, status=status.HTTP_201_CREATED if criada else status.HTTP_200_OK)


class MeusEmprestimosView(APIView):
    permission_classes = [IsAluno]

    def get(self, request):
        aluno = request.user.aluno_perfil
        emprestimos = (
            Emprestimo.objects.do_aluno(aluno)
            .select_related("livro__autor", "livro__genero")
            .order_by("-data_emprestimo")
        )
        reservas = (
            Reserva.objects.do_aluno(aluno)
            .ativas()
            .select_related("livro__autor", "livro__genero")
            .order_by("data_disponivel_prevista")
        )
        ctx = {"request": request}
        return Response({
            "emprestimos": EmprestimoSerializer(emprestimos, many=True, context=ctx).data,
            "reservas": ReservaSerializer(reservas, many=True, context=ctx).data,
        })


class ReservarLivroView(APIView):
    permission_classes = [IsAluno]

    def post(self, request, livro_id):
        livro = get_object_or_404(Livro, pk=livro_id)
        aluno = request.user.aluno_perfil
        try:
            reserva = services.criar_reserva(aluno, livro)
        except DjangoValidationError as exc:
            return Response({"detail": exc.message}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ReservaSerializer(reserva, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RenovarEmprestimoView(APIView):
    permission_classes = [IsAluno]

    def post(self, request, emprestimo_id):
        aluno = request.user.aluno_perfil
        emprestimo = get_object_or_404(Emprestimo, pk=emprestimo_id)
        if emprestimo.aluno != aluno:
            return Response({"detail": "Sem permissão."}, status=status.HTTP_403_FORBIDDEN)
        try:
            services.renovar_emprestimo(emprestimo)
        except DjangoValidationError as exc:
            return Response({"detail": exc.message}, status=status.HTTP_400_BAD_REQUEST)
        serializer = EmprestimoSerializer(emprestimo, context={"request": request})
        return Response(serializer.data)


class CancelarMinhaReservaView(APIView):
    permission_classes = [IsAluno]

    def post(self, request, pk):
        aluno = request.user.aluno_perfil
        reserva = get_object_or_404(Reserva, pk=pk, aluno=aluno)
        if reserva.status != "ATIVA":
            return Response({"detail": "Só é possível cancelar reservas ativas."}, status=status.HTTP_400_BAD_REQUEST)
        reserva.status = "CANCELADA"
        reserva.save(update_fields=["status"])
        return Response({"status": "cancelada"})


# ---------------------------------------------------------------------------
# Staff — CRUD de Livros
# ---------------------------------------------------------------------------

class StaffLivroViewSet(viewsets.ModelViewSet):
    permission_classes = [IsStaff]
    queryset = Livro.objects.select_related("autor", "genero").order_by("-data_cadastro")

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return LivroDetailSerializer
        return LivroWriteSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.query_params.get("q")
        if q:
            qs = qs.filter(Q(titulo__icontains=q) | Q(autor__nome__icontains=q))
        return qs


# ---------------------------------------------------------------------------
# Staff — CRUD de Alunos
# ---------------------------------------------------------------------------

class StaffAlunoViewSet(viewsets.ViewSet):
    permission_classes = [IsStaff]

    def list(self, request):
        qs = Aluno.objects.select_related("usuario", "turma").order_by("usuario__first_name")
        q = request.query_params.get("q")
        if q:
            qs = qs.filter(
                Q(usuario__first_name__icontains=q)
                | Q(usuario__last_name__icontains=q)
                | Q(matricula__icontains=q)
            )
        serializer = AlunoSerializer(qs, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        aluno = get_object_or_404(Aluno.objects.select_related("usuario", "turma"), pk=pk)
        return Response(AlunoSerializer(aluno).data)

    def create(self, request):
        serializer = AlunoWriteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data
        user = User(
            username=data["username"],
            first_name=data["first_name"],
            last_name=data.get("last_name", ""),
            email=data.get("email", ""),
        )
        user.set_password(data["password"])
        user.save()
        aluno = Aluno.objects.create(
            usuario=user,
            matricula=data["matricula"],
            turma=data.get("turma"),
        )
        return Response(AlunoSerializer(aluno).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        aluno = get_object_or_404(Aluno, pk=pk)
        serializer = AlunoWriteSerializer(
            data=request.data, context={"aluno_pk": pk}, partial=False
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data
        user = aluno.usuario
        user.first_name = data["first_name"]
        user.last_name = data.get("last_name", "")
        user.email = data.get("email", "")
        if data.get("password"):
            user.set_password(data["password"])
        user.save()
        aluno.matricula = data["matricula"]
        aluno.turma = data.get("turma")
        aluno.save()
        return Response(AlunoSerializer(aluno).data)

    def partial_update(self, request, pk=None):
        aluno = get_object_or_404(Aluno, pk=pk)
        serializer = AlunoWriteSerializer(
            data=request.data, context={"aluno_pk": pk}, partial=True
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data
        user = aluno.usuario
        if "first_name" in data:
            user.first_name = data["first_name"]
        if "last_name" in data:
            user.last_name = data["last_name"]
        if "email" in data:
            user.email = data["email"]
        if data.get("password"):
            user.set_password(data["password"])
        user.save()
        if "matricula" in data:
            aluno.matricula = data["matricula"]
        if "turma" in data:
            aluno.turma = data["turma"]
        aluno.save()
        return Response(AlunoSerializer(aluno).data)

    def destroy(self, request, pk=None):
        aluno = get_object_or_404(Aluno, pk=pk)
        user = aluno.usuario
        aluno.delete()
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# Staff — Empréstimos
# ---------------------------------------------------------------------------

class StaffEmprestimoViewSet(viewsets.ViewSet):
    permission_classes = [IsStaff]

    def list(self, request):
        qs = (
            Emprestimo.objects.select_related("livro__autor", "livro__genero", "aluno__usuario")
            .order_by("-data_emprestimo")
        )
        q = request.query_params.get("q")
        if q:
            qs = qs.filter(
                Q(livro__titulo__icontains=q)
                | Q(aluno__usuario__first_name__icontains=q)
                | Q(aluno__matricula__icontains=q)
            )
        status_filter = request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)
        serializer = EmprestimoSerializer(qs, many=True, context={"request": request})
        return Response(serializer.data)

    def create(self, request):
        livro_id = request.data.get("livro_id")
        aluno_id = request.data.get("aluno_id")
        if not livro_id or not aluno_id:
            return Response({"detail": "livro_id e aluno_id são obrigatórios."}, status=status.HTTP_400_BAD_REQUEST)
        livro = get_object_or_404(Livro, pk=livro_id)
        aluno = get_object_or_404(Aluno, pk=aluno_id)
        try:
            emprestimo = services.registrar_emprestimo(aluno, livro)
        except DjangoValidationError as exc:
            return Response({"detail": exc.message}, status=status.HTTP_400_BAD_REQUEST)
        serializer = EmprestimoSerializer(emprestimo, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="devolver")
    def devolver(self, request, pk=None):
        emprestimo = get_object_or_404(Emprestimo, pk=pk)
        try:
            services.devolver_emprestimo(emprestimo)
        except DjangoValidationError as exc:
            return Response({"detail": exc.message}, status=status.HTTP_400_BAD_REQUEST)
        serializer = EmprestimoSerializer(emprestimo, context={"request": request})
        return Response(serializer.data)


# ---------------------------------------------------------------------------
# Staff — Reservas
# ---------------------------------------------------------------------------

class StaffReservaViewSet(viewsets.ViewSet):
    permission_classes = [IsStaff]

    def list(self, request):
        qs = (
            Reserva.objects.select_related("livro__autor", "aluno__usuario")
            .order_by("-data_reserva")
        )
        q = request.query_params.get("q")
        if q:
            qs = qs.filter(
                Q(livro__titulo__icontains=q)
                | Q(aluno__usuario__first_name__icontains=q)
                | Q(aluno__usuario__last_name__icontains=q)
                | Q(aluno__matricula__icontains=q)
            )
        status_filter = request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)
        serializer = ReservaSerializer(qs, many=True, context={"request": request})
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="cancelar")
    def cancelar(self, request, pk=None):
        reserva = get_object_or_404(Reserva, pk=pk)
        if reserva.status != "ATIVA":
            return Response({"detail": "Só é possível cancelar reservas ativas."}, status=status.HTTP_400_BAD_REQUEST)
        reserva.status = "CANCELADA"
        reserva.save(update_fields=["status"])
        serializer = ReservaSerializer(reserva, context={"request": request})
        return Response(serializer.data)


# ---------------------------------------------------------------------------
# Staff — Resenhas
# ---------------------------------------------------------------------------

class StaffResenhaViewSet(mixins.ListModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsStaff]
    serializer_class = StaffResenhaSerializer
    pagination_class = None

    def get_queryset(self):
        qs = Resenha.objects.select_related("aluno__usuario", "livro").order_by("-data_criacao")
        q = self.request.query_params.get("q")
        if q:
            qs = qs.filter(
                Q(livro__titulo__icontains=q)
                | Q(aluno__usuario__first_name__icontains=q)
                | Q(aluno__usuario__last_name__icontains=q)
            )
        return qs

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx


# ---------------------------------------------------------------------------
# Staff — Lookup tables (Autor, Genero, Turma)
# ---------------------------------------------------------------------------

class StaffAutorViewSet(viewsets.ModelViewSet):
    permission_classes = [IsStaff]
    serializer_class = AutorSerializer
    queryset = Autor.objects.order_by("nome")
    pagination_class = None


class StaffGeneroViewSet(viewsets.ModelViewSet):
    permission_classes = [IsStaff]
    serializer_class = GeneroSerializer
    queryset = Genero.objects.order_by("nome")
    pagination_class = None


class StaffTurmaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsStaff]
    serializer_class = TurmaSerializer
    queryset = Turma.objects.order_by("nome")
    pagination_class = None


# ---------------------------------------------------------------------------
# Relatórios
# ---------------------------------------------------------------------------

class RelatorioEmprestimosView(APIView):
    permission_classes = [IsStaff]

    def get(self, request):
        data_inicio = request.query_params.get("data_inicio")
        data_fim = request.query_params.get("data_fim")
        if not data_inicio or not data_fim:
            return Response({"detail": "data_inicio e data_fim são obrigatórios."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            from datetime import date
            inicio = date.fromisoformat(data_inicio)
            fim = date.fromisoformat(data_fim)
        except ValueError:
            return Response({"detail": "Formato de data inválido. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        if fim < inicio:
            return Response({"detail": "A data final não pode ser anterior à data inicial."}, status=status.HTTP_400_BAD_REQUEST)

        qs = (
            Emprestimo.objects.no_periodo(inicio, fim)
            .select_related("livro", "aluno__usuario")
            .order_by("data_emprestimo")
        )

        if request.query_params.get("exportar"):
            return _exportar_emprestimos_csv(qs, "emprestimos")

        serializer = EmprestimoSerializer(qs, many=True, context={"request": request})
        return Response(serializer.data)


class RelatorioDevolucoesView(APIView):
    permission_classes = [IsStaff]

    def get(self, request):
        data_inicio = request.query_params.get("data_inicio")
        data_fim = request.query_params.get("data_fim")
        if not data_inicio or not data_fim:
            return Response({"detail": "data_inicio e data_fim são obrigatórios."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            from datetime import date
            inicio = date.fromisoformat(data_inicio)
            fim = date.fromisoformat(data_fim)
        except ValueError:
            return Response({"detail": "Formato de data inválido. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        if fim < inicio:
            return Response({"detail": "A data final não pode ser anterior à data inicial."}, status=status.HTTP_400_BAD_REQUEST)

        qs = (
            Emprestimo.objects.devolvidos()
            .no_periodo(inicio, fim)
            .select_related("livro", "aluno__usuario")
            .order_by("data_devolucao_real")
        )

        if request.query_params.get("exportar"):
            return _exportar_emprestimos_csv(qs, "devolucoes")

        serializer = EmprestimoSerializer(qs, many=True, context={"request": request})
        return Response(serializer.data)


def _exportar_emprestimos_csv(emprestimos, nome_arquivo: str) -> HttpResponse:
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{nome_arquivo}.csv"'
    response.write("﻿")
    writer = csv.writer(response)
    writer.writerow(["Livro", "Aluno", "Data Empréstimo", "Data Prev. Devolução", "Data Real Devolução", "Status"])
    for e in emprestimos:
        writer.writerow([
            e.livro.titulo,
            str(e.aluno),
            e.data_emprestimo.strftime("%d/%m/%Y"),
            e.data_devolucao_prevista.strftime("%d/%m/%Y") if e.data_devolucao_prevista else "",
            e.data_devolucao_real.strftime("%d/%m/%Y") if e.data_devolucao_real else "",
            e.get_status_display(),
        ])
    return response
