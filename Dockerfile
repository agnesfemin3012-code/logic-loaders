# ==============================================================================
# SmartInfra AI - Production Dockerfile
# ==============================================================================

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for geospatial libraries & C extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libgeos-dev \
    gdal-bin \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY backend/app /app/app
COPY backend/alembic /app/alembic
COPY backend/alembic.ini /app/alembic.ini
COPY backend/scripts /app/scripts
COPY .env.example /app/.env

EXPOSE 8000

# Run uvicorn server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
