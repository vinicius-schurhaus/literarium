from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from unfold.admin import ModelAdmin
from django.utils.html import format_html
from .models import Autor, Genero, Livro, Aluno, Emprestimo

admin.site.unregister(User)

@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin): pass

@admin.register(Autor)
class AutorAdmin(ModelAdmin): pass

@admin.register(Genero)
class GeneroAdmin(ModelAdmin): pass

@admin.register(Aluno)
class AlunoAdmin(ModelAdmin):
    list_display = ('matricula', 'turma')

@admin.register(Livro)
class LivroAdmin(ModelAdmin):
    list_display = ('titulo', 'autor', 'quantidade', 'ver_capa')
    search_fields = ('titulo',)

    def ver_capa(self, obj):
        if obj.capa:
            return format_html('<img src="{}" style="height:50px; border-radius:4px;" />', obj.capa.url)
        return "-"

@admin.register(Emprestimo)
class EmprestimoAdmin(ModelAdmin):
    list_display = ('livro', 'aluno', 'data_devolucao_prevista', 'status')
    list_filter = ('status', 'data_emprestimo')