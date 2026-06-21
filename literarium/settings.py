from pathlib import Path
import dj_database_url
import os

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Carrega variáveis de um arquivo .env, se existir (dev local e PythonAnywhere).
# Em produção o .env é criado manualmente no servidor e NUNCA versionado.
load_dotenv(BASE_DIR / ".env")

import sys
TESTING = "test" in sys.argv or "pytest" in sys.modules

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    if TESTING:
        SECRET_KEY = "django-insecure-test-key-only-for-tests"
    else:
        raise RuntimeError("SECRET_KEY não definida. Configure a variável de ambiente SECRET_KEY.")

DEBUG = os.getenv("DEBUG", "False") == "True"
ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if h.strip()]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "literarium.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "literarium.wsgi.application"

_db_url = os.getenv("DATABASE_URL")
if _db_url:
    DATABASES = {
        "default": dj_database_url.config(default=_db_url, conn_max_age=600)
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "/admin/login/"

# --- REST Framework ---

from datetime import timedelta

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 12,
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    # Desabilitado em testes para não acumular contadores no cache entre requisições.
    "DEFAULT_THROTTLE_RATES": {
        "anon": None if TESTING else "30/min",
        "user": None if TESTING else "1000/hour",
    },
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

CORS_ALLOWED_ORIGINS = [
    h.strip()
    for h in os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:5173").split(",")
    if h.strip()
]
# A autenticação é via Bearer token (Authorization header), não cookies.
# Por isso NÃO habilitamos CORS_ALLOW_CREDENTIALS — reduz a superfície de ataque.

# --- Hardening de produção ---
# Aplicado apenas fora de DEBUG (e nunca em testes, que usam HTTP). Em produção
# (PythonAnywhere) o TLS é encerrado no proxy, que encaminha X-Forwarded-Proto.
if not DEBUG and not TESTING:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

# Origens confiáveis para CSRF (necessário para o /admin atrás de HTTPS).
# Ex.: https://seuapp.onrender.com
CSRF_TRUSTED_ORIGINS = [
    h.strip()
    for h in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",")
    if h.strip()
]

# --- Render ---
# O Render injeta automaticamente o hostname público em RENDER_EXTERNAL_HOSTNAME,
# então não é preciso configurar ALLOWED_HOSTS/CSRF manualmente no painel.
RENDER_HOST = os.getenv("RENDER_EXTERNAL_HOSTNAME")
if RENDER_HOST:
    ALLOWED_HOSTS.append(RENDER_HOST)
    CSRF_TRUSTED_ORIGINS.append(f"https://{RENDER_HOST}")

# Em produção combinada (Django serve o build do React), o WhiteNoise entrega os
# arquivos de frontend/dist na raiz, ao lado do STATIC_ROOT (admin/DRF) em /static/.
# Não adicionamos o dist em STATICFILES_DIRS de propósito: o ManifestStaticFilesStorage
# reescreveria os caminhos do index.html e quebraria a SPA.
_SPA_DIR = BASE_DIR / "frontend" / "dist"
if _SPA_DIR.exists():
    WHITENOISE_ROOT = str(_SPA_DIR)
