###########
# Builder #
###########
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build

# Optional: pass a token to avoid GitHub Markdown API rate limits
ARG MARKDOWN_GITHUB_TOKEN
ENV MARKDOWN_GITHUB_TOKEN=${MARKDOWN_GITHUB_TOKEN}

# Install build-time dependencies to render markdown and build the DB
COPY requirements.txt /build/requirements.txt
RUN pip install --upgrade pip \
    && pip install -r /build/requirements.txt

# Copy the full (filtered) context: .git + markdown + build script
COPY . /build

# Build the SQLite database inside the image
RUN python /build/build_database.py

############
# Runtime  #
############
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install only the runtime dependencies needed to serve the site
COPY requirements.web.txt /app/requirements.web.txt
RUN pip install --upgrade pip \
    && pip install -r /app/requirements.web.txt

# Copy app assets
COPY metadata.yml /app/metadata.yml
COPY templates /app/templates
COPY pages /app/pages

# Copy built database from builder stage
COPY --from=builder /build/tils.db /app/tils.db

EXPOSE 8000

CMD ["datasette", "serve", "/app/tils.db", "--host", "0.0.0.0", "--port", "8000", "-m", "/app/metadata.yml", "--template-dir", "/app/templates"]
