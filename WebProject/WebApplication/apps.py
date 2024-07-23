from django.apps import AppConfig


class WebapplicationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'WebApplication'

    def ready(self):
        from .spotify_api import fetch_and_cache_genres
        fetch_and_cache_genres()