from django import forms
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.html import format_html

from . import services
from .models import Aluno, Autor, Emprestimo, Genero, Livro, Reserva, Resenha, Turma

admin.site.unregister(User)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    search_fields = ["username", "first_name", "last_name", "email"]


@admin.register(Autor)
class AutorAdmin(admin.ModelAdmin):
    list_display = ("nome",)
    search_fields = ["nome"]
    ordering = ["nome"]


@admin.register(Genero)
class GeneroAdmin(admin.ModelAdmin):
    list_display = ("nome",)
    search_fields = ["nome"]
    ordering = ["nome"]


@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    list_display = ("nome", "exibe_conteudo_explicito")
    list_filter = ("exibe_conteudo_explicito",)
    search_fields = ["nome"]
    ordering = ["nome"]


class AlunoAdminForm(forms.ModelForm):
    username = forms.CharField(label="Nome de usuário", max_length=150)
    first_name = forms.CharField(label="Nome", max_length=150)
    last_name = forms.CharField(label="Sobrenome", max_length=150, required=False)
    email = forms.EmailField(label="E-mail", required=False)
    password1 = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(render_value=False),
        required=False,
        help_text="Deixe em branco para manter a senha atual (edição). Obrigatório na criação.",
    )
    password2 = forms.CharField(
        label="Confirmar senha",
        widget=forms.PasswordInput(render_value=False),
        required=False,
    )

    class Meta:
        model = Aluno
        fields = ["matricula", "turma"]

    def clean_username(self):
        username = self.cleaned_data.get("username")
        qs = User.objects.filter(username=username)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.usuario_id)
        if qs.exists():
            raise ValidationError("Este nome de usuário já está em uso.")
        return username

    def clean_password2(self):
        p1 = self.cleaned_data.get("password1")
        p2 = self.cleaned_data.get("password2")
        if p1 or p2:
            if p1 != p2:
                raise ValidationError("As senhas não coincidem.")
            try:
                validate_password(p1)
            except ValidationError as e:
                raise ValidationError(e.messages)
        return p2

    def clean(self):
        cleaned = super().clean()
        if not self.instance.pk and not cleaned.get("password1"):
            self.add_error("password1", "A senha é obrigatória para novos alunos.")
        return cleaned


class EmprestimoInline(admin.TabularInline):
    model = Emprestimo
    extra = 0
    fields = ("livro", "data_emprestimo", "data_devolucao_prevista", "status", "esta_atrasado_display")
    readonly_fields = ("data_emprestimo", "esta_atrasado_display")

    def esta_atrasado_display(self, obj):
        if obj.pk and obj.esta_atrasado:
            return format_html('<span style="color:red;font-weight:bold;">Sim</span>')
        return "Não"
    esta_atrasado_display.short_description = "Atrasado?"


@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    form = AlunoAdminForm
    list_display = ("get_nome_completo", "matricula", "turma", "tem_pendencia_display")
    search_fields = ("matricula", "usuario__first_name", "usuario__last_name", "usuario__username")
    list_filter = ("turma",)
    inlines = [EmprestimoInline]
    fieldsets = (
        ("Dados do usuário", {
            "fields": ("username", "first_name", "last_name", "email", "password1", "password2"),
        }),
        ("Dados do aluno", {
            "fields": ("matricula", "turma"),
        }),
    )

    @admin.display(description="Nome")
    def get_nome_completo(self, obj):
        return obj.usuario.get_full_name() or obj.usuario.username

    @admin.display(description="Pendência?", boolean=True)
    def tem_pendencia_display(self, obj):
        return obj.tem_pendencia

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:
            form.base_fields["username"].initial = obj.usuario.username
            form.base_fields["first_name"].initial = obj.usuario.first_name
            form.base_fields["last_name"].initial = obj.usuario.last_name
            form.base_fields["email"].initial = obj.usuario.email
            form.base_fields["password1"].required = False
            form.base_fields["password2"].required = False
        else:
            form.base_fields["password1"].required = True
            form.base_fields["password2"].required = True
        return form

    def save_model(self, request, obj, form, change):
        if not change:
            user = User(
                username=form.cleaned_data["username"],
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data.get("last_name", ""),
                email=form.cleaned_data.get("email", ""),
            )
            user.set_password(form.cleaned_data["password1"])
            user.save()
            obj.usuario = user
        else:
            user = obj.usuario
            user.first_name = form.cleaned_data["first_name"]
            user.last_name = form.cleaned_data.get("last_name", "")
            user.email = form.cleaned_data.get("email", "")
            if form.cleaned_data.get("password1"):
                user.set_password(form.cleaned_data["password1"])
            user.save()
        super().save_model(request, obj, form, change)


