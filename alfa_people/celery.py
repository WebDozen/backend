import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alfa_people.settings")
app = Celery("alfa_people", include=["api.tasks"])
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
