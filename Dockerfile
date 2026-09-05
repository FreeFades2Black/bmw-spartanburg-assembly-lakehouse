# Multi-stage Dockerfile for BMW Plant Spartanburg Multi-Powertrain Assembly Lakehouse
# Stage 1: Pipeline Builder & AIQX Quarantine Engine
FROM python:3.11-slim AS builder

WORKDIR /app

# Install dependencies
COPY requirements.txt* ./
RUN pip install --no-cache-dir pydantic pytest

# Copy source code and test suite
COPY src/ ./src/
COPY tests/ ./tests/
COPY pytest.ini ./

# Execute full Medallion pipeline (Bronze -> Silver -> Gold) and build dashboard
RUN python src/processing/delta_lakehouse.py && \
    python src/visualization/build_dashboard.py && \
    mkdir -p /app/docs && \
    cp -r data/gold/* /app/docs/ || true

# Stage 2: Ultra-Lightweight Production Runtime
FROM python:3.11-alpine AS runtime

WORKDIR /app

# Non-root security user (CIS / Manufacturing standard)
RUN addgroup -g 10003 bmwgroup && \
    adduser -u 10003 -G bmwgroup -s /bin/sh -D bmwgroup

# Copy compiled dashboard and gold artifacts from builder
COPY --from=builder --chown=bmwgroup:bmwgroup /app/docs /app/docs
COPY --from=builder --chown=bmwgroup:bmwgroup /app/data/gold /app/data/gold

USER 10003:10003

EXPOSE 8830

# Serve dashboard on port 8830
CMD ["python", "-m", "http.server", "8830", "--directory", "/app/docs"]
