from django.db import migrations


GESTOR_PERMISSIONS = [
    ("auth", "user", "add_user"),
    ("auth", "user", "change_user"),
    ("auth", "user", "delete_user"),
    ("auth", "user", "view_user"),
    ("core", "aluno", "add_aluno"),
    ("core", "aluno", "change_aluno"),
    ("core", "aluno", "delete_aluno"),
    ("core", "aluno", "view_aluno"),
]

BIBLIOTECARIO_PERMISSIONS = [
    ("core", "livro", "add_livro"),
    ("core", "livro", "change_livro"),
    ("core", "livro", "delete_livro"),
    ("core", "livro", "view_livro"),
    ("core", "genero", "add_genero"),
    ("core", "genero", "change_genero"),
    ("core", "genero", "delete_genero"),
    ("core", "genero", "view_genero"),
    ("core", "autor", "add_autor"),
    ("core", "autor", "change_autor"),
    ("core", "autor", "delete_autor"),
    ("core", "autor", "view_autor"),
    ("core", "emprestimo", "add_emprestimo"),
    ("core", "emprestimo", "change_emprestimo"),
    ("core", "emprestimo", "delete_emprestimo"),
    ("core", "emprestimo", "view_emprestimo"),
    ("core", "reserva", "add_reserva"),
    ("core", "reserva", "change_reserva"),
    ("core", "reserva", "delete_reserva"),
    ("core", "reserva", "view_reserva"),
    ("core", "aluno", "view_aluno"),
]


def criar_grupos(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    ContentType = apps.get_model("contenttypes", "ContentType")

    def _get_permissions(perm_list):
        perms = []
        for app_label, model, codename in perm_list:
            try:
                ct = ContentType.objects.get(app_label=app_label, model=model)
                perm = Permission.objects.get(content_type=ct, codename=codename)
                perms.append(perm)
            except (ContentType.DoesNotExist, Permission.DoesNotExist):
                pass
        return perms

    gestor, _ = Group.objects.get_or_create(name="Gestor")
    gestor.permissions.set(_get_permissions(GESTOR_PERMISSIONS))

    bibliotecario, _ = Group.objects.get_or_create(name="Bibliotecário")
    bibliotecario.permissions.set(_get_permissions(BIBLIOTECARIO_PERMISSIONS))


def remover_grupos(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name__in=["Gestor", "Bibliotecário"]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_add_reserva_unique_constraints'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(criar_grupos, remover_grupos),
    ]
