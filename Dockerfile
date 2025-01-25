FROM python:3.9-slim-buster

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirement.txt

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
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && celery -A execute worker --loglevel=info & gunicorn execute.wsgi:application --bind 0.0.0.0:$PORT"]
