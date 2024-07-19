from django.db import models

# Create your models here.
class Artist(models.Model):
    name = models.CharField(max_length=255)
    bio = models.TextField()

    def __str__(self):
        return self.name
    