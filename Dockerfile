FROM python:3.9-slim-buster

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Install dependencies
COPY celery_requirements.txt .
RUN pip install --no-cache-dir -r celery_requirements.txt

# Copy the entire project into the container
COPY . .

# Create a non-root user and set it as the owner of the working directory
RUN adduser --disabled-password --gecos '' celeryuser && \
    chown -R celeryuser:celeryuser /app

# Switch to the celeryuser to avoid running as root
USER celeryuser

# Command to run Celery worker
CMD ["celery", "-A", "celery", "worker", "--loglevel=info", "--uid=celeryuser"]
