import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pie_global.settings')

app = Celery('pie_global')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
