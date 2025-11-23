#!/bin/sh

echo "Esperando o banco subir..."
sleep 5

echo "Rodando migrations..."
python manage.py migrate --noinput

echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

echo "Iniciando o servidor..."
gunicorn literarium.wsgi:application --bind 0.0.0.0:8000
