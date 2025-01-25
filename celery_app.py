import os
from celery_app import Celery
from celery.schedules import crontab
from dotenv import load_dotenv

load_dotenv()
# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "execute.settings")

app = Celery(
    "execute",
    broker=os.getenv("CELERY_BROKER_URL"),
    result_backend=os.getenv("CELERY_RESULT_BACKEND"),
)

# Using a separate configuration object for Celery.
app.config_from_object("django.conf:settings", namespace="CELERY")

app.conf.broker_connection_retry_on_startup = True


# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Optional if you are not using django celery beat
app.conf.beat_schedule = {
    "every-minute": {
        "task": "api.tasks.execute_code_task",
        "schedule": crontab(minute="*"),
    },
    "every-10-seconds": {
        "task": "api.tasks.execute_code_task",
        "schedule": 10.0,
    },
    "daily-task": {
        "task": "api.tasks.execute_code_task",
        "schedule": crontab(minute=0, hour=0),
    },
}


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
