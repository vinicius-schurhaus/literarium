from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .models import Aluno, Autor, Emprestimo, Genero, Livro, Reserva, Resenha, Turma


class AutorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Autor
        fields = ["id", "nome"]


class GeneroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genero
        fields = ["id", "nome"]


class TurmaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Turma
        fields = ["id", "nome", "exibe_conteudo_explicito"]


class LivroListSerializer(serializers.ModelSerializer):
    autor = AutorSerializer(read_only=True)
    genero = GeneroSerializer(read_only=True)
    disponivel = serializers.BooleanField(read_only=True)
    capa = serializers.SerializerMethodField()
    total_emprestimos = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Livro
        fields = [
            "id",
            "titulo",
            "autor",
            "genero",
            "conteudo_explicito",
            "disponivel",
            "capa",
            "data_cadastro",
            "total_emprestimos",
        ]

    def get_capa(self, obj):
        if not obj.capa:
            return None
        # URL absoluta para funcionar com o frontend em outro domínio (Netlify).
        # build_absolute_uri usa o host da requisição (o backend), tanto em
        # produção quanto em dev via proxy do Vite.
        request = self.context.get("request")
        if request is not None:
            return request.build_absolute_uri(obj.capa.url)
        return obj.capa.url


class LivroDetailSerializer(LivroListSerializer):
    previsao_retorno = serializers.SerializerMethodField()
    media_notas = serializers.SerializerMethodField()
    total_resenhas = serializers.SerializerMethodField()

    class Meta(LivroListSerializer.Meta):
        fields = LivroListSerializer.Meta.fields + [
            "sinopse",
            "quantidade",
            "previsao_retorno",
            "media_notas",
            "total_resenhas",
        ]

    def get_previsao_retorno(self, obj):
        return obj.previsao_retorno()

    def get_media_notas(self, obj):
        resenhas = obj.resenhas.all()
        if not resenhas.exists():
            return None
        return round(sum(r.nota for r in resenhas) / resenhas.count(), 1)

    def get_total_resenhas(self, obj):
        return obj.resenhas.count()


class LivroWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Livro
        fields = [
            "titulo",
            "autor",
            "genero",
            "quantidade",
            "sinopse",
            "capa",
            "conteudo_explicito",
        ]

    def validate_quantidade(self, value):
        if value < 1:
            raise serializers.ValidationError(
                "Deve haver pelo menos um exemplar disponível no acervo."
            )
        return value


class ResenhaSerializer(serializers.ModelSerializer):
    aluno_nome = serializers.SerializerMethodField()
    is_minha = serializers.SerializerMethodField()

    class Meta:
        model = Resenha
        fields = ["id", "nota", "texto", "data_criacao", "aluno_nome", "is_minha"]

    def get_aluno_nome(self, obj):
        return obj.aluno.usuario.get_full_name() or obj.aluno.usuario.username

    def get_is_minha(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        aluno = getattr(request.user, "aluno_perfil", None)
        return aluno is not None and obj.aluno_id == aluno.pk


class StaffResenhaSerializer(ResenhaSerializer):
    livro = serializers.SerializerMethodField()

    class Meta(ResenhaSerializer.Meta):
        fields = ResenhaSerializer.Meta.fields + ["livro"]

    def get_livro(self, obj):
        return {"id": obj.livro_id, "titulo": obj.livro.titulo}


class ResenhaWriteSerializer(serializers.Serializer):
    nota = serializers.IntegerField(min_value=1, max_value=5)
    texto = serializers.CharField(allow_blank=True, default="")


class EmprestimoSerializer(serializers.ModelSerializer):
    livro = LivroListSerializer(read_only=True)
    aluno_nome = serializers.SerializerMethodField()
    aluno_matricula = serializers.SerializerMethodField()
    esta_atrasado = serializers.BooleanField(read_only=True)

    class Meta:
        model = Emprestimo
        fields = [
            "id",
            "livro",
            "aluno_nome",
            "aluno_matricula",
            "data_emprestimo",
            "data_devolucao_prevista",
            "data_devolucao_real",
            "status",
            "esta_atrasado",
        ]

    def get_aluno_nome(self, obj):
        return obj.aluno.usuario.get_full_name() or obj.aluno.usuario.username

    def get_aluno_matricula(self, obj):
        return obj.aluno.matricula


class ReservaSerializer(serializers.ModelSerializer):
    livro = LivroListSerializer(read_only=True)
    aluno_nome = serializers.SerializerMethodField()

    class Meta:
        model = Reserva
        fields = [
            "id",
            "livro",
            "aluno_nome",
            "data_reserva",
            "data_disponivel_prevista",
            "status",
        ]

    def get_aluno_nome(self, obj):
        return obj.aluno.usuario.get_full_name() or obj.aluno.usuario.username


class AlunoSerializer(serializers.ModelSerializer):
    nome_completo = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    turma = TurmaSerializer(read_only=True)
    tem_pendencia = serializers.BooleanField(read_only=True)

    class Meta:
        model = Aluno
        fields = ["id", "matricula", "turma", "nome_completo", "email", "username", "tem_pendencia"]

    def get_nome_completo(self, obj):
        return obj.usuario.get_full_name() or obj.usuario.username

    def get_email(self, obj):
        return obj.usuario.email

    def get_username(self, obj):
        return obj.usuario.username


class AlunoWriteSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150, default="", allow_blank=True)
    email = serializers.EmailField(default="", allow_blank=True)
    password = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        style={"input_type": "password"},
    )
    matricula = serializers.CharField(max_length=50)
    turma_id = serializers.PrimaryKeyRelatedField(
        queryset=Turma.objects.all(), source="turma", required=False, allow_null=True
    )

    def validate_username(self, value):
        qs = User.objects.filter(username=value)
        aluno_pk = self.context.get("aluno_pk")
        if aluno_pk:
            aluno = Aluno.objects.get(pk=aluno_pk)
            qs = qs.exclude(pk=aluno.usuario_id)
        if qs.exists():
            raise serializers.ValidationError("Este nome de usuário já está em uso.")
        return value

    def validate_matricula(self, value):
        qs = Aluno.objects.filter(matricula=value)
        aluno_pk = self.context.get("aluno_pk")
        if aluno_pk:
            qs = qs.exclude(pk=aluno_pk)
        if qs.exists():
            raise serializers.ValidationError("Esta matrícula já está em uso.")
        return value

    def validate_password(self, value):
        if value:
            try:
                validate_password(value)
            except DjangoValidationError as exc:
                raise serializers.ValidationError(list(exc.messages))
        return value

    def validate(self, attrs):
        aluno_pk = self.context.get("aluno_pk")
        if not aluno_pk and not attrs.get("password"):
            raise serializers.ValidationError({"password": "A senha é obrigatória para novos alunos."})
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    has_aluno_perfil = serializers.SerializerMethodField()
    tem_pendencia = serializers.SerializerMethodField()
    matricula = serializers.SerializerMethodField()
    turma = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_staff",
            "has_aluno_perfil",
            "tem_pendencia",
            "matricula",
            "turma",
        ]

    def get_has_aluno_perfil(self, obj):
        return hasattr(obj, "aluno_perfil")

    def get_tem_pendencia(self, obj):
        aluno = getattr(obj, "aluno_perfil", None)
        return aluno.tem_pendencia if aluno else False

    def get_matricula(self, obj):
        aluno = getattr(obj, "aluno_perfil", None)
        return aluno.matricula if aluno else None

    def get_turma(self, obj):
        aluno = getattr(obj, "aluno_perfil", None)
        if aluno and aluno.turma:
            return TurmaSerializer(aluno.turma).data
        return None
