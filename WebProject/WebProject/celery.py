# for automatic re-caching of genres
import os
import environ
from celery import Celery
from pathlib import Path

# Set base directory and load environment variables
BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
env_file = BASE_DIR / ".env"
if env_file.exists():
    environ.Env.read_env(str(env_file))

# Set default Django settings module for Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WebProject.settings')

# Initialize Celery app
app = Celery('WebProject')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
