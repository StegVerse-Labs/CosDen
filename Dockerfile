# Simple production-ish Dockerfile for CosDenOS API

FROM python:3.11-slim

# Prevent Python from writing .pyc files & enable flush
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System deps (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

# Copy project metadata and install
COPY pyproject.toml /app/

# Install project + runtime deps
RUN pip install --upgrade pip \
 && pip install "fastapi>=0.115.0" "uvicorn[standard]>=0.30.0" "pydantic>=2.7.0" \
 && pip install -e .

# Copy source
COPY src /app/src

# Expose port
EXPOSE 8000

# Default command: run FastAPI app
CMD ["uvicorn", "CosDenOS.api:app", "--host", "0.0.0.0", "--port", "8000"]
