from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_livro_sinopse'),
    ]

    operations = [
        # Genero: unique + ordering
        migrations.AlterField(
            model_name='genero',
            name='nome',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterModelOptions(
            name='genero',
            options={'ordering': ['nome'], 'verbose_name': 'Gênero', 'verbose_name_plural': 'Gêneros'},
        ),

        # Autor: unique + ordering
        migrations.AlterField(
            model_name='autor',
            name='nome',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterModelOptions(
            name='autor',
            options={'ordering': ['nome'], 'verbose_name': 'Autor', 'verbose_name_plural': 'Autores'},
        ),

        # Aluno: ordering
        migrations.AlterModelOptions(
            name='aluno',
            options={
                'ordering': ['usuario__first_name', 'usuario__username'],
                'verbose_name': 'Aluno',
                'verbose_name_plural': 'Alunos',
            },
        ),

        # Livro: sinopse sem null, UniqueConstraint titulo+autor, ordering
        migrations.AlterField(
            model_name='livro',
            name='sinopse',
            field=models.TextField(blank=True),
        ),
        migrations.AlterModelOptions(
            name='livro',
            options={'ordering': ['-data_cadastro'], 'verbose_name': 'Livro', 'verbose_name_plural': 'Livros'},
        ),
        migrations.AddConstraint(
            model_name='livro',
            constraint=models.UniqueConstraint(fields=['titulo', 'autor'], name='livro_titulo_autor_unique'),
        ),

        # Emprestimo: ordering
        migrations.AlterModelOptions(
            name='emprestimo',
            options={'ordering': ['-data_emprestimo'], 'verbose_name': 'Empréstimo', 'verbose_name_plural': 'Empréstimos'},
        ),

        # Reserva: new model
        migrations.CreateModel(
            name='Reserva',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_reserva', models.DateField(auto_now_add=True)),
                ('data_disponivel_prevista', models.DateField(blank=True, null=True)),
                ('status', models.CharField(
                    choices=[('ATIVA', 'Ativa'), ('ATENDIDA', 'Atendida'), ('CANCELADA', 'Cancelada')],
                    default='ATIVA',
                    max_length=20,
                )),
                ('aluno', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.aluno')),
                ('livro', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.livro')),
            ],
            options={
                'verbose_name': 'Reserva',
                'verbose_name_plural': 'Reservas',
                'ordering': ['data_reserva'],
            },
        ),
        migrations.AddConstraint(
            model_name='reserva',
            constraint=models.UniqueConstraint(
                condition=models.Q(status='ATIVA'),
                fields=['aluno', 'livro'],
                name='reserva_aluno_livro_ativa_unique',
            ),
        ),
    ]
