FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x /app/entrypoint.sh

# Carpeta de estaticos con dueno no-root para el volumen compartido
RUN mkdir -p /app/staticfiles && chown 1000:1000 /app/staticfiles

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["sh", "-c", "python manage.py collectstatic --noinput && gunicorn core.wsgi:application --bind 0.0.0.0:8000"]
