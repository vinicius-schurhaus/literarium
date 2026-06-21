from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import api_views

router = DefaultRouter()
router.register(r"livros", api_views.LivroViewSet, basename="livro")
router.register(r"staff/livros", api_views.StaffLivroViewSet, basename="staff-livro")
router.register(r"staff/alunos", api_views.StaffAlunoViewSet, basename="staff-aluno")
router.register(r"staff/emprestimos", api_views.StaffEmprestimoViewSet, basename="staff-emprestimo")
router.register(r"staff/reservas", api_views.StaffReservaViewSet, basename="staff-reserva")
router.register(r"staff/resenhas", api_views.StaffResenhaViewSet, basename="staff-resenha")
router.register(r"staff/autores", api_views.StaffAutorViewSet, basename="staff-autor")
router.register(r"staff/generos", api_views.StaffGeneroViewSet, basename="staff-genero")
router.register(r"staff/turmas", api_views.StaffTurmaViewSet, basename="staff-turma")

urlpatterns = [
    # Auth
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/me/", api_views.UserProfileView.as_view(), name="user_profile"),
    path("auth/change-password/", api_views.ChangePasswordView.as_view(), name="change_password"),

    # Home
    path("home/", api_views.HomeView.as_view(), name="api_home"),

    # Gêneros (para filtro de catálogo)
    path("generos/", api_views.GeneroListView.as_view(), name="api_generos"),

    # Livros — detalhe e ações
    path("livros/<int:livro_id>/resenhas/", api_views.ResenhaView.as_view(), name="api_resenhas"),
    path("livros/<int:livro_id>/resenha/", api_views.ResenhaView.as_view(), name="api_salvar_resenha"),
    path("livros/<int:livro_id>/reservar/", api_views.ReservarLivroView.as_view(), name="api_reservar"),

    # Empréstimos do aluno
    path("meus-emprestimos/", api_views.MeusEmprestimosView.as_view(), name="api_meus_emprestimos"),
    path("emprestimos/<int:emprestimo_id>/renovar/", api_views.RenovarEmprestimoView.as_view(), name="api_renovar"),
    path("minhas-reservas/<int:pk>/cancelar/", api_views.CancelarMinhaReservaView.as_view(), name="api_cancelar_reserva"),

    # Relatórios
    path("relatorios/emprestimos/", api_views.RelatorioEmprestimosView.as_view(), name="api_relatorio_emprestimos"),
    path("relatorios/devolucoes/", api_views.RelatorioDevolucoesView.as_view(), name="api_relatorio_devolucoes"),

    # Router (livros, staff/*)
    path("", include(router.urls)),
]
