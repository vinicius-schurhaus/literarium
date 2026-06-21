import os
from datetime import timedelta
from io import BytesIO

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import models, transaction
from django.utils import timezone
from PIL import Image


class Genero(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Gênero"
        verbose_name_plural = "Gêneros"
        ordering = ["nome"]


class Autor(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Autor"
        verbose_name_plural = "Autores"
        ordering = ["nome"]


class Turma(models.Model):
    nome = models.CharField(max_length=50, unique=True, verbose_name="Nome")
    exibe_conteudo_explicito = models.BooleanField(
        default=False,
        verbose_name="Exibe conteúdo explícito",
    )

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Turma"
        verbose_name_plural = "Turmas"
        ordering = ["nome"]


class Aluno(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name="aluno_perfil")
    matricula = models.CharField(max_length=50, unique=True)
    turma = models.ForeignKey(
        Turma, on_delete=models.PROTECT, null=True, blank=True, verbose_name="Turma"
    )

    def __str__(self):
        nome = self.usuario.get_full_name() or self.usuario.username
        return f"{nome} ({self.matricula})"

    @property
    def tem_pendencia(self):
        """Aluno tem empréstimo em aberto com prazo vencido (RN002)."""
        return self.emprestimo_set.filter(
            status="ABERTO",
            data_devolucao_prevista__lt=timezone.now().date(),
        ).exists()

    class Meta:
        verbose_name = "Aluno"
        verbose_name_plural = "Alunos"
        ordering = ["usuario__first_name", "usuario__username"]


class Livro(models.Model):
    # Capas são retrato; limitamos o lado maior e recomprimimos como JPEG para
    # não estourar os 512 MB de disco do servidor (PythonAnywhere free).
    CAPA_TAMANHO_MAXIMO = (800, 1000)
    CAPA_QUALIDADE_JPEG = 80

    titulo = models.CharField(max_length=200)
    autor = models.ForeignKey(Autor, on_delete=models.CASCADE)
    genero = models.ForeignKey(Genero, on_delete=models.SET_NULL, null=True, blank=True)
    quantidade = models.PositiveIntegerField(default=1)
    sinopse = models.TextField(blank=True)
    capa = models.ImageField(upload_to="capas/", null=True, blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    conteudo_explicito = models.BooleanField(
        default=False,
        verbose_name="Contém conteúdo explícito",
    )

    def __str__(self):
        return self.titulo

    def clean(self):
        if self.quantidade is not None and self.quantidade < 0:
            raise ValidationError({"quantidade": "A quantidade não pode ser negativa."})

    def save(self, *args, **kwargs):
        self._comprimir_capa()
        super().save(*args, **kwargs)

    def _comprimir_capa(self):
        # `_committed` é False apenas para um arquivo recém-enviado; assim não
        # reprocessamos uma capa já armazenada a cada save() do livro.
        if not self.capa or getattr(self.capa, "_committed", True):
            return
        try:
            self.capa.seek(0)
            with Image.open(self.capa) as imagem:
                imagem = imagem.convert("RGB")
                imagem.thumbnail(self.CAPA_TAMANHO_MAXIMO, Image.Resampling.LANCZOS)
                buffer = BytesIO()
                imagem.save(buffer, format="JPEG", quality=self.CAPA_QUALIDADE_JPEG, optimize=True)
        except OSError:
            # Arquivo ilegível ou não é imagem válida: mantém o upload original.
            return
        nome_base = os.path.splitext(os.path.basename(self.capa.name))[0]
        self.capa.save(f"{nome_base}.jpg", ContentFile(buffer.getvalue()), save=False)

    @property
    def disponivel(self):
        return self.quantidade > 0

    def previsao_retorno(self):
        """Retorna a data de devolução mais próxima entre os empréstimos em aberto."""
        from django.db.models import Min
        resultado = self.emprestimo_set.filter(status="ABERTO").aggregate(
            Min("data_devolucao_prevista")
        )
        return resultado["data_devolucao_prevista__min"]

    class Meta:
        verbose_name = "Livro"
        verbose_name_plural = "Livros"
        ordering = ["-data_cadastro"]
        constraints = [
            models.UniqueConstraint(fields=["titulo", "autor"], name="livro_titulo_autor_unique"),
        ]


class EmprestimoQuerySet(models.QuerySet):
    def abertos(self):
        return self.filter(status="ABERTO")

    def devolvidos(self):
        return self.filter(status="DEVOLVIDO")

    def atrasados(self):
        return self.filter(status="ABERTO", data_devolucao_prevista__lt=timezone.now().date())

    def do_aluno(self, aluno):
        return self.filter(aluno=aluno)

    def do_livro(self, livro):
        return self.filter(livro=livro)

    def no_periodo(self, inicio, fim):
        return self.filter(data_emprestimo__range=(inicio, fim))


class EmprestimoManager(models.Manager):
    def get_queryset(self):
        return EmprestimoQuerySet(self.model, using=self._db)

    def abertos(self):
        return self.get_queryset().abertos()

    def devolvidos(self):
        return self.get_queryset().devolvidos()

    def atrasados(self):
        return self.get_queryset().atrasados()

    def do_aluno(self, aluno):
        return self.get_queryset().do_aluno(aluno)

    def do_livro(self, livro):
        return self.get_queryset().do_livro(livro)

    def no_periodo(self, inicio, fim):
        return self.get_queryset().no_periodo(inicio, fim)


class Emprestimo(models.Model):
    STATUS = [("ABERTO", "Em Aberto"), ("DEVOLVIDO", "Devolvido")]

    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE)
    livro = models.ForeignKey(Livro, on_delete=models.PROTECT)
    data_emprestimo = models.DateField(auto_now_add=True)
    data_devolucao_prevista = models.DateField(blank=True, null=True)
    data_devolucao_real = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default="ABERTO")

    objects = EmprestimoManager()

    def __str__(self):
        return f"{self.livro.titulo} - {self.aluno}"

    @property
    def esta_atrasado(self):
        if self.status != "ABERTO":
            return False
        return self.data_devolucao_prevista is not None and self.data_devolucao_prevista < timezone.now().date()

    def clean(self):
        erros = {}
        if self.data_devolucao_real and self.data_emprestimo:
            if self.data_devolucao_real < self.data_emprestimo:
                erros["data_devolucao_real"] = "A data de devolução real não pode ser anterior à data do empréstimo."
        if self.data_devolucao_prevista and self.data_emprestimo:
            if self.data_devolucao_prevista < self.data_emprestimo:
                erros["data_devolucao_prevista"] = "A data prevista de devolução não pode ser anterior à data do empréstimo."
        if erros:
            raise ValidationError(erros)

    @transaction.atomic
    def save(self, *args, **kwargs):
        if not self.pk:
            livro = Livro.objects.select_for_update().get(pk=self.livro_id)
            if self.status == "ABERTO":
                if livro.quantidade <= 0:
                    raise ValidationError("Não há exemplares disponíveis deste livro.")
                livro.quantidade -= 1
                livro.save()
                self.livro = livro
            if not self.data_devolucao_prevista:
                self.data_devolucao_prevista = timezone.now().date() + timedelta(days=7)
        else:
            antes = Emprestimo.objects.select_related("livro").get(pk=self.pk)
            if antes.livro_id != self.livro_id:
                livro_antigo = Livro.objects.select_for_update().get(pk=antes.livro_id)
                livro_novo = Livro.objects.select_for_update().get(pk=self.livro_id)
                livro_antigo.quantidade += 1
                livro_antigo.save()
                if livro_novo.quantidade <= 0:
                    raise ValidationError("Não há exemplares disponíveis deste livro.")
                livro_novo.quantidade -= 1
                livro_novo.save()
                self.livro = livro_novo
            elif antes.status == "ABERTO" and self.status == "DEVOLVIDO":
                livro = Livro.objects.select_for_update().get(pk=self.livro_id)
                livro.quantidade += 1
                livro.save()
                self.livro = livro
                if not self.data_devolucao_real:
                    self.data_devolucao_real = timezone.now().date()
            elif antes.status == "DEVOLVIDO" and self.status == "ABERTO":
                livro = Livro.objects.select_for_update().get(pk=self.livro_id)
                if livro.quantidade <= 0:
                    raise ValidationError("Não há exemplares disponíveis.")
                livro.quantidade -= 1
                livro.save()
                self.livro = livro

        super().save(*args, **kwargs)

    @transaction.atomic
    def delete(self, *args, **kwargs):
        if self.status == "ABERTO":
            livro = Livro.objects.select_for_update().get(pk=self.livro_id)
            livro.quantidade += 1
            livro.save()
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = "Empréstimo"
        verbose_name_plural = "Empréstimos"
        ordering = ["-data_emprestimo"]


class ReservaQuerySet(models.QuerySet):
    def ativas(self):
        return self.filter(status="ATIVA")

    def do_livro(self, livro):
        return self.filter(livro=livro)

    def do_aluno(self, aluno):
        return self.filter(aluno=aluno)


class ReservaManager(models.Manager):
    def get_queryset(self):
        return ReservaQuerySet(self.model, using=self._db)

    def ativas(self):
        return self.get_queryset().ativas()

    def do_livro(self, livro):
        return self.get_queryset().do_livro(livro)

    def do_aluno(self, aluno):
        return self.get_queryset().do_aluno(aluno)


class Reserva(models.Model):
    STATUS = [
        ("ATIVA", "Ativa"),
        ("ATENDIDA", "Atendida"),
        ("CANCELADA", "Cancelada"),
    ]

    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE)
    livro = models.ForeignKey(Livro, on_delete=models.PROTECT)
    data_reserva = models.DateField(auto_now_add=True)
    data_disponivel_prevista = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default="ATIVA")

    objects = ReservaManager()

    def __str__(self):
        return f"Reserva: {self.livro.titulo} - {self.aluno}"

    class Meta:
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"
        ordering = ["data_reserva"]
        constraints = [
            models.UniqueConstraint(
                fields=["aluno", "livro"],
                condition=models.Q(status="ATIVA"),
                name="reserva_aluno_livro_ativa_unique",
            )
        ]


class Resenha(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name="resenhas")
    livro = models.ForeignKey(Livro, on_delete=models.CASCADE, related_name="resenhas")
    nota = models.PositiveSmallIntegerField(verbose_name="Nota (1–5)")
    texto = models.TextField(blank=True, verbose_name="Comentário")
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Resenha de {self.aluno} — {self.livro.titulo} ({self.nota}★)"

    def clean(self):
        if self.nota is not None and not (1 <= self.nota <= 5):
            raise ValidationError({"nota": "A nota deve ser entre 1 e 5."})

    class Meta:
        verbose_name = "Resenha"
        verbose_name_plural = "Resenhas"
        ordering = ["-data_criacao"]
        constraints = [
            models.UniqueConstraint(fields=["aluno", "livro"], name="resenha_aluno_livro_unique")
        ]
