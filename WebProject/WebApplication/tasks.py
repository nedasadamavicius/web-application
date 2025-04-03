from celery import shared_task
from .spotify_api import fetch_and_cache_genres

@shared_task
def refresh_spotify_genres():
    fetch_and_cache_genres()