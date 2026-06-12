# ALCHEMY - Temporal Content Transmuter
# Multi-stage lightweight Docker build (CPU-constrained deployment)

# ---- Stage 1: Base ----
FROM python:3.12-slim AS base

WORKDIR /app

# Install system dependencies (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- Stage 2: API Server ----
FROM base AS api

COPY . .

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

# ---- Stage 3: Pipeline Runner (one-shot processing) ----
FROM base AS pipeline

COPY . .

ENTRYPOINT ["python", "-m", "src.pipeline.orchestrator"]