@admin.register(Livro)
class LivroAdmin(admin.ModelAdmin):
    list_display = ("titulo", "autor", "genero", "quantidade", "conteudo_explicito", "disponivel_display", "ver_capa")
    search_fields = ("titulo", "autor__nome")
    list_filter = ("genero", "autor", "conteudo_explicito")
    autocomplete_fields = ["autor", "genero"]
    readonly_fields = ("data_cadastro",)

    @admin.display(description="Disponível?", boolean=True)
    def disponivel_display(self, obj):
        return obj.disponivel

    def ver_capa(self, obj):
        if obj.capa:
            return format_html('<img src="{}" style="height:50px; border-radius:4px;" />', obj.capa.url)
        return "—"
    ver_capa.short_description = "Capa"


@admin.register(Emprestimo)
class EmprestimoAdmin(admin.ModelAdmin):
    list_display = ("livro", "aluno", "data_emprestimo", "data_devolucao_prevista", "status", "esta_atrasado_display")
    list_filter = ("status", "data_emprestimo")
    search_fields = ("livro__titulo", "aluno__usuario__first_name", "aluno__usuario__last_name", "aluno__matricula")
    date_hierarchy = "data_emprestimo"
    readonly_fields = ("data_emprestimo", "data_devolucao_real")
    autocomplete_fields = ["livro", "aluno"]
    actions = ["marcar_como_devolvido"]

    @admin.display(description="Atrasado?", boolean=True)
    def esta_atrasado_display(self, obj):
        return obj.esta_atrasado

    @admin.action(description="Marcar selecionados como devolvidos")
    def marcar_como_devolvido(self, request, queryset):
        sucesso = 0
        for emprestimo in queryset.filter(status="ABERTO"):
            try:
                services.devolver_emprestimo(emprestimo)
                sucesso += 1
            except ValidationError as exc:
                self.message_user(request, f"Erro em '{emprestimo}': {exc.message}", messages.ERROR)
        if sucesso:
            self.message_user(request, f"{sucesso} empréstimo(s) marcado(s) como devolvido(s).", messages.SUCCESS)


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ("livro", "aluno", "data_reserva", "data_disponivel_prevista", "status")
    list_filter = ("status",)
    search_fields = ("livro__titulo", "aluno__usuario__first_name", "aluno__matricula")
    readonly_fields = ("data_reserva",)
    autocomplete_fields = ["livro", "aluno"]
    actions = ["cancelar_reservas"]

    @admin.action(description="Cancelar reservas selecionadas")
    def cancelar_reservas(self, request, queryset):
        atualizadas = queryset.filter(status="ATIVA").update(status="CANCELADA")
        self.message_user(request, f"{atualizadas} reserva(s) cancelada(s).", messages.SUCCESS)


@admin.register(Resenha)
class ResenhaAdmin(admin.ModelAdmin):
    list_display = ("livro", "aluno", "nota", "data_criacao")
    list_filter = ("nota", "livro")
    search_fields = ("livro__titulo", "aluno__usuario__first_name", "aluno__matricula")
    readonly_fields = ("data_criacao",)
    autocomplete_fields = ["livro", "aluno"]
