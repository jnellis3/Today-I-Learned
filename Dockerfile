FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install only the runtime dependencies needed to serve the site
COPY requirements.web.txt /app/requirements.web.txt
RUN pip install --upgrade pip \
    && pip install -r /app/requirements.web.txt

# Copy app assets and database (database should be present in build context)
COPY metadata.yml /app/metadata.yml
COPY templates /app/templates
COPY pages /app/pages
COPY tils.db /app/tils.db

EXPOSE 8000

CMD ["datasette", "serve", "/app/tils.db", "--host", "0.0.0.0", "--port", "8000", "-m", "/app/metadata.yml", "--template-dir", "/app/templates"]
