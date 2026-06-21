from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0008_seed_genero_vestibular"),
    ]

    operations = [
        migrations.AddField(
            model_name="turma",
            name="exibe_conteudo_explicito",
            field=models.BooleanField(default=False, verbose_name="Exibe conteúdo explícito"),
        ),
        migrations.RemoveField(
            model_name="livro",
            name="classificacao_indicativa",
        ),
        migrations.AddField(
            model_name="livro",
            name="conteudo_explicito",
            field=models.BooleanField(default=False, verbose_name="Contém conteúdo explícito"),
        ),
    ]
