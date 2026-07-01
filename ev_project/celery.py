"""
Celery configuration for VoltStream.

This file sets up Celery so it knows:
- Which Django settings to use
- Where to find tasks (auto-discovers from all installed apps)
"""

import os

from celery import Celery

# Tell Celery which settings file to use
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ev_project.settings")

# Create the Celery app
app = Celery("ev_project")

# Load settings from Django settings file
# All celery settings in settings.py start with CELERY_
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks from all installed Django apps
# This means Celery will look for tasks.py in every app folder
app.autodiscover_tasks()
