from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from unfold.admin import ModelAdmin
from django.utils.html import format_html
from .models import Autor, Genero, Livro, Aluno, Emprestimo

admin.site.unregister(User)

@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    search_fields = ['username', 'first_name', 'email']

@admin.register(Autor)
class AutorAdmin(ModelAdmin):
    search_fields = ['nome']

@admin.register(Genero)
class GeneroAdmin(ModelAdmin):
    search_fields = ['nome']

@admin.register(Aluno)
class AlunoAdmin(ModelAdmin):
    list_display = ('matricula', 'usuario', 'turma')
    search_fields = ('matricula', 'usuario__first_name', 'usuario__username')
    autocomplete_fields = ['usuario']

@admin.register(Livro)
class LivroAdmin(ModelAdmin):
    list_display = ('titulo', 'autor', 'quantidade', 'ver_capa')
    search_fields = ('titulo', 'autor__nome')
    list_filter = ('genero',)
    autocomplete_fields = ['autor', 'genero']

    def ver_capa(self, obj):
        if obj.capa:
            return format_html('<img src="{}" style="height:50px; border-radius:4px;" />', obj.capa.url)
        return "-"
    ver_capa.short_description = 'Capa'

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Remove a lixeira do campo Gênero
        if 'genero' in form.base_fields:
            form.base_fields['genero'].widget.can_delete_related = False
        return form

@admin.register(Emprestimo)
class EmprestimoAdmin(ModelAdmin):
    list_display = ('livro', 'aluno', 'data_devolucao_prevista', 'status')
    list_filter = ('status', 'data_emprestimo')
    autocomplete_fields = ['livro', 'aluno']

    # --- NOVA PROTEÇÃO AQUI ---
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        # Remove a lixeira do campo Livro
        if 'livro' in form.base_fields:
            form.base_fields['livro'].widget.can_delete_related = False
            
        # Remove a lixeira do campo Aluno
        if 'aluno' in form.base_fields:
            form.base_fields['aluno'].widget.can_delete_related = False
            
        return form