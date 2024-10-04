from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

# Установка настроек Django для Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Создание экземпляра Celery
app = Celery('fashion_store')

# Загрузка конфигурации из settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматический поиск задач в приложениях
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

