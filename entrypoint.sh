#!/bin/sh
set -e

echo "Rodando migrations..."
python manage.py migrate --noinput

echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

echo "Semeando dados de demonstração (idempotente)..."
python manage.py seed_demo

echo "Iniciando o servidor..."
exec gunicorn literarium.wsgi:application --bind 0.0.0.0:"${PORT:-8000}" --workers 2
