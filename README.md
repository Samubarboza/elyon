# ELYON

ELYON is a business management system for small and medium companies.

The goal is to help companies manage users, customers, products, stock, sales, purchases, cash and reports in one place.

ELYON follows a defined plan for its modules, architecture and business rules.

This repository contains the codebase and the basic setup for that plan.

## Stack

- Django
- Django Templates
- HTMX
- Django REST Framework
- PostgreSQL
- Docker
- Nginx
- Gunicorn
- Celery
- Redis

## Requirements

You need:

- Git
- Docker
- Docker Compose

## Environment Variables

Create a `.env` file in the project root.

Use `.env.example` as a guide and add all required values.

## Initial Setup

Clone the project:

```bash
git clone <repository-url>
cd elyon
```

Build the containers:

```bash
docker compose build
```

Start the project:

```bash
docker compose up
```

Create migrations:

```bash
docker compose run --rm web python manage.py makemigrations
```

Run migrations:

```bash
docker compose run --rm web python manage.py migrate
```

Create a superuser:

```bash
docker compose run --rm web python manage.py createsuperuser
```

## Project Status

This project is in development.
