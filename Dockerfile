# --- Estágio 1: build do frontend React (Vite) ---
FROM node:20-slim AS frontend

WORKDIR /frontend

# Instala dependências a partir do lockfile (cache eficiente).
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

# Copia o restante do frontend e gera o build de produção em /frontend/dist.
# NÃO definimos VITE_API_URL: o cliente cai no fallback '/api' (mesma origem).
COPY frontend/ ./
RUN npm run build

# --- Estágio 2: runtime Django + Gunicorn ---
FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Traz o build do React do estágio anterior para o Django/WhiteNoise servir.
COPY --from=frontend /frontend/dist ./frontend/dist

RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
