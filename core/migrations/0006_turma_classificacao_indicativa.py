from django.db import migrations, models
import django.db.models.deletion


def criar_turmas_e_migrar(apps, schema_editor):
    Aluno = apps.get_model("core", "Aluno")
    Turma = apps.get_model("core", "Turma")

    turmas_strings = (
        Aluno.objects.exclude(turma_str__isnull=True)
        .exclude(turma_str="")
        .values_list("turma_str", flat=True)
        .distinct()
    )

    turma_map = {}
    for nome in turmas_strings:
        turma_obj, _ = Turma.objects.get_or_create(nome=nome)
        turma_map[nome] = turma_obj.pk

    for aluno in Aluno.objects.all():
        if aluno.turma_str and aluno.turma_str in turma_map:
            aluno.turma_id = turma_map[aluno.turma_str]
            aluno.save(update_fields=["turma_id"])


def reverter_turmas(apps, schema_editor):
    Aluno = apps.get_model("core", "Aluno")
    for aluno in Aluno.objects.select_related("turma").all():
        if aluno.turma:
            aluno.turma_str = aluno.turma.nome
            aluno.save(update_fields=["turma_str"])


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0005_create_groups_gestor_bibliotecario"),
    ]

    operations = [
        # 1. Criar model Turma
        migrations.CreateModel(
            name="Turma",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nome", models.CharField(max_length=50, unique=True, verbose_name="Nome")),
            ],
            options={
                "verbose_name": "Turma",
                "verbose_name_plural": "Turmas",
                "ordering": ["nome"],
            },
        ),

        # 2. Renomear coluna turma → turma_str (preservar dados)
        migrations.RenameField(
            model_name="aluno",
            old_name="turma",
            new_name="turma_str",
        ),

        # 3. Adicionar FK turma_id (nullable inicialmente)
        migrations.AddField(
            model_name="aluno",
            name="turma",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="core.turma",
                verbose_name="Turma",
            ),
        ),

        # 4. Migrar dados: criar objetos Turma e setar turma_id
        migrations.RunPython(criar_turmas_e_migrar, reverter_turmas),

        # 5. Remover coluna turma_str antiga
        migrations.RemoveField(
            model_name="aluno",
            name="turma_str",
        ),

        # 6. Adicionar classificacao_indicativa em Livro
        migrations.AddField(
            model_name="livro",
            name="classificacao_indicativa",
            field=models.CharField(
                choices=[
                    ("L", "Livre"),
                    ("10", "+10"),
                    ("12", "+12"),
                    ("14", "+14"),
                    ("16", "+16"),
                    ("18", "+18"),
                ],
                default="L",
                max_length=3,
                verbose_name="Classificação indicativa",
            ),
        ),
    ]
