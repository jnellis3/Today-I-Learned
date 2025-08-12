FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps for SQLite features and compilation of some wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl build-essential gcc && \
    rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/requirements.txt

# Copy app assets and database (database should be present in build context)
COPY metadata.yml /app/metadata.yml
COPY templates /app/templates
COPY pages /app/pages
COPY tils.db /app/tils.db

EXPOSE 8000

CMD ["datasette", "serve", "/app/tils.db", "--host", "0.0.0.0", "--port", "8000", "-m", "/app/metadata.yml"]

