from django.db import migrations


def criar_genero_vestibular(apps, schema_editor):
    Genero = apps.get_model("core", "Genero")
    Genero.objects.get_or_create(nome="Vestibular")


def remover_genero_vestibular(apps, schema_editor):
    Genero = apps.get_model("core", "Genero")
    Genero.objects.filter(nome="Vestibular").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0007_resenha"),
    ]

    operations = [
        migrations.RunPython(criar_genero_vestibular, remover_genero_vestibular),
    ]
