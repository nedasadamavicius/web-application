from django.db import models

# Create your models here.
class Artist(models.Model):
    name = models.CharField(max_length=255)
    bio = models.TextField()
    album_image = models.BinaryField(null=True)
    playlist_id = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name
