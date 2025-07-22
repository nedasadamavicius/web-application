from celery import shared_task
from .services.spotify_service import SpotifyService

@shared_task
def refresh_spotify_genres():
    service = SpotifyService()
    service.get_genres()  # Will refresh cache
