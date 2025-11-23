from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class Genero(models.Model):
    nome = models.CharField(max_length=100)
    
    def __str__(self): 
        return self.nome

    class Meta:
        verbose_name = "Gênero"
        verbose_name_plural = "Gêneros"

class Autor(models.Model):
    nome = models.CharField(max_length=100)
    
    def __str__(self): 
        return self.nome

    class Meta:
        verbose_name = "Autor"
        verbose_name_plural = "Autores"

class Aluno(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='aluno_perfil')
    matricula = models.CharField(max_length=50, unique=True)
    turma = models.CharField(max_length=50)
    
    def __str__(self): 
        # Retorna o Nome. Se não tiver nome cadastrado, retorna o Login (username)
        return self.usuario.first_name if self.usuario.first_name else self.usuario.username

    class Meta:
        verbose_name = "Aluno"
        verbose_name_plural = "Alunos"

class Livro(models.Model):
    titulo = models.CharField(max_length=200)
    autor = models.ForeignKey(Autor, on_delete=models.CASCADE)
    genero = models.ForeignKey(Genero, on_delete=models.SET_NULL, null=True)
    quantidade = models.PositiveIntegerField(default=1)
    sinopse = models.TextField(blank=True, null=True, verbose_name="Sinopse")
    capa = models.ImageField(upload_to='capas/', null=True, blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    
    def __str__(self): 
        return self.titulo

    class Meta:
        verbose_name = "Livro"
        verbose_name_plural = "Livros"

class Emprestimo(models.Model):
    STATUS = [('ABERTO', 'Em Aberto'), ('DEVOLVIDO', 'Devolvido')]
    
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE)
    livro = models.ForeignKey(Livro, on_delete=models.PROTECT)
    data_emprestimo = models.DateField(auto_now_add=True)
    data_devolucao_prevista = models.DateField(blank=True, null=True)
    data_devolucao_real = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default='ABERTO')

    # --- AQUI ESTÁ A CORREÇÃO ---
    def __str__(self):
        # Exibe: "Nome do Livro - Nome do Aluno"
        return f"{self.livro.titulo} - {self.aluno}"

    def save(self, *args, **kwargs):
        if not self.data_devolucao_prevista:
            self.data_devolucao_prevista = timezone.now().date() + timedelta(days=7)
        
        if not self.pk:
            if self.livro.quantidade > 0:
                self.livro.quantidade -= 1
                self.livro.save()
        else:
            emprestimo_antigo = Emprestimo.objects.get(pk=self.pk)
            
            if emprestimo_antigo.status == 'ABERTO' and self.status == 'DEVOLVIDO':
                self.livro.quantidade += 1
                self.livro.save()
                
                if not self.data_devolucao_real:
                    self.data_devolucao_real = timezone.now().date()

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Empréstimo"
        verbose_name_plural = "Empréstimos"