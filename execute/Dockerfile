FROM python:3.9-slim-buster

WORKDIR /app

COPY celery_requirements.txt .
RUN pip install --no-cache-dir -r celery_requirements.txt

COPY . .

CMD ["celery", "-A", "celery", "worker", "-l", "info"] #start the worker
#CMD ["celery", "-A", "celery_app", "beat", "-l", "info"] #start the beat