from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class Genero(models.Model):
    nome = models.CharField(max_length=100)
    def __str__(self): return self.nome

class Autor(models.Model):
    nome = models.CharField(max_length=100)
    def __str__(self): return self.nome

class Aluno(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='aluno_perfil')
    matricula = models.CharField(max_length=50, unique=True)
    turma = models.CharField(max_length=50)
    def __str__(self): return f"{self.usuario.first_name}"

class Livro(models.Model):
    titulo = models.CharField(max_length=200)
    autor = models.ForeignKey(Autor, on_delete=models.CASCADE)
    genero = models.ForeignKey(Genero, on_delete=models.SET_NULL, null=True)
    quantidade = models.PositiveIntegerField(default=1)
    # Aqui usamos ImageField. O Django salvará no MinIO automaticamente.
    capa = models.ImageField(upload_to='capas/', null=True, blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.titulo

class Emprestimo(models.Model):
    STATUS = [('ABERTO', 'Em Aberto'), ('DEVOLVIDO', 'Devolvido')]
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE)
    livro = models.ForeignKey(Livro, on_delete=models.PROTECT)
    data_emprestimo = models.DateField(auto_now_add=True)
    data_devolucao_prevista = models.DateField(blank=True, null=True)
    data_devolucao_real = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default='ABERTO')

    def save(self, *args, **kwargs):
        if not self.data_devolucao_prevista:
            self.data_devolucao_prevista = timezone.now().date() + timedelta(days=7)
        if not self.pk and self.livro.quantidade > 0:
            self.livro.quantidade -= 1
            self.livro.save()
        super().save(*args, **kwargs)