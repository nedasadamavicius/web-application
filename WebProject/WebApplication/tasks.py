from celery import shared_task
from .services.spotify_service import SpotifyService

@shared_task
def refresh_client_token():
    service = SpotifyService()
    service.client.authenticate_client()
