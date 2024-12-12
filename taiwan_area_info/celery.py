from celery import Celery

app = Celery("taiwan_area_info")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
