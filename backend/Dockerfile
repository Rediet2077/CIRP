# CIRP Backend - Django REST API
# Dockerfile

FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set work directory
WORKDIR /app

# Install system dependencies for GeoDjango (GDAL, GEOS, PROJ)
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    binutils \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Set GDAL environment variable
ENV GDAL_LIBRARY_PATH=/usr/lib/libgdal.so

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy project files
COPY . .

# Create directories for static and media files
RUN mkdir -p staticfiles media

# Expose port
EXPOSE 8000

# Run migrations and start server (overridden by docker-compose)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
