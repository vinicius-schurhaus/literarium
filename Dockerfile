FROM python:3.10-slim

RUN apt-get update && apt-get install -y libpq-dev gcc gettext

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

CMD ["gunicorn", "literarium.wsgi:application", "--bind", "0.0.0.0:8000"]