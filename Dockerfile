###########
# Builder #
###########
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build

# Install git for GitPython to read commit history
RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

## Clone the public repo so full git history is available during build
ARG REPO_URL=https://github.com/jnellis3/Today-I-Learned.git
ARG GIT_REF=
RUN git clone --recursive ${REPO_URL} /repo \
    && if [ -n "${GIT_REF}" ]; then git -C /repo checkout "${GIT_REF}"; fi \
    && git -C /repo config --global --add safe.directory /repo


# Install build-time dependencies to render markdown and build the DB
RUN pip install --upgrade pip \
    && pip install -r /repo/requirements.txt

# Build the SQLite database inside the image
RUN python /repo/build_database.py

############
# Runtime  #
############
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install only the runtime dependencies needed to serve the site
COPY --from=builder /repo/requirements.web.txt /app/requirements.web.txt
RUN pip install --upgrade pip \
    && pip install -r /app/requirements.web.txt

# Copy app assets
COPY --from=builder /repo/metadata.yml /app/metadata.yml
COPY --from=builder /repo/templates /app/templates
COPY --from=builder /repo/pages /app/pages

# Copy built database from builder stage
COPY --from=builder /repo/tils.db /app/tils.db

EXPOSE 8000

CMD ["datasette", "serve", "/app/tils.db", "--host", "0.0.0.0", "--port", "8000", "-m", "/app/metadata.yml", "--template-dir", "/app/templates"]
