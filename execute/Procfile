web: gunicorn --bind 0.0.0.0:$PORT execute.wsgi  # If using Django
worker: celery -A execute worker -l info
beat: celery -A execute beat -l info
