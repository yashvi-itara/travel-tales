# ==== Base Stage ====
FROM python:3.11-slim AS base
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install tini for proper init process handling (zombie reaping & signal forwarding)
RUN apt-get update && apt-get install -y --no-install-recommends tini \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ==== Builder Stage ====
FROM base AS builder
# Install build dependencies if needed (for C extensions)
RUN apt-get update && apt-get install -y --no-install-recommends gcc python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# ==== Final Stage ====
FROM base AS final

# Copy wheels from builder and install them
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache /wheels/* \
    && rm -rf /wheels

# Create an app user for security instead of running as root
RUN useradd -m appuser \
    # Create necessary directories
    && mkdir -p /app/app/static/uploads /app/data \
    # Give ownership to appuser
    && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Copy the rest of the application code
COPY --chown=appuser:appuser . .

# Expose the port the app runs on
EXPOSE 5000

# Use tini as the entrypoint for proper graceful shutdown
ENTRYPOINT ["/usr/bin/tini", "--"]

# Production command using gunicorn + gevent
CMD ["gunicorn", "-w", "4", "-k", "gevent", "-b", "0.0.0.0:5000", "--access-logfile", "-", "--error-logfile", "-", "run:app"]
