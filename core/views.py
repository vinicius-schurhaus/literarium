from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Min
from .models import Livro, Genero, Emprestimo, Aluno

def catalogo(request):
    livros = Livro.objects.all().select_related('autor', 'genero')
    generos = Genero.objects.all().order_by('nome')

    q = request.GET.get('q')
    if q:
        livros = livros.filter(
            Q(titulo__icontains=q) | 
            Q(autor__nome__icontains=q)
        )

    genero_id = request.GET.get('genero')
    if genero_id:
        livros = livros.filter(genero_id=genero_id)

    livros = livros.order_by('-data_cadastro')

    context = {
        'livros': livros,
        'generos': generos,
        'query_search': q,
        'genero_selecionado': genero_id,
    }
    return render(request, 'core/catalogo.html', context)

@login_required
def livro_detalhes(request, livro_id):
    livro = get_object_or_404(Livro.objects.select_related('autor', 'genero'), id=livro_id)

    previsao_retorno = None
    if livro.quantidade == 0:
        proximo_emprestimo = Emprestimo.objects.filter(livro=livro, status='ABERTO').aggregate(Min('data_devolucao_prevista'))
        previsao_retorno = proximo_emprestimo['data_devolucao_prevista__min']

    context = {
        'livro': livro,
        'previsao_retorno': previsao_retorno
    }
    return render(request, 'core/livro_detalhes.html', context)

@login_required
def meus_emprestimos(request):
    try:
        aluno = request.user.aluno_perfil
        emprestimos = Emprestimo.objects.filter(aluno=aluno).select_related('livro', 'livro__autor').order_by('-data_emprestimo')
    except Aluno.DoesNotExist:
        emprestimos = []

    context = {
        'emprestimos': emprestimos,
    }
    return render(request, 'core/meus_emprestimos.html', context)