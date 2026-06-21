from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0006_turma_classificacao_indicativa"),
    ]

    operations = [
        migrations.CreateModel(
            name="Resenha",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "aluno",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="resenhas",
                        to="core.aluno",
                    ),
                ),
                (
                    "livro",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="resenhas",
                        to="core.livro",
                    ),
                ),
                ("nota", models.PositiveSmallIntegerField(verbose_name="Nota (1–5)")),
                ("texto", models.TextField(blank=True, verbose_name="Comentário")),
                ("data_criacao", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "Resenha",
                "verbose_name_plural": "Resenhas",
                "ordering": ["-data_criacao"],
            },
        ),
        migrations.AddConstraint(
            model_name="resenha",
            constraint=models.UniqueConstraint(
                fields=["aluno", "livro"],
                name="resenha_aluno_livro_unique",
            ),
        ),
    ]
