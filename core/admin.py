from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from unfold.admin import ModelAdmin, StackedInline
from django.utils.html import format_html
from .models import Autor, Genero, Livro, Aluno, Emprestimo

admin.site.unregister(User)

# --- CONFIGURAÇÃO DO INLINE ---
class AlunoInline(StackedInline):
    model = Aluno
    can_delete = False
    verbose_name_plural = 'Dados Escolares (Aluno)'
    fk_name = 'usuario'

# --- CONFIGURAÇÃO DO USUÁRIO ---
@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    list_display = ('username', 'first_name', 'email', 'get_turma', 'is_staff')
    search_fields = ['username', 'first_name', 'email', 'aluno_perfil__matricula']

    def get_inlines(self, request, obj=None):
        if not obj:
            return []
        return [AlunoInline] 

    def get_turma(self, instance):
        if hasattr(instance, 'aluno_perfil'):
            return instance.aluno_perfil.turma
        return "-"
    get_turma.short_description = 'Turma'

# --- OUTROS CADASTROS ---

@admin.register(Autor)
class AutorAdmin(ModelAdmin):
    search_fields = ['nome']

@admin.register(Genero)
class GeneroAdmin(ModelAdmin):
    search_fields = ['nome']

# Mantivemos o AlunoAdmin separado caso precise corrigir algo isolado
@admin.register(Aluno)
class AlunoAdmin(ModelAdmin):
    list_display = ('matricula', 'turma', 'get_nome')
    search_fields = ('matricula', 'usuario__first_name')
    autocomplete_fields = ['usuario']

    def get_nome(self, obj):
        return obj.usuario.first_name
    get_nome.short_description = 'Nome'

@admin.register(Livro)
class LivroAdmin(ModelAdmin):
    list_display = ('titulo', 'autor', 'quantidade', 'ver_capa')
    search_fields = ('titulo',)
    list_filter = ('genero',)
    autocomplete_fields = ['autor', 'genero']

    def ver_capa(self, obj):
        if obj.capa:
            return format_html('<img src="{}" style="height:50px; border-radius:4px;" />', obj.capa.url)
        return "-"
    ver_capa.short_description = 'Capa'

@admin.register(Emprestimo)
class EmprestimoAdmin(ModelAdmin):
    list_display = ('livro', 'aluno', 'data_devolucao_prevista', 'status')
    list_filter = ('status', 'data_emprestimo')
    autocomplete_fields = ['livro', 'aluno']