import os
import shutil

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand

from core.models import Livro

FIXTURE = os.path.join(settings.BASE_DIR, "seed", "initial_data.json")
SEED_MEDIA = os.path.join(settings.BASE_DIR, "seed_media")


class Command(BaseCommand):
    help = (
        "Seed idempotente para demonstração: carrega o catálogo inicial, copia as "
        "capas versionadas para o MEDIA_ROOT e garante um superusuário a partir das "
        "variáveis de ambiente DJANGO_SUPERUSER_*."
    )

    def handle(self, *args, **options):
        self._seed_catalog()
        self._copy_media()
        self._ensure_superuser()

    def _seed_catalog(self):
        if Livro.objects.exists():
            self.stdout.write("Catálogo já populado — pulando loaddata.")
            return
        if not os.path.exists(FIXTURE):
            self.stdout.write(self.style.WARNING(f"Fixture não encontrada: {FIXTURE}"))
            return
        call_command("loaddata", FIXTURE)
        self.stdout.write(self.style.SUCCESS("Catálogo inicial carregado."))

    def _copy_media(self):
        if not os.path.isdir(SEED_MEDIA):
            return
        copied = 0
        for root, _dirs, files in os.walk(SEED_MEDIA):
            rel = os.path.relpath(root, SEED_MEDIA)
            dst_dir = os.path.join(settings.MEDIA_ROOT, "" if rel == "." else rel)
            os.makedirs(dst_dir, exist_ok=True)
            for name in files:
                dst = os.path.join(dst_dir, name)
                if not os.path.exists(dst):
                    shutil.copy2(os.path.join(root, name), dst)
                    copied += 1
        self.stdout.write(f"Capas de seed copiadas: {copied} arquivo(s) novo(s).")

    def _ensure_superuser(self):
        username = os.getenv("DJANGO_SUPERUSER_USERNAME")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD")
        email = os.getenv("DJANGO_SUPERUSER_EMAIL", "")
        if not username or not password:
            self.stdout.write("DJANGO_SUPERUSER_* não definidos — superusuário não criado.")
            return
        User = get_user_model()
        if User.objects.filter(username=username).exists():
            self.stdout.write(f"Superusuário '{username}' já existe.")
            return
        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f"Superusuário '{username}' criado."))
