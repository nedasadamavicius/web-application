from django.db import models

# Create your models here.
class Artist(models.Model):
    spotify_id = models.CharField(max_length=50, unique=True) # A unique identifier for the artist from Spotify.
    image_url = models.URLField(null=True, blank=True) # The URL of the artist's image.
    name = models.CharField(max_length=255) # The name of the artist.
    popularity = models.IntegerField() # The popularity score of the artist.

    def __str__(self):
        return self.name
