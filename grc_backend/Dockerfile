# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Install necessary system packages for mysqlclient and tesseract (for OCR)
RUN apt-get update && apt-get install -y \
    pkg-config \
    libmariadb-dev \
    build-essential \
    tesseract-ocr \
    tesseract-ocr-eng \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create a non-root user to run the application
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app && \
    chown -R appuser:appuser /app

# Set the working directory in the container
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY --chown=appuser:appuser . /app

# Create necessary directories for file uploads and set permissions
RUN mkdir -p /app/MEDIA_ROOT /app/TEMP_MEDIA_ROOT /app/Reports \
    /app/secure_uploads /app/temp_uploads /app/quarantine && \
    chown -R appuser:appuser /app/MEDIA_ROOT /app/TEMP_MEDIA_ROOT \
    /app/Reports /app/secure_uploads /app/temp_uploads /app/quarantine

# Collect static files (uncomment if needed for production)
# RUN python manage.py collectstatic --noinput

# Switch to non-root user
USER appuser

# Expose port 8000 for the application to listen on
EXPOSE 8000

# Set environment variables for Django
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=backend.settings

# Health check - checks if the application is responding
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Run the Django server with gunicorn
CMD ["gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-"]
