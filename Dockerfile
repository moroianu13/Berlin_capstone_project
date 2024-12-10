# Basis-Image
FROM python:3.10-slim

WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y \
    python3-dev \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN python manage.py collectstatic --clear --noinput


RUN pip install gunicorn

EXPOSE 8000

CMD ["gunicorn",  "--workers", "3", "--bind", "0.0.0.0:8000", "rentfinder.wsgi:application"]
