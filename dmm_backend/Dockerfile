####
# Production-grade multi-stage image for the Peace Script backend
# Stage 1: build Python wheels so the final image stays slim
####

FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1

WORKDIR /app

# Install OS build deps required for several scientific / crypto packages
RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
	   build-essential \
	   libpq-dev \
	   curl \
	&& rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip \
	&& pip wheel --wheel-dir /wheels -r requirements.txt

####
# Stage 2: runtime image with only the essentials
####

FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	PYTHONPATH=/app

WORKDIR /app

# Install runtime system dependencies (e.g., libpq for pymongo optional compression)
RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
	   libpq5 \
	&& rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./requirements.txt
COPY --from=builder /wheels /wheels

RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt

# Copy application source
COPY . .

# Create non-root user for security
RUN useradd --create-home --uid 1001 appuser \
	&& chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

# Run uvicorn with multiple workers for production throughput
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--app-dir", "."]
