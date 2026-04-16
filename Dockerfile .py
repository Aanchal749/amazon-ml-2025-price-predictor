# ═══════════════════════════════════════════════
# Multi-stage Dockerfile for ML Price Predictor
# ═══════════════════════════════════════════════

# ──────────────────────────────────────────────
# Stage 1: Base image with dependencies
# ──────────────────────────────────────────────
FROM python:3.10-slim AS base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ──────────────────────────────────────────────
# Stage 2: Training image
# ──────────────────────────────────────────────
FROM base AS training

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY train.py .
COPY dataset/ ./dataset/

# Create directories
RUN mkdir -p features models logs

# Training command (override at runtime)
CMD ["python", "train.py"]

# ──────────────────────────────────────────────
# Stage 3: Inference API image
# ──────────────────────────────────────────────
FROM base AS inference

# Install only inference dependencies (lighter)
COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

# Copy only necessary files
COPY src/multimodal_model.py ./src/
COPY api_inference.py .
COPY models/ ./models/

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run API server
CMD ["uvicorn", "api_inference:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

# ──────────────────────────────────────────────
# Stage 4: Production-ready image (minimal)
# ──────────────────────────────────────────────
FROM python:3.10-alpine AS production

ENV PYTHONUNBUFFERED=1

# Install minimal dependencies
RUN apk add --no-cache libgomp libstdc++ curl

WORKDIR /app

# Copy pre-built artifacts from inference stage
COPY --from=inference /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=inference /app /app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "-m", "uvicorn", "api_inference:app", "--host", "0.0.0.0", "--port", "8000"]