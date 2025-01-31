FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Copy requirements.txt FIRST
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install system dependencies (if needed for your Python packages)
RUN apt-get update && apt-get install -y \
    python3-dev \
    libpq-dev \
    build-essential \
    libffi-dev \
    zlib1g-dev \
    curl \
    gnupg

# Create the utils directory (if it doesn't exist)
RUN mkdir -p utils

# Copy package.json and executor.js (or the entire utils d
COPY package.json .
COPY utils/ /app/utils/ 

# Install Node.js and npm (for isolated-vm)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs

# Install Node.js dependencies (important: AFTER copying package.json)
RUN npm install

# Copy the rest of your Django project (AFTER installing npm dependencies)
COPY . .

# Create a non-root user and set it as the owner of the working directory
RUN adduser --disabled-password --gecos '' celeryuser \
    && chown -R celeryuser:celeryuser /app

# Switch to the celeryuser to avoid running as root
USER celeryuser

# Expose port
EXPOSE 8000

# Command to run Celery worker and Gunicorn
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && celery -A execute.celery_app worker --loglevel=info & gunicorn execute.wsgi:application --bind 0.0.0.0:$PORT"]