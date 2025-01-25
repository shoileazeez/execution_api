FROM python:3.12-slim


# Set environment variables
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y \
    python3-dev \
    libpq-dev \
    build-essential \
    libffi-dev \
    zlib1g-dev \
    curl \
    gnupg

# Install Node.js and npm (for vm2)
RUN curl -fsSL https://deb.nodesource.com/setup_16.x | bash - && \
    apt-get install -y nodejs

# Install Python dependencies (requirements.txt)


# Install Node.js dependencies (package.json)
COPY package.json .
RUN npm install

# Copy the entire Django project into the container
COPY . .

# Create a non-root user and set it as the owner of the working directory


RUN adduser --disabled-password --gecos '' celeryuser \
    && chown -R celeryuser:celeryuser /app

# Switch to the celeryuser to avoid running as root
USER celeryuser

# Command to run Celery worker
EXPOSE 8000

# CMD to apply migrations, collect static files, and start both Django and Celery
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && celery -A execute.celery_app  worker --loglevel=info & gunicorn execute.wsgi:application --bind 0.0.0.0:$PORT"]
